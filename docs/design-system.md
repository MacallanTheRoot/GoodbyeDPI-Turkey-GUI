# UI foundations

The application uses a compact utility layout. The status and one primary action come first; DNS and preferences are secondary; Activity starts collapsed. A window may scroll at increased desktop scaling. The visual language follows hierarchy, restraint, and familiar controls without platform-owned assets or simulated system chrome.

`src/utils/theme.py` is the source of truth for light and dark semantic colors. Components use semantic roles (`background`, `surface`, `surface_alt`, `text`, `muted`, `border`, `accent`, `success`) rather than inline hex values. The spacing scale is 4, 8, 16, 24, and 32 pixels. Cards have a 16 pixel radius; controls have a 12 pixel radius.

| Component | States | Role |
| --- | --- | --- |
| Protection card | Off, active, engine error | Text and indicator communicate state together |
| Primary action | Activate, deactivate, disabled during exit | One prominent action |
| DNS option menu | Enabled, disabled while active | Selects the engine DNS address |
| Startup switch | On, off | User-level autostart |
| Appearance menu | System, light, dark | Changes both semantic color modes |
| Activity section | Collapsed, expanded | Keeps logs available without dominating the window |

Segoe UI Variable is requested on Windows. Linux requests Noto Sans, with the desktop's font fallback if unavailable. The shield icon is original art generated in `src/utils/icon_generator.py`. No Apple font, icon, or other proprietary asset is bundled.
