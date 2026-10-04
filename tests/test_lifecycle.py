import subprocess
import sys
import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from utils.paths import config_dir, resource_path, resource_root
from utils.config import ConfigManager
from utils.runner import DNSRunner, find_spoof_dpi
from utils.startup import startup_path, set_enabled


class FakeProcess:
    def __init__(self, exited=False, timeout=False):
        self.returncode = 0 if exited else None
        self.timeout = timeout
        self.events = []
        self.stdin = Mock()
        self.stdout = Mock()
        self.stderr = Mock()

    def poll(self):
        return self.returncode

    def terminate(self):
        self.events.append("terminate")

    def kill(self):
        self.events.append("kill")
        self.returncode = -9

    def wait(self, timeout=None):
        self.events.append("wait")
        if self.timeout:
            self.timeout = False
            raise subprocess.TimeoutExpired("engine", timeout)
        self.returncode = 0 if self.returncode is None else self.returncode
        return self.returncode


class RunnerStopTests(unittest.TestCase):
    def runner(self, process):
        with patch("utils.runner.atexit.register"):
            runner = DNSRunner()
        runner.process = process
        return runner

    def test_graceful_terminate_reaps_and_closes_resources(self):
        process = FakeProcess()
        runner = self.runner(process)
        output_thread = Mock()
        output_thread.is_alive.return_value = False
        runner.output_thread = output_thread
        runner.stop()
        self.assertEqual(process.events, ["terminate", "wait"])
        for pipe in (process.stdin, process.stdout, process.stderr):
            pipe.close.assert_called_once()
        self.assertIsNone(runner.process)
        output_thread.join.assert_called_once_with(timeout=3)
        runner.stop()
        self.assertEqual(process.events, ["terminate", "wait"])

    def test_timeout_kills_then_waits_again(self):
        process = FakeProcess(timeout=True)
        runner = self.runner(process)
        runner.stop()
        self.assertEqual(process.events, ["terminate", "wait", "kill", "wait"])
        self.assertIsNone(runner.process)

    def test_already_exited_is_reaped_without_terminate(self):
        process = FakeProcess(exited=True)
        runner = self.runner(process)
        runner.stop()
        self.assertEqual(process.events, ["wait"])
        self.assertIsNone(runner.process)

    def test_stop_without_process_is_repeatable(self):
        runner = self.runner(None)
        runner.stop()
        runner.stop()
        self.assertIsNone(runner.process)

    def test_job_handle_is_closed_once_without_process(self):
        runner = self.runner(None)
        runner.job_handle = 123
        close_handle = Mock(return_value=1)
        fake_windll = SimpleNamespace(kernel32=SimpleNamespace(CloseHandle=close_handle))
        with patch("utils.runner.ctypes.windll", fake_windll, create=True):
            runner.stop()
            runner.stop()
        close_handle.assert_called_once_with(123)
        self.assertIsNone(runner.job_handle)

    def test_broken_stream_does_not_skip_other_cleanup(self):
        process = FakeProcess()
        process.stdin.close.side_effect = OSError("already closed")
        runner = self.runner(process)
        with self.assertLogs("utils.runner", level="WARNING"):
            runner.stop()
        process.stdout.close.assert_called_once()
        process.stderr.close.assert_called_once()
        self.assertIsNone(runner.process)

    def test_terminate_error_still_waits_and_reaps(self):
        process = FakeProcess()
        process.terminate = Mock(side_effect=ProcessLookupError())
        runner = self.runner(process)
        runner.stop()
        self.assertEqual(process.events, ["wait"])
        self.assertIsNone(runner.process)

    def test_second_wait_is_bounded_and_keeps_unreaped_process(self):
        process = FakeProcess()
        process.wait = Mock(side_effect=subprocess.TimeoutExpired("engine", 3))
        runner = self.runner(process)
        with self.assertLogs("utils.runner", level="WARNING"):
            runner.stop()
        self.assertEqual(process.wait.call_count, 3)
        self.assertTrue(all(call.kwargs == {"timeout": 3} for call in process.wait.call_args_list))
        self.assertIs(runner.process, process)

    def test_explicit_close_unregisters_atexit_fallback(self):
        process = FakeProcess()
        runner = self.runner(process)
        with patch("utils.runner.atexit.unregister") as unregister:
            runner.close()
        unregister.assert_called_once_with(runner.stop)
        self.assertIsNone(runner.process)

    def test_unreaped_process_keeps_atexit_fallback(self):
        process = FakeProcess()
        process.wait = Mock(side_effect=subprocess.TimeoutExpired("engine", 3))
        runner = self.runner(process)
        with patch("utils.runner.atexit.unregister") as unregister, \
             self.assertLogs("utils.runner", level="WARNING"):
            runner.close()
        unregister.assert_not_called()
        self.assertIs(runner.process, process)


class PlatformPathsTests(unittest.TestCase):
    def test_config_directories(self):
        home = Path("/home/user")
        self.assertEqual(config_dir("linux", {}, home), home / ".config/goodbyedpi-turkey")
        self.assertEqual(config_dir("linux", {"XDG_CONFIG_HOME": "/tmp/cfg"}, home),
                         Path("/tmp/cfg/goodbyedpi-turkey"))
        self.assertEqual(config_dir("win32", {"APPDATA": "C:/Users/u/AppData/Roaming"}, home),
                         Path("C:/Users/u/AppData/Roaming/GoodbyeDPI-Turkey"))

    def test_autostart_platform_selection(self):
        home = Path("/home/user")
        self.assertEqual(startup_path("linux", {}, home),
                         home / ".config/autostart/goodbyedpi-turkey.desktop")
        self.assertEqual(startup_path("win32", {"APPDATA": "C:/Users/u/AppData/Roaming"}, home),
                         Path("C:/Users/u/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/GoodbyeDPI-Turkey GUI.lnk"))

    def test_source_and_frozen_resources(self):
        with patch.object(sys, "frozen", False, create=True):
            self.assertTrue(resource_path("assets", "icon.png").is_file())
        with patch.object(sys, "frozen", True, create=True), patch.object(
            sys, "_MEIPASS", "/tmp/frozen-bundle", create=True
        ):
            self.assertEqual(resource_root(), Path("/tmp/frozen-bundle"))
            self.assertEqual(resource_path("bin", "x86_64", "goodbyedpi.exe"),
                             Path("/tmp/frozen-bundle/bin/x86_64/goodbyedpi.exe"))

    def test_config_is_written_below_user_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            settings = ConfigManager(Path(directory) / "settings")
            settings.save_config("dns_provider", "Cloudflare")
            self.assertEqual(ConfigManager(Path(directory) / "settings").get("dns_provider"), "Cloudflare")

    def test_linux_autostart_can_be_enabled_and_removed(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(sys, "platform", "linux"), \
             patch.dict("os.environ", {"XDG_CONFIG_HOME": directory}):
            set_enabled(True)
            entry = Path(directory) / "autostart/goodbyedpi-turkey.desktop"
            self.assertIn("--minimized", entry.read_text())
            set_enabled(False)
            self.assertFalse(entry.exists())

    def test_spoofdpi_is_found_in_user_install_location(self):
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / ".spoof-dpi/bin/spoof-dpi"
            binary.parent.mkdir(parents=True)
            binary.touch(mode=0o755)
            with patch("utils.runner.shutil.which", return_value=None), \
                 patch("utils.runner.Path.home", return_value=Path(directory)):
                self.assertEqual(find_spoof_dpi(), str(binary))



if __name__ == "__main__":
    unittest.main()
