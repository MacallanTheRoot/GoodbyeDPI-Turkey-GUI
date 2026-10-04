from PySide6.QtWidgets import QPushButton, QPlainTextEdit, QHBoxLayout, QLabel

from ui.theme import mono_font
from .common import card


class ActivityPanel:
    def __init__(self):
        self.widget, layout = card(margins=(18, 12, 18, 12), spacing=8)
        self.widget.setMinimumHeight(54)
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        self.button = QPushButton("Activity")
        self.button.setObjectName("activityToggle")
        self.button.setAccessibleName("Expand Activity")
        self.button.setMinimumHeight(28)
        self.arrow = QLabel("⌄")
        self.arrow.setObjectName("backend")
        header.addWidget(self.button, 1)
        header.addWidget(self.arrow)
        layout.addLayout(header)
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setFont(mono_font())
        self.log.setAccessibleName("Activity log")
        self.log.setFixedHeight(142)
        self.log.hide()
        layout.addWidget(self.log)

    def render(self, state):
        expanded = state.activity_expanded
        self.log.setVisible(expanded)
        self.arrow.setText("⌃" if expanded else "⌄")
        self.button.setAccessibleName("Collapse Activity" if expanded else "Expand Activity")
        contents = "\n".join(state.messages)
        if self.log.toPlainText() != contents:
            self.log.setPlainText(contents)
            bar = self.log.verticalScrollBar()
            bar.setValue(bar.maximum())
