"""Opt-in packaged GUI exercise for build validation; never runs in normal use."""
import json
import socket
import subprocess
import time

from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QSystemTrayIcon

from app_state import Phase
from ui.theme import resolve_theme


class PackagedSmoke(QObject):
    def __init__(self, app, controller, window, minimized=False):
        super().__init__(window)
        self.app = app
        self.controller = controller
        self.window = window
        self.minimized = minimized
        self.stage = "initial"
        self.deadline = time.monotonic() + 35
        self.result = {"platform": app.platformName(), "tray": controller.tray_available,
                       "minimized": minimized, "hide_restore": False,
                       "theme": resolve_theme(controller.state.theme, app),
                       "icon_loaded": not window.windowIcon().isNull()}
        self.timer = QTimer(self)
        self.timer.setInterval(30)
        self.timer.timeout.connect(self.tick)
        self.timer.start()

    @staticmethod
    def port_open():
        with socket.socket() as probe:
            probe.settimeout(0.2)
            return probe.connect_ex(("127.0.0.1", 8080)) == 0

    def finish(self, error=None):
        self.timer.stop()
        if error:
            self.result["error"] = error
            self.result["phase_on_error"] = self.controller.state.phase.value
            self.result["retry_enabled"] = self.window.status.action.isEnabled()
        self.result["pass"] = not error
        print(json.dumps(self.result), flush=True)
        if self.controller.tray_available:
            self.controller.quit_action.trigger()
        else:
            self.controller.quit_app()
        if error:
            self.app.exit(1)

    def tick(self):
        try:
            if time.monotonic() > self.deadline:
                raise TimeoutError(f"Timed out in {self.stage}")
            if self.stage == "initial":
                if not self.result["icon_loaded"]:
                    raise AssertionError("Packaged app icon missing")
                self.result["initial_heading"] = self.window.status.heading.text()
                self.result["initial_hidden"] = self.window.isHidden()
                if self.minimized and self.controller.tray_available and not self.window.isHidden():
                    raise AssertionError("--minimized displayed the window")
                if not self.minimized:
                    self.window.status.action.click()
                self.stage = "starting"
            elif self.stage == "starting" and self.controller.state.phase in (Phase.ACTIVE, Phase.ERROR):
                if self.controller.state.phase != Phase.ACTIVE:
                    raise RuntimeError(self.controller.state.error)
                self.result["active_heading"] = self.window.status.heading.text()
                self.result["endpoint"] = self.window.status.detail.text()
                if not self.port_open() or "127.0.0.1:8080" not in self.result["endpoint"]:
                    raise AssertionError("Proxy endpoint missing")
                response = subprocess.run(
                    ["curl", "--max-time", "20", "-sS", "-o", "/dev/null", "-w", "%{http_code}",
                     "-x", "http://127.0.0.1:8080", "https://example.com"],
                    capture_output=True, text=True)
                self.result["http_status"] = response.stdout
                if response.returncode or response.stdout != "200":
                    raise RuntimeError(f"Proxy curl failed: {response.stderr.strip()}")
                if self.controller.tray_available:
                    self.window.show()
                    self.window.close()
                    if not self.window.isHidden():
                        raise AssertionError("Window close did not hide")
                    self.controller._tray_activated(QSystemTrayIcon.ActivationReason.Trigger)
                    self.result["hide_restore"] = self.window.isVisible() and self.controller.window is self.window
                    if not self.result["hide_restore"]:
                        raise AssertionError("Tray activation did not restore the same window")
                self.controller.stop()
                self.stage = "stopping"
            elif self.stage == "stopping" and self.controller.state.phase in (Phase.INACTIVE, Phase.ERROR):
                if self.controller.state.phase != Phase.INACTIVE:
                    raise RuntimeError(self.controller.state.error)
                self.result["reaped"] = self.controller.runner.process is None
                self.result["port_free"] = not self.port_open()
                if not self.result["reaped"] or not self.result["port_free"]:
                    raise AssertionError("Backend remains after Disable")
                self.finish()
        except Exception as exc:
            self.finish(str(exc))
