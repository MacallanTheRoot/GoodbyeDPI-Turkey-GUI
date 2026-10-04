"""Single compact window composed from Figma section widgets."""
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMainWindow,
                               QMessageBox, QPushButton, QScrollArea, QVBoxLayout, QWidget)

from app_state import Phase
from metadata import APP_NAME, DISPLAY_VERSION, PROJECT_URL
from ui.theme import apply_theme
from ui.widgets.activity_panel import ActivityPanel
from ui.widgets.app_header import AppHeader
from ui.widgets.dns_card import DNSCard
from ui.widgets.preferences_card import PreferencesCard
from ui.widgets.status_card import StatusCard
from utils.paths import resource_path

class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(str(resource_path("assets", "icon.png"))))
        self.resize(576, 720)
        self.setMinimumSize(520, 620)
        self._applied_theme = None
        self.quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.quit_shortcut.activated.connect(controller.quit_app)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QWidget()
        content.setObjectName("content")
        column = QVBoxLayout(content)
        column.setContentsMargins(24, 24, 24, 24)
        column.setSpacing(14)
        self.header = AppHeader()
        self.status = StatusCard()
        self.dns = DNSCard()
        self.preferences = PreferencesCard()
        self.activity = ActivityPanel()
        self.footer = QWidget()
        self.footer.setObjectName("footer")
        footer_row = QHBoxLayout(self.footer)
        footer_row.setContentsMargins(0, 0, 0, 0)
        footer_row.setSpacing(2)
        self.github_button = QPushButton("GitHub")
        self.github_button.setObjectName("link")
        self.github_button.setAccessibleName("Open project on GitHub")
        self.footer_about_button = QPushButton("·  About")
        self.footer_about_button.setObjectName("link")
        self.footer_about_button.setAccessibleName("About GoodbyeDPI Turkey")
        footer_row.addWidget(self.github_button)
        footer_row.addWidget(self.footer_about_button)
        footer_row.addStretch(1)
        version = QLabel(DISPLAY_VERSION)
        version.setObjectName("footerVersion")
        footer_row.addWidget(version)
        self.footer.setMinimumHeight(24)
        for section in (self.header, self.status.widget, self.dns.widget,
                        self.preferences.widget, self.activity.widget, self.footer):
            column.addWidget(section)
        column.addStretch(1)
        scroll.setWidget(content)
        self.setCentralWidget(scroll)

        self.header.about_button.clicked.connect(self.open_about)
        self.status.action.clicked.connect(self._primary_action)
        self.dns.selector.currentTextChanged.connect(controller.set_dns)
        self.preferences.startup.toggled.connect(controller.set_startup)
        self.preferences.theme.currentTextChanged.connect(controller.set_theme)
        self.activity.button.clicked.connect(self._toggle_activity)
        self.github_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(PROJECT_URL)))
        self.footer_about_button.clicked.connect(self.open_about)
        controller.state_changed.connect(self.render)
        QApplication.instance().styleHints().colorSchemeChanged.connect(self._system_theme_changed)
        self.render(controller.state)
        QWidget.setTabOrder(self.header.about_button, self.status.action)
        QWidget.setTabOrder(self.status.action, self.dns.selector)
        QWidget.setTabOrder(self.dns.selector, self.preferences.startup)
        QWidget.setTabOrder(self.preferences.startup, self.preferences.theme)
        QWidget.setTabOrder(self.preferences.theme, self.activity.button)
        QWidget.setTabOrder(self.activity.button, self.github_button)
        QWidget.setTabOrder(self.github_button, self.footer_about_button)

    def _primary_action(self):
        if self.controller.state.phase == Phase.ACTIVE:
            self.controller.stop()
        else:
            self.controller.start()

    def _toggle_activity(self):
        self.controller.set_activity_expanded(not self.controller.state.activity_expanded)

    def _system_theme_changed(self, _scheme):
        if self.controller.state.theme == "System":
            apply_theme("System")
            self.preferences.startup.update()

    def render(self, state):
        if state.theme != self._applied_theme:
            apply_theme(state.theme)
            self._applied_theme = state.theme
        self.status.render(state)
        self.dns.selector.setProperty("themeChoice", state.theme)
        self.preferences.theme.setProperty("themeChoice", state.theme)
        self.dns.render(state)
        self.preferences.render(state)
        self.activity.render(state)
        self.preferences.startup.update()

    def open_about(self):
        backend = "GoodbyeDPI" if self.controller.state.platform == "windows" else "SpoofDPI"
        QMessageBox.about(self, f"About {APP_NAME}",
                          f"{APP_NAME} · {DISPLAY_VERSION}\n\nBackend: {backend}\n\nProject: {PROJECT_URL}")

    def closeEvent(self, event):
        if self.controller._shutting_down:
            event.accept()
        else:
            event.ignore()
            self.controller.hide_window()
