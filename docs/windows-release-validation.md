# Windows 1.0.1rc1 native sign-off

Use a real Windows x64 machine. Copy `dist/GoodbyeDPI-Turkey-1.0.1rc1-windows-build-source.zip` to a fresh working directory and open PowerShell in the directory containing that ZIP. Compare its SHA-256 with the value in the Phase 6A report or `dist/SHA256SUMS` on the source machine. Do not use an older checkout or EXE. PowerShell does **not** need to be elevated to build. The app requests UAC when launched normally.

## Build (copy/paste in PowerShell from the directory containing the ZIP)

```powershell
Get-FileHash .\GoodbyeDPI-Turkey-1.0.1rc1-windows-build-source.zip -Algorithm SHA256
Expand-Archive .\GoodbyeDPI-Turkey-1.0.1rc1-windows-build-source.zip -DestinationPath .\rc -Force
Set-Location .\rc\GoodbyeDPI-Turkey-1.0.1rc1-windows-build-source
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:QT_QPA_PLATFORM = 'offscreen'
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
Remove-Item Env:\QT_QPA_PLATFORM
.\build.bat
.\tools\windows\validate_rc.ps1
Get-FileHash .\dist\GoodbyeDPI-Turkey.exe -Algorithm SHA256
```

If already inside the extracted project directory, begin at `py -3 --version`. If PowerShell script execution is restricted, run `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\windows\validate_rc.ps1`; this helper only reads local state. Record the EXE byte size and SHA-256 in the result template. Keep the full build log if the build fails. Check that the onefile `dist\GoodbyeDPI-Turkey.exe` exists and there is no missing Qt platform/image plugin or bundled resource error. The build script requires `.venv` and uses the Windows spec. No Git is needed.

## Human test sequence

Close any older copy and check processes before testing:

```powershell
Get-Process GoodbyeDPI-Turkey,goodbyedpi -ErrorAction SilentlyContinue
.\tools\windows\validate_rc.ps1
```

Record PASS/FAIL for every row. Use a site or service already suitable for your own network to check real bypass behavior; record what was tested. A browser response alone is not proof unless the site was blocked before enabling. The tester judges GUI appearance; the helper cannot.

| ID | Action and pass condition | Result |
| --- | --- | --- |
| A | Clean onefile build succeeds; EXE exists, icon/version and bundled resources load; record bytes and SHA-256. | ___ |
| B | Launch `./dist/GoodbyeDPI-Turkey.exe` normally. Exactly one UAC prompt if not already elevated; one window, correct icon, **Protection Inactive**. | ___ |
| C | Click **Enable**. `goodbyedpi.exe` runs, state becomes **Protection Active**, GUI responds; verify an appropriate previously blocked site/service. | ___ |
| D | Click window X. GUI hides, GoodbyeDPI keeps running, tray icon remains. Primary tray click restores the **same** window without another app process/window. Right-click shows **Show** and **Quit**. | ___ |
| E | Click **Disable**. State becomes **Protection Inactive**; GoodbyeDPI exits and no stale WinDivert symptom remains. | ___ |
| F | Enable again, then tray **Quit** while active. GUI and GoodbyeDPI exit, WinDivert releases, no visible `_MEI` warning or delayed cleanup error. Recheck processes with helper. | ___ |
| G | Launch again, leave inactive, tray **Quit**; clean exit. | ___ |
| H | Run `./dist/GoodbyeDPI-Turkey.exe --minimized`. Accept one UAC prompt if shown. No normal main-window flash if avoidable; tray appears, **Show** restores the existing window, Enable/Disable still work. | ___ |
| I | Enable **Run on startup**. Confirm Startup shortcut target and `--minimized` argument under `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`; log out/reboot once if practical, verify startup and UAC behavior, then disable startup and confirm shortcut removal. | ___ |
| J | Select **System**, **Light**, **Dark**. Text, status colors and controls remain readable and usable. | ___ |
| K | Use Tab/Shift+Tab, Enter/Space through primary controls; focus is visible and the order is sensible. | ___ |
| L | Inspect at **100%, 125%, 150%, 200%** display scaling; record clipping, overflow, truncated labels, hidden controls, blurry assets or unusable minimum size. | ___ |
| M | After final Quit, helper and Task Manager show no GUI or GoodbyeDPI child; no cleanup warning. | ___ |

For process checks use `Get-Process GoodbyeDPI-Turkey,goodbyedpi -ErrorAction SilentlyContinue` while active and after Quit. For WinDivert, inspect the helper's driver/service output and test that activation works again after Disable/Quit; a stopped driver entry by itself is not a leak. A recent `_MEI*` directory may belong to another app, so record a warning only when it is tied to this EXE's exit. The helper prints observations and changes no proxy, firewall or security settings.

Fill in [the concise result template](windows-release-validation-result-template.md) and return it with the EXE hash, build log on failure, and screenshots for visual defects. Native Windows sign-off requires the result, not just a CI build.
