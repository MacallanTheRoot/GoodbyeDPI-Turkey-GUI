from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton

from utils.paths import resource_path
from metadata import APP_NAME, DISPLAY_VERSION


class AppHeader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("header")
        row = QHBoxLayout(self)
        row.setContentsMargins(4, 0, 4, 0)
        row.setSpacing(12)
        mark = QLabel()
        mark.setPixmap(QPixmap(str(resource_path("assets", "icon.png"))).scaled(
            36, 36, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        mark.setFixedSize(36, 36)
        mark.setAccessibleName("GoodbyeDPI Turkey app mark")
        row.addWidget(mark)
        titles = QVBoxLayout()
        titles.setContentsMargins(0, 0, 0, 0)
        titles.setSpacing(0)
        title = QLabel(APP_NAME)
        title.setObjectName("title")
        version = QLabel(DISPLAY_VERSION)
        version.setObjectName("version")
        titles.addWidget(title)
        titles.addWidget(version)
        row.addLayout(titles, 1)
        self.about_button = QPushButton("About")
        self.about_button.setObjectName("link")
        self.about_button.setAccessibleName("About GoodbyeDPI Turkey")
        self.about_button.setMinimumSize(60, 40)
        row.addWidget(self.about_button)
        self.setMinimumHeight(54)
