"""Application-wide semantic palette, fonts, and controlled stylesheet."""
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QFontDatabase, QPalette
from PySide6.QtWidgets import QApplication

from .tokens import COLORS


def resolve_theme(choice, app=None):
    if choice in ("Light", "Dark"):
        return choice
    app = app or QApplication.instance()
    if app is not None and app.styleHints().colorScheme() == Qt.ColorScheme.Dark:
        return "Dark"
    return "Light"


def ui_font():
    available = set(QFontDatabase.families())
    choices = ("Segoe UI Variable", "Segoe UI") if sys.platform == "win32" else ("Inter", "Noto Sans")
    family = next((name for name in choices if name in available), QFont().defaultFamily())
    font = QFont(family)
    font.setPixelSize(13)
    return font


def mono_font():
    available = set(QFontDatabase.families())
    family = next((name for name in ("Roboto Mono", "Noto Sans Mono", "Consolas") if name in available),
                  QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont).family())
    font = QFont(family)
    font.setPixelSize(12)
    return font


def apply_theme(choice, app=None):
    app = app or QApplication.instance()
    mode = resolve_theme(choice, app)
    c = COLORS[mode]
    palette = QPalette()
    for role, key in ((QPalette.ColorRole.Window, "bg/window"),
                      (QPalette.ColorRole.WindowText, "text/primary"),
                      (QPalette.ColorRole.Base, "bg/surface"),
                      (QPalette.ColorRole.AlternateBase, "bg/secondary"),
                      (QPalette.ColorRole.Text, "text/primary"),
                      (QPalette.ColorRole.Button, "bg/secondary"),
                      (QPalette.ColorRole.ButtonText, "text/primary"),
                      (QPalette.ColorRole.Highlight, "accent/default"),
                      (QPalette.ColorRole.HighlightedText, "text/on-accent")):
        palette.setColor(role, QColor(c[key]))
    app.setPalette(palette)
    app.setFont(ui_font())
    app.setStyleSheet(f"""
        QWidget {{ color: {c['text/primary']}; background: {c['bg/window']}; }}
        QWidget#content, QWidget#header, QWidget#footer {{ background: transparent; }}
        QFrame#card {{ background: {c['bg/surface']}; border: 1px solid {c['border/subtle']}; border-radius: 14px; }}
        QFrame#card QLabel, QFrame#card QWidget#row {{ background: transparent; border: none; }}
        QLabel#title {{ font-size: 20px; font-weight: 600; }}
        QLabel#version, QLabel#footerVersion {{ color: {c['text/tertiary']}; font-size: 12px; }}
        QLabel#sectionTitle {{ font-size: 14px; font-weight: 600; }}
        QLabel#statusHeading {{ font-size: 25px; font-weight: 600; }}
        QLabel#detail, QLabel#backend, QLabel#badge {{ color: {c['text/secondary']}; font-size: 12px; }}
        QLabel#badge[status="active"] {{ color: {c['status/success']}; }}
        QLabel#badge[status="error"] {{ color: {c['status/error']}; }}
        QLabel#badge[status="starting"], QLabel#badge[status="stopping"] {{ color: {c['status/warning']}; }}
        QLabel#detail[error="true"] {{ color: {c['status/error']}; }}
        QLabel#statusDot {{ color: {c['status/inactive']}; font-size: 10px; }}
        QLabel#statusDot[status="active"] {{ color: {c['status/success']}; }}
        QLabel#statusDot[status="error"] {{ color: {c['status/error']}; }}
        QPushButton, QComboBox, QCheckBox {{ font-size: 13px; }}
        QPushButton:focus, QComboBox:focus, QCheckBox:focus {{ border: 2px solid {c['focus/ring']}; }}
        QPushButton#primary {{ background: {c['accent/default']}; color: {c['text/on-accent']};
            border: 2px solid transparent; border-radius: 9px; font-weight: 600; padding: 0 12px; }}
        QPushButton#primary:hover {{ background: {c['accent/hover']}; }}
        QPushButton#primary:pressed {{ background: {c['accent/pressed']}; }}
        QPushButton#primary:focus {{ border: 2px solid {c['focus/ring']}; }}
        QPushButton#primary:disabled {{ background: {c['bg/secondary']}; color: {c['text/tertiary']}; }}
        QPushButton#secondary {{ background: {c['bg/secondary']}; color: {c['text/primary']};
            border: 2px solid transparent; border-radius: 9px; font-weight: 600; }}
        QPushButton#secondary:hover {{ background: {c['border/default']}; }}
        QPushButton#secondary:focus {{ border: 2px solid {c['focus/ring']}; }}
        QPushButton#link {{ background: transparent; border: 2px solid transparent;
            color: {c['accent/default']}; padding: 0 4px; }}
        QPushButton#link:focus {{ border: 2px solid {c['focus/ring']}; border-radius: 9px; }}
        QPushButton#activityToggle {{ background: transparent; border: 2px solid transparent;
            text-align: left; font-size: 14px; font-weight: 600; padding: 0; }}
        QPushButton#activityToggle:focus {{ border: 2px solid {c['focus/ring']}; border-radius: 9px; }}
        QComboBox {{ background: {c['bg/secondary']}; color: {c['text/primary']};
            border: 2px solid transparent; border-radius: 9px; padding: 0 14px; }}
        QComboBox:disabled {{ color: {c['text/tertiary']}; }}
        QComboBox QAbstractItemView {{ background: {c['bg/elevated']}; color: {c['text/primary']};
            selection-background-color: {c['accent/default']}; selection-color: {c['text/on-accent']}; }}
        QComboBox::drop-down {{ border: none; width: 28px; }}
        QComboBox::down-arrow {{ image: none; }}
        QCheckBox {{ spacing: 12px; min-height: 40px; }}
        QCheckBox::indicator {{ width: 48px; height: 26px; border-radius: 13px;
            border: 1px solid {c['border/default']}; background: {c['bg/secondary']}; }}
        QCheckBox::indicator:checked {{ background: {c['accent/default']}; border-color: {c['accent/default']}; }}
        QPlainTextEdit {{ background: {c['bg/secondary']}; color: {c['text/secondary']};
            border: 2px solid transparent; border-radius: 9px; padding: 8px 10px; }}
        QPlainTextEdit:focus {{ border: 2px solid {c['focus/ring']}; }}
        QScrollArea {{ border: none; background: {c['bg/window']}; }}
        QWidget#footer QPushButton#link {{ color: {c['text/secondary']}; font-size: 12px; }}
    """)
    return mode
