"""Connects platform services to an explicit Qt-facing state."""
import sys
import threading
from datetime import datetime

from PySide6.QtCore import QObject, QTimer, Signal, Slot
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from app_state import AppState, DNS_PROVIDERS, Phase
from utils import startup
from utils.config import ConfigManager
from utils.paths import resource_path
from utils.runner import DNSRunner


class AppController(QObject):
    state_changed = Signal(object)
    log_arrived = Signal(str)
    operation_finished = Signal(str, bool, str)

    def __init__(self, config=None, runner=None, platform=None, tray_enabled=True):
        super().__init__()
        self.config = config or ConfigManager()
        platform = platform or ("windows" if sys.platform == "win32" else "linux")
        saved_dns = self.config.get("dns_provider")
        saved_theme = self.config.get("theme")
        try:
            startup_enabled = startup.is_enabled()
        except (OSError, NotImplementedError):
            startup_enabled = False
        self.state = AppState(platform=platform,
                              dns_provider=saved_dns if saved_dns in DNS_PROVIDERS else "Turkey DNSRedir",
                              theme=saved_theme if saved_theme in ("System", "Light", "Dark") else "System",
                              startup_enabled=startup_enabled)
        self.runner = runner or DNSRunner(log_callback=self.log)
        self.window = None
        self._worker = None
        self._shutting_down = False
        self._shutdown_complete = False
        self.log_arrived.connect(self._append_log)
        self.operation_finished.connect(self._finish_operation)
        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(1000)
        self._poll_timer.timeout.connect(self.poll_process)
        self._poll_timer.start()
        self.tray_available = tray_enabled and QSystemTrayIcon.isSystemTrayAvailable()
        self.tray = None
        self.tray_menu = None
        if self.tray_available:
            self.tray = QSystemTrayIcon(QIcon(str(resource_path("assets", "icon.png"))), self)
            self.tray_menu = QMenu()
            self.show_action = QAction("Show", self.tray_menu)
            self.quit_action = QAction("Quit", self.tray_menu)
            self.show_action.triggered.connect(self.show_window)
            self.quit_action.triggered.connect(self.quit_app)
            self.tray_menu.addAction(self.show_action)
            self.tray_menu.addAction(self.quit_action)
            self.tray.setContextMenu(self.tray_menu)
            self.tray.activated.connect(self._tray_activated)
            self.tray.show()

    def set_window(self, window):
        self.window = window
        self.state_changed.emit(self.state)

    @Slot(QSystemTrayIcon.ActivationReason)
    def _tray_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger,
                      QSystemTrayIcon.ActivationReason.DoubleClick):
            self.show_window()

    @Slot()
    def show_window(self):
        if self._shutting_down or self.window is None:
            return
        self.window.showNormal()
        self.window.raise_()
        self.window.activateWindow()

    def hide_window(self):
        if self._shutting_down or self.window is None:
            return
        if self.tray_available:
            self.window.hide()
        else:
            self.quit_app()

    def log(self, message):
        # This signal may be emitted by DNSRunner's output reader thread.
        self.log_arrived.emit(str(message))

    @Slot(str)
    def _append_log(self, message):
        if self._shutting_down:
            return
        line = f"{datetime.now():%H:%M:%S}  {message}"
        self.state.messages.append(line)
        self.state_changed.emit(self.state)

    def _run_operation(self, name, operation):
        def work():
            try:
                operation()
                self.operation_finished.emit(name, True, "")
            except Exception as exc:
                self.operation_finished.emit(name, False, str(exc))
        self._worker = threading.Thread(target=work, name=f"engine-{name}")
        self._worker.start()

    @Slot()
    def start(self):
        if self._shutting_down or self.state.phase not in (Phase.INACTIVE, Phase.ERROR):
            return
        name = self.state.dns_provider
        address, port = DNS_PROVIDERS[name]
        self.state.phase = Phase.STARTING
        self.state.error = ""
        self.state_changed.emit(self.state)
        self.log(f"Starting service with {name} ({address}:{port})…")
        self._run_operation("start", lambda: self.runner.start(dns_addr=address, dns_port=port))

    @Slot()
    def stop(self):
        if self._shutting_down or self.state.phase != Phase.ACTIVE:
            return
        self.state.phase = Phase.STOPPING
        self.state_changed.emit(self.state)
        self.log("Stopping service…")
        self._run_operation("stop", self.runner.stop)

    @Slot(str, bool, str)
    def _finish_operation(self, name, success, error):
        if self._shutting_down:
            return
        if name == "start":
            self.state.phase = Phase.ACTIVE if success else Phase.ERROR
            if not success:
                self.state.error = error
                self.log(f"Error starting: {error}")
            else:
                self.log("Service active.")
        else:
            if success and self.runner.process is not None:
                success = False
                error = "The engine did not exit. Open Activity for details."
            self.state.phase = Phase.INACTIVE if success else Phase.ERROR
            if not success:
                self.state.error = error
                self.log(f"Error stopping: {error}")
            else:
                self.log("Service stopped.")
        self.state_changed.emit(self.state)

    @Slot()
    def poll_process(self):
        if self._shutting_down or self.state.phase != Phase.ACTIVE:
            return
        process = self.runner.process
        if process is not None and process.poll() is not None:
            self.runner.stop()
            self.state.phase = Phase.ERROR
            self.state.error = "The engine exited. Open Activity for details."
            self.log(self.state.error)
            self.state_changed.emit(self.state)

    def set_dns(self, provider):
        if self.state.phase not in (Phase.INACTIVE, Phase.ERROR) or provider not in DNS_PROVIDERS:
            return
        self.config.save_config("dns_provider", provider)
        self.state.dns_provider = provider
        self.state_changed.emit(self.state)

    def set_theme(self, theme):
        if theme not in ("System", "Light", "Dark"):
            return
        self.config.save_config("theme", theme)
        self.state.theme = theme
        self.state_changed.emit(self.state)

    def set_startup(self, enabled):
        try:
            startup.set_enabled(enabled)
        except Exception as exc:
            self.log(f"Could not change autostart: {exc}")
        else:
            self.state.startup_enabled = enabled
            self.log("Autostart enabled." if enabled else "Autostart disabled.")
        self.state_changed.emit(self.state)

    def set_activity_expanded(self, expanded):
        self.state.activity_expanded = expanded
        self.state_changed.emit(self.state)

    @Slot()
    def quit_app(self):
        if self.shutdown():
            QApplication.instance().quit()

    @Slot()
    def shutdown(self):
        if self._shutdown_complete:
            return True
        if self._shutting_down:
            return False
        self._shutting_down = True
        self.state.phase = Phase.SHUTTING_DOWN
        self.state_changed.emit(self.state)
        self._poll_timer.stop()
        if self._worker and self._worker.is_alive() and self._worker is not threading.current_thread():
            self._worker.join(timeout=15)
        if self._worker and self._worker.is_alive():
            self._shutdown_failed("An engine operation is still running. Try Quit again.")
            return False
        try:
            self.runner.close()
        except Exception as exc:
            self._shutdown_failed(f"Could not finish engine cleanup: {exc}")
            return False
        if any(getattr(self.runner, name, None) is not None
               for name in ("process", "output_thread", "job_handle")):
            self._shutdown_failed("The engine still holds resources. Try Quit again.")
            return False
        self._shutdown_complete = True
        if self.tray is not None:
            self.tray.hide()
        return True

    def _shutdown_failed(self, message):
        self._shutting_down = False
        self.state.phase = Phase.ERROR
        self.state.error = message
        self.state_changed.emit(self.state)
        self.log(message)
        self._poll_timer.start()
        if self.window is not None:
            self.show_window()
