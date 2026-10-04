# Phase 4A UI redesign specification

**Decision:** PySide6 / Qt 6 Widgets, per [ADR-001](ADR-001-ui-framework.md). This document is the Phase 4B implementation contract; no production UI migration is part of Phase 4A.

**Figma:** [GoodbyeDPI Turkey — Desktop App Redesign](https://www.figma.com/design/BRUdj1sIugCs5RZFOdjSAV) (`BRUdj1sIugCs5RZFOdjSAV`). Pages: `01 — Foundations`, `02 — Components`, `03 — Windows`, `04 — Linux`, `05 — Notes / Handoff`. The file has editable text, vectors and component instances, not flattened screen images.

## Product intent and guardrails

The app is a calm, compact desktop controller. Its hierarchy is header, primary status, DNS/backend, preferences, collapsed Activity, and low-emphasis footer. No sidebar or fake platform chrome. The visual direction uses restrained contrast and whitespace; it does not imply VPN, encryption, anonymity, or Linux-wide protection.

The Windows backend is **GoodbyeDPI**. The Linux backend is **SpoofDPI**, which starts a **local HTTP proxy**. Linux applications must be configured to use `127.0.0.1:8080`; the app does not set the system proxy. The DNS selector supplies the backend arguments already implemented in `DNSRunner`; the interface must not imply identical DNS behavior across platforms.

## Figma screen inventory

| Page | Frame | Node ID | State |
| --- | --- | --- | --- |
| Windows | Windows / Inactive / Light | `9:2` | Inactive, Light |
| Windows | Windows / Active / Light | `9:56` | Active, Light |
| Windows | Windows / Inactive / Dark | `9:100` | Inactive, Dark |
| Windows | Windows / Active / Dark | `9:141` | Active, Dark |
| Linux | Linux / Inactive / Light | `11:2` | Inactive, Light |
| Linux | Linux / Local Proxy Active / Light | `11:56` | Active, Light |
| Linux | Linux / Inactive / Dark | `11:100` | Inactive, Dark |
| Linux | Linux / Local Proxy Active / Dark | `11:141` | Active, Dark |
| Linux | Linux / Local Proxy Active / Activity Expanded / Light | `11:182` | Expanded Activity reference |

The eight default frames are **576 × 720 logical px**. The expanded reference is **576 × 896** to show all log content on the Figma canvas; the runtime window should stay at its normal size and scroll its content. The minimum usable window is **520 × 620 logical px**. At smaller physical screens or higher scaling, use a `QScrollArea` for the main column; keep the primary action reachable and avoid truncating status or proxy instructions. The window is resizable. At 576 px width, use 24 px outer padding, 528 px content, 14 px section gaps. Default section heights in Figma: header 54, status 176, DNS/backend 144, preferences 142, collapsed Activity 54, footer 24. Treat these as visual targets, not fixed widget heights when text needs more room.

## Design tokens

Figma has `Palette` (34 base values), `Color` (18 semantic values with Light/Dark modes), `Spacing` (7 values), `Radius` (3 values), and `Icon` (4 size values). Semantic colors alias the palette. Variables have scopes and code syntax. In Python, keep the semantic names; implement as `QColor`/`QPalette` values or QSS properties. The CSS syntax attached to Figma variables is handoff metadata, not a request to use a web renderer.

| Semantic color | Light | Dark | Main use |
| --- | --- | --- | --- |
| `color/bg/window` | `#F6F7F9` | `#11161D` | Root window |
| `color/bg/surface` | `#FFFFFF` | `#1B222B` | Cards |
| `color/bg/elevated` | `#FAFBFC` | `#222B35` | Popovers / raised surfaces |
| `color/bg/secondary` | `#EDF1F5` | `#2B3541` | Select and log well |
| `color/text/primary` | `#192434` | `#EEF2F6` | Status and headings |
| `color/text/secondary` | `#526174` | `#B6C1CE` | Body support |
| `color/text/tertiary` | `#617084` | `#95A4B5` | Version / quiet metadata |
| `color/text/on-accent` | `#FFFFFF` | `#17263A` | Accent button label |
| `color/border/default` | `#D8E0E8` | `#3B4857` | Stronger divisions |
| `color/border/subtle` | `#E7ECF1` | `#2F3B49` | Card borders |
| `color/accent/default` | `#315FA7` | `#91B4F0` | Enable and links |
| `color/accent/hover` | `#28518F` | `#A8C4F4` | Hover |
| `color/accent/pressed` | `#1E4279` | `#779DDD` | Pressed |
| `color/status/success` | `#207759` | `#73D2AA` | Active indicator |
| `color/status/warning` | `#9B651C` | `#E8B86C` | Recoverable warning |
| `color/status/error` | `#B33F49` | `#F08A92` | Error |
| `color/status/inactive` | `#6D7A89` | `#94A3B5` | Inactive indicator |
| `color/focus/ring` | `#315FA7` | `#A8C4F4` | Keyboard focus |

Spacing values are **4, 8, 12, 16, 24, 32, 40 px**, used on an 8 px-oriented grid with 4 and 12 for compact controls. Radius values: **control 9 px**, **card 14 px**, **larger surface 18 px**. Icon slots: **16, 20, 24, 32 px**; the app mark is shown at **36 px**. Avoid pill buttons, gratuitous shadows, and large gradients. Use a 1 px subtle border on cards, with no broad blur.

### Typography

The Figma source uses **Inter** as a neutral design reference and **Roboto Mono** for logs. Runtime font stacks:

- Windows: `Segoe UI Variable`, then `Segoe UI`, then system sans. Do not bundle or redistribute Segoe.
- Linux: installed `Inter` when available, then `Noto Sans`, then system sans. Do not require Inter to launch; bundle it only after a license and packaging review.
- Logs: installed `Roboto Mono`, then `Noto Sans Mono`, then system monospace.

| Role | Figma size / line height | Weight |
| --- | --- | --- |
| App title | 20 / 28 px | Semibold |
| Status headline | 25 / 32 px | Semibold |
| Section title | 14 / 20 px | Semibold |
| Primary body | 13 / 20 px | Regular |
| Body emphasis / button | 13 / 20 px | Medium / semibold |
| Secondary body | 12 / 18 px | Regular |
| Caption | 12 / 18 px | Medium |
| Monospace log | 12 / 19 px | Regular |

Use QFont point or pixel sizing consistently and inspect `QFontMetrics` on both systems. Do not force Figma text-box heights when the selected platform font needs more room. Long labels should wrap in available space; controls may grow vertically. No Apple-proprietary fonts, symbols, or assets.

## Component inventory and behavior

The Figma Components page contains:

- `Button / Primary`, `Button / Secondary`, `Button / Icon`
- `Toggle` with On/Off variants
- `Select / Dropdown`
- `Status Indicator / Badge` with Active/Inactive variants
- `Card / Surface`
- `Setting Row`
- `App Mark` and `App Header`
- `Status Card` with Windows/Linux × Active/Inactive variants
- `Backend / DNS Row` with Windows/Linux variants
- `Preferences Card`
- `Activity / Log Container` with Collapsed/Expanded variants
- `App Footer`

Screen frames instantiate these components. The status badge, headline, supporting text, and single action form one status card. The action is `Enable` when inactive and `Disable` when active. Keep a neutral/secondary Disable appearance so Active does not look like an error. The selected DNS provider is readable in a compact selector; disable changes while the backend is active. The startup control is a real two-state control. The appearance selector offers `System`, `Light`, `Dark`.

Activity begins collapsed. Expanding it reveals a bounded, scrollable log area with monospaced rows and clear line spacing. It should not take focus or height from the primary status on initial launch. Copy/Clear controls are not included in this version because they add complexity without a demonstrated need. Do not print raw debug noise into the status card.

## Exact platform copy

| State | Status heading | Supporting text | Action | Backend label |
| --- | --- | --- | --- | --- |
| Windows inactive | `Protection Inactive` | `GoodbyeDPI is ready. Select Enable to start protection.` | `Enable` | `GoodbyeDPI · DNS redirection` |
| Windows active | `Protection Active` | `GoodbyeDPI is running. DNS selection is locked while active.` | `Disable` | `GoodbyeDPI · DNS redirection` |
| Linux inactive | `Local Proxy Inactive` | `SpoofDPI is ready. Applications need to use the local proxy.` | `Enable` | `SpoofDPI · local HTTP proxy` |
| Linux active | `Local Proxy Active` | `Applications must use 127.0.0.1:8080 to use this proxy.` | `Disable` | `SpoofDPI · local HTTP proxy` |

The badge also spells out `ACTIVE` or `INACTIVE`; the dot is supplementary. If startup fails, show an error detail with a retryable `Enable` action. If the engine exits unexpectedly, revert to inactive, report that the engine exited, and direct the user to Activity. Do not show `Protection Active` on Linux. Do not claim VPN, encryption, anonymity, or system-wide Linux coverage.

## State and integration model

Use a UI-facing state model with `INACTIVE`, `STARTING`, `ACTIVE`, `STOPPING`, `ERROR`, and `SHUTTING_DOWN`, plus a platform identity (`windows` / `linux`), selected provider, theme, startup preference, and Activity expansion state. Derive label, badge, action, and DNS enabled state from one state object. `ACTIVE` begins only after `DNSRunner.start()` succeeds; for Linux that includes the existing listener check. `INACTIVE` follows a completed stop. During transitions, disable the main action and DNS selector, show progress text, and avoid double starts/stops. On errors, show text as well as warning/error color.

Preserve these authorities and semantics:

- `src/utils/runner.py`: GoodbyeDPI arguments and Job Object behavior, SpoofDPI v0.12.0 arguments (`127.0.0.1:8080`, selected DNS address/port, `-system-proxy=false`), process polling, stopping, reaping and `close()`.
- `src/utils/config.py`: per-user `dns_provider` and `theme` keys and atomic writes.
- `src/utils/startup.py`: Windows shortcut and Linux `.desktop` behavior; the existing minimized-startup path also starts the service.
- `src/utils/paths.py`: source/frozen paths and read-only `/opt` deployment.
- `src/utils/tray.py` and current `App` callbacks: close hides, Show restores the same window, Quit performs centralized cleanup, and queued Show cannot revive a shutting-down app.

Do not change provider names, address/port values, backend arguments, autostart values, process cleanup order, or packaging mode. The current UI stores providers in `create_widgets()` and reads them in `start_service()`; move this data to a non-UI module or controller without changing it. The current `App` also owns runner, tray, settings, polling and widget mutation. That coupling is the main Phase 4B extraction target. Runner output currently arrives through a queue and is applied on the UI thread every 50 ms; preserve thread-safe delivery with Qt signals/slots or an equivalent main-thread bridge. Keep the 1 s unexpected-exit check or an equivalent event-driven check.

### Theme behavior

Explicit Light and Dark always select the corresponding semantic token values. `System` follows the OS appearance when Qt reports it; on platforms without a reliable signal, fall back to Light and keep the `System` preference saved. React to changes while running when possible. Reapply palette, stylesheet, icons and focus color together. Both modes use distinct surface values and readable text; do not invert an image of one mode.

### Tray and shutdown behavior

Closing the window hides it and keeps an active backend running. Windows primary tray activation restores the existing window; the right-click Show/Quit menu remains. On KDE/Wayland, check tray availability and retain a usable window/quit path when the desktop has no tray host. `Quit` is a final application exit and must call `DNSRunner.close()` before destroying the UI/tray. Keep callbacks on the GUI thread and preserve the current race protection for queued Show/Quit events. Test active and inactive Quit, unexpected engine exit, and startup-minimized flows on both platforms.

## Accessibility and scaling

- Natural Tab/Shift+Tab order: About, Enable/Disable, DNS selector, startup, appearance, Activity, footer links. Enter/Space activate buttons and toggle; arrow keys operate selects.
- A visible 2 px focus ring uses `color/focus/ring`; hover and focus are different. Do not remove Qt's focus behavior through QSS.
- Give controls meaningful accessible names and descriptions, including the endpoint instruction on Linux. The visual icon button is labeled for assistive technology.
- Use text, action wording and badge labels in addition to color. Disabled DNS and transition states must remain legible.
- Target at least 4.5:1 contrast for body text and 3:1 for larger text/control boundaries; check rendered results with platform font antialiasing.
- Main action minimum 44 px height; other clickable rows at least 40 px. The 30 px visual toggle lives inside a larger clickable setting row.
- Test 125%, 150%, and 200% scaling on Windows and KDE Wayland/X11, long translated strings, fallback fonts, and a narrow 520 px window. Use layouts, size hints and scroll areas rather than fixed absolute positions.
- Respect reduced-motion preferences where available. Optional status fades should be short and never hide state text or delay the action.

## Figma to Python widget mapping

| Figma object | Phase 4B widget / role |
| --- | --- |
| Screen frame | `MainWindow(QMainWindow)` or a QWidget central view in `QScrollArea` |
| App Header | `AppHeader(QWidget)` with QLabel mark/title/version and an accessible flat `QPushButton` for About |
| Status Card | `StatusCard(QWidget)` with status QLabel, detail QLabel and one `QPushButton` |
| Status Indicator / Badge | QLabel plus small decorative indicator; accessible status text comes from the label |
| Button / Primary, Secondary, Icon | Styled `QPushButton` or `QToolButton` with semantic properties |
| Backend / DNS Row and Select | `DNSCard(QWidget)` with `QComboBox` and backend detail QLabel |
| Preferences Card and Setting Row | `PreferencesCard(QWidget)` with `QCheckBox`/switch presentation and `QComboBox` for theme |
| Activity / Log Container | `ActivityPanel(QWidget)`, expandable button and read-only `QPlainTextEdit` inside a constrained area |
| App Footer | Accessible link buttons / `QDesktopServices.openUrl()` |
| Figma Color/Spacing/Radius | `tokens.py` semantic values, `theme.py` palette/QSS mapping |
| App Mark | Generated icon asset/pixmap derived from the existing original mark; no external Apple asset |

Suggested layout:

```text
src/
  main.py                  # bootstrap and current Windows elevation flow
  app_controller.py        # runner/config/startup/tray orchestration; no widgets
  app_state.py             # UI-facing state and platform copy
  ui/
    __init__.py
    app.py                 # QApplication setup and theme tracking
    theme.py               # QPalette/QSS generation
    tokens.py              # semantic color, type, spacing, radius values
    icons.py               # original icon adaptation
    views/main_window.py
    widgets/status_card.py
    widgets/dns_card.py
    widgets/preferences_card.py
    widgets/activity_panel.py
    widgets/app_header.py
```

The controller owns operations and publishes immutable state snapshots or signals. Widgets render state and emit user intent; they do not import `DNSRunner`, inspect `os.name`, write config, or manipulate processes. `main.py` remains the platform bootstrap. Keep `utils/*` as the backend and platform boundary.

## Phase 4B migration sequence

1. Pin a compatible PySide6-Essentials and Shiboken version in an isolated build environment; add a minimal Qt smoke build on Kali and Windows before removing dependencies. Measure installed and frozen size against the approximately 150 MB budget.
2. Extract provider data, platform copy and view state from `App.create_widgets()` while preserving values and tests. Define controller signals and lifecycle transitions.
3. Implement semantic tokens, both themes, font fallbacks and the 576 × 720 responsive window skeleton. Build reusable widgets from Figma component roles, not copied React/Tailwind output from Figma MCP.
4. Wire Enable/Disable, DNS lock, config theme/provider, startup preference, errors, process exit polling, and Activity log delivery through the controller. Preserve startup-minimized service behavior.
5. Integrate tray Show/Quit with the same cleanup contract. Test active/inactive exit, tray restoration, no tray host, listener collision, child cleanup, and the Windows `_MEI` extraction case.
6. Compare rendered Windows and Linux Light/Dark views with the Figma screens at default and high scaling. Check keyboard path, focus, contrast, long strings, accessible names, and Activity scrolling.
7. Build Windows onefile and Linux onedir; run the installed `/opt` build as a normal user. Measure size, startup, native Qt platform plugins, and Wayland/X11 behavior. Only then retire the old UI.

## Icon decision

**Refine later.** The current original blue shield in `src/utils/icon_generator.py` remains the Phase 4A app/tray mark and is reproduced as editable vector geometry in Figma. It is recognizable and already packaged, but a shield can overstate Linux's proxy scope. A later icon study should explore path, bypass, connection or boundary motifs without hacker imagery. Do not make icon redesign a dependency for Phase 4B's state and lifecycle migration.

## Phase 4A validation record

The current Kali app was visually inspected on KDE/Wayland. The Figma Windows and Linux Light/Dark screens and expanded Activity screen were rendered and reviewed. A white header fill and clipped Appearance row were corrected in reusable components; the Foundations sample copy and text height were corrected; Linux active copy now explicitly instructs proxy use. Light tertiary text was darkened after a contrast check. A structural audit found all nine screens within their frame bounds, 12 component instances in each screen, editable text, and no image-filled screen layers. The token audit found 18 Light/Dark semantic colors, no `ALL_SCOPES` variables, and code syntax on all 66 variables. Native Qt appearance, accessibility, packaging, and final binary sizes remain Phase 4B verification gates.
