# v1.0.1-rc1 — Pre-release

Application version `1.0.1rc1`; Debian version `1.0.1~rc1`. This is a release candidate for wider testing.

## What changed

- A complete PySide6 / Qt Widgets interface redesign replaces the previous Tk interface. It adds Light, Dark and System themes, clearer service state, keyboard focus and accessible control names.
- Windows tray handling uses the Qt event loop. Closing the window hides it; Show restores the same window. Quit waits for GoodbyeDPI and its resources to close before the GUI exits.
- Linux/Kali support runs an **external** SpoofDPI v0.12.0 local HTTP proxy on `127.0.0.1:8080`. Browsers and other applications must be configured to use that proxy. It is **not a VPN** and does **not transparently protect all system traffic**.
- Per-user settings and autostart use Windows AppData or Linux XDG paths. Linux installation is available as a Debian/Kali `.deb`, a manual onedir installer, or a portable archive.
- Windows and Linux packaging now have dedicated PyInstaller specifications; the Windows build carries an icon, version information and both bundled engine architectures.

## Validation and sources

The Windows asset is the exact native-tested executable (SHA-256 `21900e25a99aa2df55c7aa3e1eaca3c83df7c64f4d8b2ae8e816f19bf4ad9ae8`). The Debian package was installed and exercised with a real SpoofDPI proxy on Kali. Its SHA-256 is `59a20e35f45847c48b32bff075194e328c7aee931ea18c727307d0bbf6df4a80`.

The Qt/PySide6, WinDivert and GoodbyeDPI source archives and the application build-source archive are included with the binary assets. See [Qt LGPL compliance](https://github.com/MacallanTheRoot/GoodbyeDPI-Turkey-GUI/blob/v1.0.1-rc1/docs/qt-lgpl-compliance.md) for the source and modified-library rebuild path. Verify downloads with `SHA256SUMS`.
