from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QLabel, QWidget

from .common import card
from ui.tokens import COLORS
from ui.theme import resolve_theme
from .common import CompactComboBox


class Toggle(QCheckBox):
    """Accessible native checkbox with a Figma-sized painted switch."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_choice = "System"
        self.setFixedSize(52, 40)
        self.setAccessibleName("Run on startup")
        self.setAccessibleDescription("Start the application minimized when you sign in")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def paintEvent(self, event):
        colors = COLORS[resolve_theme(self.theme_choice)]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(colors["accent/default"] if self.isChecked() else colors["bg/secondary"]))
        painter.drawRoundedRect(0, 5, 52, 30, 15, 15)
        painter.setBrush(QColor(colors["text/on-accent"] if self.isChecked() else colors["status/inactive"]))
        painter.drawEllipse(26 if self.isChecked() else 4, 9, 22, 22)
        if self.hasFocus():
            pen = painter.pen()
            pen.setColor(QColor(colors["focus/ring"]))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(1, 5, 50, 30, 15, 15)


class PreferencesCard:
    def __init__(self):
        self.widget, layout = card(margins=(18, 12, 18, 12))
        self.widget.setMinimumHeight(142)
        title = QLabel("Preferences")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        startup_row = QWidget()
        startup_row.setObjectName("row")
        row = QHBoxLayout(startup_row)
        row.setContentsMargins(4, 0, 4, 0)
        row.addWidget(QLabel("Run on startup"))
        row.addStretch(1)
        self.startup = Toggle()
        row.addWidget(self.startup)
        layout.addWidget(startup_row)
        appearance_row = QWidget()
        appearance_row.setObjectName("row")
        appearance = QHBoxLayout(appearance_row)
        appearance.setContentsMargins(4, 0, 4, 0)
        appearance.addWidget(QLabel("Appearance"))
        appearance.addStretch(1)
        self.theme = CompactComboBox()
        self.theme.addItems(("System", "Light", "Dark"))
        self.theme.setAccessibleName("Appearance theme")
        self.theme.setMinimumSize(116, 40)
        appearance.addWidget(self.theme)
        layout.addWidget(appearance_row)
        layout.addStretch(1)

    def render(self, state):
        self.startup.theme_choice = state.theme
        self.startup.blockSignals(True)
        self.startup.setChecked(state.startup_enabled)
        self.startup.blockSignals(False)
        self.theme.blockSignals(True)
        self.theme.setCurrentText(state.theme)
        self.theme.blockSignals(False)
