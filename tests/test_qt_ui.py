"""Qt UI behavior and thread boundary tests, runnable without a display server."""
import os
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtCore import QThread
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QSystemTrayIcon
from shiboken6 import delete

from app_controller import AppController
from app_state import Phase
from ui.theme import resolve_theme
from ui.views.main_window import MainWindow
from utils.config import ConfigManager


class QtUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.config = ConfigManager(Path(self.folder.name))
        self.runner = Mock()
        self.runner.process = None
        self.runner.output_thread = None
        self.runner.job_handle = None
        self.controller = AppController(config=self.config, runner=self.runner,
                                        platform="linux", tray_enabled=False)
        self.window = MainWindow(self.controller)
        self.controller.set_window(self.window)
        self.app.processEvents()

    def tearDown(self):
        self.controller.shutdown()
        delete(self.window)
        delete(self.controller)
        self.folder.cleanup()

    def wait_for(self, predicate, timeout=2):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self.app.processEvents()
            if predicate():
                return
            time.sleep(0.005)
        self.fail("Qt signal was not delivered")

    def test_one_window_and_initial_linux_wording(self):
        self.assertEqual(self.window.status.heading.text(), "Local Proxy Inactive")
        self.assertIn("SpoofDPI", self.window.status.detail.text())
        self.assertEqual(self.window.dns.backend.text(), "SpoofDPI · local HTTP proxy")
        self.assertEqual(self.window.status.action.text(), "Enable")
        self.assertFalse(self.window.activity.log.isVisible())
        self.assertEqual(sum(isinstance(w, MainWindow) for w in self.app.topLevelWidgets()), 1)

    def test_windows_copy(self):
        self.controller.state.platform = "windows"
        self.controller.state_changed.emit(self.controller.state)
        self.assertEqual(self.window.status.heading.text(), "Protection Inactive")
        self.assertIn("GoodbyeDPI", self.window.status.detail.text())
        self.controller.state.phase = Phase.ACTIVE
        self.controller.state_changed.emit(self.controller.state)
        self.assertEqual(self.window.status.heading.text(), "Protection Active")
        self.assertEqual(self.window.dns.backend.text(), "GoodbyeDPI · DNS redirection")

    def test_enable_disable_and_endpoint(self):
        self.window.status.action.click()
        self.assertIn(self.controller.state.phase, (Phase.STARTING, Phase.ACTIVE))
        self.wait_for(lambda: self.controller.state.phase == Phase.ACTIVE)
        self.runner.start.assert_called_once_with(dns_addr="77.88.8.8", dns_port="1253")
        self.assertEqual(self.window.status.heading.text(), "Local Proxy Active")
        self.assertIn("127.0.0.1:8080", self.window.status.detail.text())
        self.assertFalse(self.window.dns.selector.isEnabled())
        self.window.status.action.click()
        self.wait_for(lambda: self.controller.state.phase == Phase.INACTIVE)
        self.runner.stop.assert_called_once()
        self.assertTrue(self.window.dns.selector.isEnabled())

    def test_failed_start_stays_error_and_retryable(self):
        self.runner.start.side_effect = FileNotFoundError("SpoofDPI not found")
        self.controller.start()
        self.wait_for(lambda: self.controller.state.phase == Phase.ERROR)
        self.assertEqual(self.window.status.action.text(), "Enable")
        self.assertIn("SpoofDPI not found", self.window.status.detail.text())
        self.assertNotIn("Active", self.window.status.heading.text())

    def test_port_collision_does_not_claim_active(self):
        self.runner.start.side_effect = OSError("Port 8080 is already in use")
        self.controller.start()
        self.wait_for(lambda: self.controller.state.phase == Phase.ERROR)
        self.assertIn("Port 8080", self.window.status.detail.text())

    def test_unreaped_stop_does_not_claim_inactive(self):
        self.controller.state.phase = Phase.ACTIVE
        self.runner.process = Mock()
        self.controller.stop()
        self.wait_for(lambda: self.controller.state.phase == Phase.ERROR)
        self.assertIn("did not exit", self.window.status.detail.text())

    def test_unreaped_quit_keeps_qt_running_and_allows_retry(self):
        self.runner.process = Mock()
        with patch.object(QApplication, "quit") as quit_qt:
            self.controller.quit_app()
            quit_qt.assert_not_called()
            self.assertEqual(self.controller.state.phase, Phase.ERROR)
            self.assertFalse(self.controller._shutdown_complete)
            self.runner.process = None
            self.controller.quit_app()
            quit_qt.assert_called_once()
        self.runner.close.assert_called()

    def test_dns_load_and_save(self):
        self.config.save_config("dns_provider", "Google")
        self.controller.state.dns_provider = "Google"
        self.controller.state_changed.emit(self.controller.state)
        self.assertEqual(self.window.dns.selector.currentText(), "Google")
        self.window.dns.selector.setCurrentText("Cloudflare")
        self.assertEqual(ConfigManager(Path(self.folder.name)).get("dns_provider"), "Cloudflare")

    def test_startup_toggle(self):
        with patch("app_controller.startup.set_enabled") as set_enabled:
            self.window.preferences.startup.click()
        set_enabled.assert_called_once_with(True)
        self.assertTrue(self.controller.state.startup_enabled)

    def test_theme_persistence_and_modes(self):
        for name in ("Light", "Dark", "System"):
            self.window.preferences.theme.setCurrentText(name)
            self.assertEqual(self.config.get("theme"), name)
            self.assertEqual(self.controller.state.theme, name)
        self.assertIn(resolve_theme("System"), ("Light", "Dark"))
        self.assertEqual(resolve_theme("Light"), "Light")
        self.assertEqual(resolve_theme("Dark"), "Dark")

    def test_activity_expands_and_log_arrives_on_gui_thread(self):
        received = []
        self.controller.state_changed.connect(lambda _: received.append(QThread.currentThread() == self.app.thread()))
        worker = threading.Thread(target=lambda: self.controller.log("reader line"))
        worker.start()
        worker.join()
        self.wait_for(lambda: "reader line" in self.window.activity.log.toPlainText())
        self.assertTrue(all(received))
        self.window.activity.button.click()
        self.assertTrue(self.controller.state.activity_expanded)
        self.assertFalse(self.window.activity.log.isHidden())
        self.window.activity.button.click()
        self.assertFalse(self.controller.state.activity_expanded)

    def test_window_close_and_restore_same_window(self):
        self.controller.tray_available = True
        self.window.show()
        self.window.close()
        self.assertTrue(self.window.isHidden())
        self.controller.show_window()
        self.assertTrue(self.window.isVisible())
        self.assertIs(self.controller.window, self.window)

    def test_tray_primary_and_quit_call_safe_shutdown(self):
        self.controller.tray_available = True
        self.window.hide()
        self.controller._tray_activated(QSystemTrayIcon.ActivationReason.Trigger)
        self.assertTrue(self.window.isVisible())
        with patch.object(self.controller, "shutdown", wraps=self.controller.shutdown) as shutdown:
            self.controller.quit_app()
            self.controller.quit_app()
        self.assertGreaterEqual(shutdown.call_count, 1)
        self.runner.close.assert_called_once()

    def test_accessible_names_and_minimum_size(self):
        self.assertIn("proxy", self.window.status.action.accessibleName())
        self.assertEqual(self.window.dns.selector.accessibleName(), "DNS provider")
        self.assertEqual(self.window.preferences.startup.accessibleName(), "Run on startup")
        self.assertEqual(self.window.minimumWidth(), 520)
        self.assertEqual(self.window.minimumHeight(), 620)

    def test_keyboard_primary_action_and_tab_order(self):
        self.window.show()
        self.window.header.about_button.setFocus()
        next_control = self.window.header.about_button.nextInFocusChain()
        while next_control.focusPolicy() == Qt.FocusPolicy.NoFocus:
            next_control = next_control.nextInFocusChain()
        self.assertIs(next_control, self.window.status.action)
        QTest.keyClick(self.window.status.action, Qt.Key.Key_Space)
        self.wait_for(lambda: self.controller.state.phase == Phase.ACTIVE)
        QTest.keyClick(self.window.status.action, Qt.Key.Key_Space)
        self.wait_for(lambda: self.controller.state.phase == Phase.INACTIVE)

    def test_minimized_semantics_with_tray(self):
        self.controller.tray_available = True
        self.assertTrue(self.window.isHidden())
        self.controller.start()
        self.wait_for(lambda: self.controller.state.phase == Phase.ACTIVE)
        self.assertTrue(self.window.isHidden())
        self.controller.show_window()
        self.assertTrue(self.window.isVisible())


if __name__ == "__main__":
    unittest.main()
