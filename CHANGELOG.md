# Changelog

## 1.0.1rc1 — release candidate

- Rebuilt the desktop interface with PySide6 Widgets, accessible names and keyboard focus, Light, Dark and System themes, and one Qt tray.
- Improved Windows GoodbyeDPI shutdown so Quit waits for child cleanup, stream readers and the Job Object before the application exits.
- Added Linux support through an externally installed SpoofDPI v0.12.0 local HTTP proxy at `127.0.0.1:8080`. Applications must select that proxy.
- Moved settings and autostart into per-user platform locations; added Debian/Kali packaging and a staged manual installer.
- Added dedicated Windows and Linux PyInstaller specifications, release validation tests, and CI build definitions.

Native Windows and Kali Linux functional sign-off completed for the release candidate artifacts. GitHub Actions verification is required before publication.
