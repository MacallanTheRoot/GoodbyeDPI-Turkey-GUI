# UI foundations

The production interface uses PySide6 / Qt Widgets. Status and the primary
Enable or Disable action come first; DNS and preferences are secondary;
Activity starts collapsed. The main window has a 520 × 620 minimum and
scrolls when scaling or longer text requires it.

`src/ui/tokens.py` defines Light and Dark semantic colors.
`src/ui/theme.py` applies the Qt palette and stylesheet. The design uses
distinct surfaces, readable text, visible focus, and state text alongside
color. The System preference follows Qt's reported appearance.

| Component | States | Role |
| --- | --- | --- |
| Status card | Inactive, starting, active, stopping, error | Text and indicator communicate state |
| Primary action | Enable, Disable, transition disabled | One prominent action |
| DNS selector | Enabled, disabled while active | Selects backend DNS address and port |
| Startup control | On, off | User-level autostart |
| Appearance selector | System, Light, Dark | Chooses semantic color mode |
| Activity | Collapsed, expanded | Shows bounded engine logs |

Segoe UI Variable is requested on Windows and Noto Sans on Linux, with
desktop font fallback. The original blue shield is retained as
`assets/icon.png` for Qt and Linux, and `assets/icon.ico` embeds
16–128 px resolutions for Windows. `packaging/generate_icon.py`
regenerates the ICO from the PNG. No platform-owned art is bundled.
