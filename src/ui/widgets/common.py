from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QComboBox, QFrame, QVBoxLayout


class CompactComboBox(QComboBox):
    def paintEvent(self, event):
        super().paintEvent(event)
        from ui.theme import resolve_theme
        from ui.tokens import COLORS
        colors = COLORS[resolve_theme(self.property("themeChoice") or "System")]
        painter = QPainter(self)
        painter.setPen(QColor(colors["text/secondary"]))
        painter.drawText(self.width() - 26, 0, 20, self.height(),
                         Qt.AlignmentFlag.AlignCenter, "⌄")


def card(parent=None, margins=(18, 16, 18, 16), spacing=8):
    frame = QFrame(parent)
    frame.setObjectName("card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(*margins)
    layout.setSpacing(spacing)
    return frame, layout
