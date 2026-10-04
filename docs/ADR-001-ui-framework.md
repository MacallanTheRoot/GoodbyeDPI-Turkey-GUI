# ADR-001: Use PySide6 Qt Widgets for the desktop UI

- **Status:** Accepted for Phase 4B planning
- **Date:** 2026-10-04
- **Scope:** Presentation framework only. Engine, DNS, configuration, startup, tray behavior, and shutdown semantics stay as they are.

## Context

The current application is a single `customtkinter.CTk` class in `src/main.py`. It creates the 480 × 720 window, owns `DNSRunner`, reads and writes settings, selects DNS arguments, manages the tray thread, polls process exit, drains log events, and performs shutdown. The existing UI has a useful card hierarchy and collapsed Activity section, but the code couples widget state to process state. A Kali KDE/Wayland visual inspection found a persistent scroll bar at the default size, Linux copy that still leans on Windows protection language, and small secondary text. The verified Linux onedir build is about 56 MB. The project accepts an application size around 150 MB.

The redesign needs a compact, polished utility on Windows and KDE Linux, including Wayland and X11, explicit Light and Dark modes, sound keyboard focus, accessible control names, and reliable scaling at 125%, 150%, and 200%. It must preserve the existing network and lifecycle behavior.

## Decision

Use **PySide6 with Qt 6 Widgets**, installed from the **PySide6-Essentials** package, for the Phase 4B UI. Use native QWidget layouts, QPalette and a restrained application stylesheet for semantic tokens. Keep process, platform, configuration, and autostart logic outside `src/ui/`. Introduce a controller/state adapter between widgets and those existing modules. No migration occurs in Phase 4A.

This is a Widgets decision, not a QML or WebEngine decision. It targets the current compact utility and avoids the much larger optional Qt modules. Qt does not automatically solve the current coupling; the migration must make the boundary explicit.

## Alternatives assessed

| Concern | CustomTkinter 5.2.2 | PySide6 / Qt 6 Widgets |
| --- | --- | --- |
| Windows appearance | Existing styled widgets are consistent and familiar. Fine control of focus and native behavior needs additional work. | Qt Widgets can be deliberately styled while retaining desktop control semantics. A custom palette and focused stylesheet are needed for the intended look. |
| KDE Linux, X11, Wayland | The current app runs under the Kali Wayland session, but Tk's integration and pystray remain separate concerns. | Qt offers X11 and Wayland platform integrations; QSystemTrayIcon documents StatusNotifierItem support on KDE and other Linux desktops. Actual compositor and tray behavior still need testing. |
| HiDPI and 125/150/200% | CustomTkinter documents automatic Windows scaling and manual widget/window scaling. Linux scaling requires more project testing. | Qt 6 uses device independent coordinates and Windows per-monitor DPI awareness by default; X11 DPI configuration is less uniform than Wayland/Windows. Layouts and font metrics still need tests. |
| Typography, Light/Dark | Color tuples work; the current theme is simple. CustomTkinter documents that `System` appearance currently remains Light on Linux. | QFont, QFontMetrics, QPalette and theme signals allow a platform-aware semantic type/color system. System theme detection needs a documented fallback on Linux. |
| Keyboard, focus, accessibility | Tk can be made keyboard usable, but each custom-drawn control needs explicit focus and accessibility verification. | Standard Qt controls provide established focus policies, tab order, keyboard behavior, and accessibility APIs. Styling must preserve the visible focus indicator. |
| Tray | Existing pystray logic works on Windows; Linux availability depends on the desktop backend. | QSystemTrayIcon offers one Qt event-loop integration. Phase 4B must preserve Show/Quit and cleanup behavior and test KDE/Wayland availability. |
| Styling and animation | Easy for the current static card UI; more complex states may need custom drawing. | Reusable QWidget classes, state properties, QSS and small QPropertyAnimation transitions support restrained motion. Avoid animation for essential meaning. |
| UI/backend separation and testing | Possible by refactoring, but the current `App` class encourages direct callbacks into business logic. | Signals, slots, QObject controllers and QTest support a clear presentation boundary. This is an architectural opportunity, not an automatic guarantee. |
| PyInstaller and deployment | Existing Windows onefile and Linux onedir paths are proven. The official CustomTkinter packaging page gives conservative onedir guidance, while this repository's onefile build is already in use. | Qt libraries and platform plugins must be collected and tested. Windows onefile remains a target; Linux onedir under `/opt` remains a target. Keep an isolated build environment and exclude unused Qt modules/plugins. |
| Migration effort | Smallest short-term edit; less regression risk. | Higher one-time rewrite and packaging test cost. Long-term component/state maintenance is better aligned with the target UI. |

## Why PySide6 wins

The size allowance gives Qt Widgets a narrow but testable route, and the target quality depends more on behavior than decorative styling: predictable scaling, font metrics, keyboard focus, accessible controls, and Linux desktop integration. Qt's layout and event model also gives Phase 4B a clean place to separate the UI from `DNSRunner` and the tray lifecycle. The Figma design uses six reusable screen sections with distinct platform states, which map directly to QWidget compositions.

Qt's [High DPI guidance](https://doc.qt.io/qtforpython-6/overviews/qtdoc-highdpi.html), [keyboard focus guidance](https://doc.qt.io/qtforpython-6/overviews/qtwidgets-focus.html), [QAccessible API](https://doc.qt.io/qtforpython-6/PySide6/QtGui/QAccessible.html), and [QSystemTrayIcon support matrix](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QSystemTrayIcon.html) support this assessment. The Linux and Windows appearance conclusions are engineering inferences for this app and require platform checks in Phase 4B.

## Why CustomTkinter loses

It remains a valid, small and already working choice. It loses this decision because the requested polish includes keyboard, focus, accessibility, Linux appearance behavior, and multiple scale factors. The existing single-class architecture can be refactored in either framework, but continuing with CustomTkinter leaves more custom control and platform work to validate. Its own [appearance documentation](https://customtkinter.tomschimansky.com/documentation/appearancemode) says Linux `System` mode resolves to Light; its [scaling documentation](https://customtkinter.tomschimansky.com/documentation/scaling/) emphasizes automatic macOS/Windows handling. The already working 56 MB package is its strongest advantage.

## Migration impact

Phase 4B should add `src/ui/` for widgets, theme and token mapping, with a small controller/state layer outside view classes. `DNSRunner`, `ConfigManager`, `startup`, and platform paths remain the authorities for their current behavior. Move `dns_options` out of widget construction without changing values or arguments. Route runner output and tray callbacks into the Qt main thread. A single state model must drive status text, Enable/Disable action, DNS enablement, and errors. Preserve the existing startup behavior, including minimized launch that starts the service.

Maintain the old UI until all nine Figma reference states, the 42 existing tests, lifecycle tests, and native platform smoke checks pass. Do not remove the known-good entry point early.

## Packaging impact and expected size class

- **Windows:** Keep `--onefile`, the bundled GoodbyeDPI binaries, elevation flow, and temporary extraction lifecycle. Add Qt Core/Gui/Widgets, Shiboken and required Windows platform plugins. Expect a larger executable and extraction/startup cost. **Planning range: about 85–135 MB**, pending a native Windows build; no Windows Qt bundle was measured in Phase 4A.
- **Linux:** Keep `--onedir`, x86_64 target and `/opt/goodbyedpi-turkey` install flow. Bundle required Qt platform plugins and their shared libraries; test both `xcb` and Wayland on the target Debian/Kali baseline. **Planning range: about 138–150 MB after audited plugin selection**, compared with the measured 56.5 MB current bundle. The optional Addons, QML and WebEngine packages should not be imported or collected. Avoid retaining Pillow and pystray solely for the new UI when Qt can render the original mark and provide the same tray behavior.

The Linux range is based on a **disposable size probe**, not a release build. On this Kali x86_64 host with Python 3.14, PyInstaller 6.16 and PySide6-Essentials 6.10.3, a minimal QWidget/QSystemTrayIcon import built to **160.9 MB** untrimmed. `--strip` reduced it to **159.5 MB**. Removing unused Qt translations, optional image formats, and non-desktop platform plugins yielded **150.8 MB**. A KDE-oriented copy without the GTK platform-theme plugin and its large GTK-only dependencies measured **137.5 MB** and launched under both Wayland and X11 (`xcb`) in bounded smoke runs. Those removals were made only in `/tmp` for estimation; Phase 4B needs a reproducible spec/filter and full feature checks, including tray, before adopting them. The real app and its exact plugin set may be larger. Phase 4B must measure native Windows and Linux artifacts against the approximately 150 MB budget before retiring CustomTkinter. Qt's [package split](https://doc.qt.io/qtforpython-6/package_details.html) and [PyInstaller hook configuration](https://pyinstaller.org/en/stable/hooks-config.html) inform the packaging plan.

## Risks

- Qt deployment can fail if platform plugins or system shared libraries are missing, especially on Linux. Build on the target distribution generation and run the installed `/opt` app as a normal user. The 150 MB target has little headroom; if a reproducible, fully working build exceeds it after safe trimming, use the rollback path.
- Native platform scaling, KDE tray availability, and System theme detection need real Windows/Wayland/X11 checks; documentation alone is insufficient.
- A Qt stylesheet can erase native focus cues. Keep explicit focus rings, accessible names, tab order, and real control states.
- The PySide6-Essentials/Qt license and bundled third-party notices need a release review. Qt for Python describes [LGPLv3/GPLv3 and commercial options](https://doc.qt.io/qtforpython-6/); this ADR does not decide distribution compliance.
- A process or tray rewrite made alongside the UI could regress cleanup. Preserve the current behavioral contract and test Show, Quit, failures, and child reaping.

## Rollback considerations

The decision is reversible before Phase 4B changes runtime code. During migration, retain the existing CustomTkinter implementation until the new UI passes parity and packaging checks. If Qt cannot meet the size or deployment constraints after a targeted plugin reduction, return to CustomTkinter with the same Figma information architecture and a separate controller. Do not roll back any completed backend or lifecycle work.
