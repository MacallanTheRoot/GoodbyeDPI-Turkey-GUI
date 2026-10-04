"""Small semantic design system for CustomTkinter's light and dark modes."""
import sys

FONT = "Segoe UI Variable" if sys.platform == "win32" else "Noto Sans"

COLORS = {
    "background": ("#F5F6F8", "#15171B"),
    "surface": ("#FFFFFF", "#22252B"),
    "surface_alt": ("#ECEFF3", "#2D3138"),
    "text": ("#1C2532", "#F2F4F7"),
    "muted": ("#5D6978", "#A9B3C0"),
    "border": ("#DDE2E9", "#3A4049"),
    "accent": ("#365FA8", "#86A8EA"),
    "accent_hover": ("#294C8D", "#A0BCF1"),
    "accent_text": ("#FFFFFF", "#172337"),
    "success": ("#237A5C", "#78D3AA"),
}

SPACE = {"xs": 4, "sm": 8, "md": 16, "lg": 24, "xl": 32}
RADIUS = {"control": 12, "card": 16}
