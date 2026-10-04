# GoodbyeDPI Turkey

A compact desktop controller for DPI circumvention. Windows runs the bundled GoodbyeDPI engine; Linux runs a separately installed SpoofDPI local proxy. The engines behave differently.

## English

### Windows

1. Download `GoodbyeDPI-Turkey.exe` from this project's Releases page, or build it using the instructions below.
2. Run it as Administrator. Windows may show a UAC prompt because GoodbyeDPI uses the WinDivert driver.
3. Choose a DNS provider and select **ACTIVATE**. Select **DEACTIVATE** to stop the engine.

Closing the window hides it in the system tray. On Windows, left-click the tray icon to restore the window; right-click opens **Show** and **Quit**. **Quit** stops and reaps GoodbyeDPI, closes its pipes, stops the tray, then exits. You do not need to deactivate first. The Windows build remains a PyInstaller `--onefile` executable; its engine is extracted under PyInstaller's temporary `_MEI...` directory while the app runs.

**Run on startup** creates a shortcut in `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`. Windows may prompt for elevation at each login. Configuration is stored in `%APPDATA%\GoodbyeDPI-Turkey\config.json`.

### Debian / Kali Linux

The GUI installs under `/opt/goodbyedpi-turkey/`, with a `goodbyedpi-turkey` command in `/usr/local/bin` and a desktop entry in `/usr/share/applications/`. Installation uses `sudo`; **run the GUI as your normal desktop user**. The app does not need root to run its local proxy.

Build and install the GUI:

```bash
sudo apt install python3 python3-venv python3-tk
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./build_linux.sh
sudo packaging/linux/install.sh
goodbyedpi-turkey
```

SpoofDPI is a separate upstream program. This app is tested with the reviewable [SpoofDPI v0.12.0 source tag](https://github.com/xvzc/SpoofDPI/tree/v0.12.0); with Go 1.21 or newer, install that exact version as your user:

```bash
go install github.com/xvzc/SpoofDPI/cmd/spoofdpi@v0.12.0
~/go/bin/spoofdpi -help
```

The GUI looks for `spoof-dpi` or `spoofdpi` in `PATH`, `~/go/bin`, `~/.spoof-dpi/bin`, `/usr/local/bin`, and `/opt/goodbyedpi-turkey/bin`. If missing, **ACTIVATE** shows an actionable error. The installer does not fetch or execute a remote shell script. Review upstream source or a release and its checksum before installing a binary.

On Linux, **ACTIVATE** starts SpoofDPI's proxy on `127.0.0.1:8080`. Configure a browser to use that HTTP proxy. The app passes the selected DNS address to SpoofDPI, but the Linux engine's DNS-over-HTTPS behavior is not identical to GoodbyeDPI's Windows DNS redirect. The selected DNS port is used only on Windows. The app explicitly leaves system proxy settings alone, so stopping it does not need to restore those settings. If you close the window, it hides to tray where supported; tray click behavior depends on the desktop backend. KDE/Wayland may require an AppIndicator compatible tray. Use the tray's **Quit** command for full cleanup.

**Run on startup** writes `$XDG_CONFIG_HOME/autostart/goodbyedpi-turkey.desktop` (or `~/.config/autostart/...`). Configuration is in `$XDG_CONFIG_HOME/goodbyedpi-turkey/config.json` (or `~/.config/goodbyedpi-turkey/config.json`). These per-user files keep `/opt` read-only. To remove the installed GUI:

```bash
sudo packaging/linux/uninstall.sh
```

The uninstaller preserves user settings and SpoofDPI.

### Build and test

Windows: create `venv` with `py -m venv venv`, then run `build.bat`. The executable is `dist\GoodbyeDPI-Turkey.exe`. The script uses pinned versions in `requirements.txt` and bundles `bin/`.

Linux: run the commands above through `./build_linux.sh`. This produces a PyInstaller `--onedir` application in `dist/goodbyedpi-turkey/`.

Logic tests (no GUI or engine required):

```bash
python -m unittest discover -s tests -v
```

For a Windows shutdown check: run the built EXE as Administrator, select **ACTIVATE**, close the window to tray, then select tray **Quit** without pressing **DEACTIVATE**. Confirm the app exits, `goodbyedpi.exe` is absent in Task Manager or `tasklist`, and no `_MEI` cleanup warning appears. Repeat while inactive and after an unexpected engine exit.

For a Linux desktop check: install the GUI and pinned engine, launch `goodbyedpi-turkey` from the application menu and terminal, activate, set the browser proxy to `127.0.0.1:8080`, then Quit from tray. Confirm `pgrep -af spoofdpi` shows no remaining child. Test your desktop's autostart and tray behavior, especially on KDE/Wayland.

### Credits

GUI: [MacallanTheRoot](https://github.com/MacallanTheRoot). Windows engine: [cagritaskn/GoodbyeDPI-Turkey](https://github.com/cagritaskn/goodbyedpi-turkey). Linux engine: [SpoofDPI](https://github.com/xvzc/SpoofDPI). See `bin/licenses/` for bundled Windows engine licenses and [LICENSE](LICENSE) for this project.

## Türkçe

### Windows

1. Projenin Releases sayfasından `GoodbyeDPI-Turkey.exe` dosyasını indirin veya aşağıdaki adımlarla derleyin.
2. Yönetici olarak çalıştırın. GoodbyeDPI, WinDivert sürücüsünü kullandığı için Windows UAC izni isteyebilir.
3. DNS sağlayıcısını seçip **ACTIVATE** düğmesine basın. Durdurmak için **DEACTIVATE** kullanın.

Pencereyi kapatmak uygulamayı sistem tepsisine gizler. Windows'ta tepsi simgesine sol tık pencereyi açar; sağ tık **Show** ve **Quit** menüsünü gösterir. **Quit**, GoodbyeDPI işlemini durdurup sonlandırılmasını bekler, kaynakları kapatır ve uygulamadan çıkar. Önceden **DEACTIVATE** düğmesine basmanız gerekmez. Windows sürümü PyInstaller `--onefile` olarak paketlenir.

**Run on startup**, `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup` içine bir kısayol oluşturur. Oturum açılışında yine yönetici izni istenebilir. Ayarlar `%APPDATA%\GoodbyeDPI-Turkey\config.json` konumundadır.

### Debian / Kali Linux

Arayüz `/opt/goodbyedpi-turkey/` konumuna kurulur. Terminal komutu `/usr/local/bin/goodbyedpi-turkey`, uygulama menüsü kaydı `/usr/share/applications/` konumundadır. Kurulum için `sudo` gerekir; **arayüzü normal masaüstü kullanıcısı olarak çalıştırın**. Yerel proxy için root gerekmez.

```bash
sudo apt install python3 python3-venv python3-tk
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./build_linux.sh
sudo packaging/linux/install.sh
goodbyedpi-turkey
```

SpoofDPI ayrıca kurulmalıdır. Denenen sürüm, incelenebilir [v0.12.0 kaynak etiketi](https://github.com/xvzc/SpoofDPI/tree/v0.12.0) üzerindendir. Go 1.21 veya üstü ile sabit sürümü kullanıcı hesabınızda derleyin:

```bash
go install github.com/xvzc/SpoofDPI/cmd/spoofdpi@v0.12.0
~/go/bin/spoofdpi -help
```

Arayüz `spoof-dpi` veya `spoofdpi` dosyasını `PATH`, `~/go/bin`, `~/.spoof-dpi/bin`, `/usr/local/bin` ve `/opt/goodbyedpi-turkey/bin` konumlarında arar. Bulamazsa **ACTIVATE** açık bir hata gösterir. Kurulum betiği uzaktan kabuk betiği indirip çalıştırmaz. İkili dosya kuracaksanız kaynağı ve sağlama toplamını inceleyin.

Linux'ta **ACTIVATE**, `127.0.0.1:8080` adresinde SpoofDPI proxy'sini başlatır. Tarayıcınızı bu HTTP proxy'sini kullanacak şekilde ayarlayın. Seçilen DNS adresi SpoofDPI'ye aktarılır; Linux DNS-over-HTTPS davranışı Windows GoodbyeDPI DNS yönlendirmesiyle aynı değildir. DNS portu seçimi yalnızca Windows'ta kullanılır. Uygulama sistem proxy ayarlarını değiştirmez. Pencere kapatılınca desteklenen masaüstlerinde tepsiye gizlenir; KDE/Wayland üzerinde AppIndicator uyumlu tepsi gerekebilir. Tam çıkış için tepsideki **Quit** komutunu kullanın.

**Run on startup**, `$XDG_CONFIG_HOME/autostart/goodbyedpi-turkey.desktop` (veya `~/.config/autostart/...`) dosyasını oluşturur. Ayarlar `$XDG_CONFIG_HOME/goodbyedpi-turkey/config.json` (veya `~/.config/goodbyedpi-turkey/config.json`) dosyasındadır. `/opt` normal kullanıcılar için salt okunur kalır. Kaldırmak için:

```bash
sudo packaging/linux/uninstall.sh
```

Kaldırıcı kullanıcı ayarlarını ve SpoofDPI'yi korur.

### Derleme ve test

Windows'ta `py -m venv venv` çalıştırın, ardından `build.bat` kullanın. EXE `dist\GoodbyeDPI-Turkey.exe` konumunda oluşur. Linux'ta yukarıdaki `./build_linux.sh` komutu `dist/goodbyedpi-turkey/` dizinini üretir.

```bash
python -m unittest discover -s tests -v
```

Windows'ta yönetici olarak EXE'yi açın, **ACTIVATE** yapın, pencereyi tepsiye gizleyin ve **DEACTIVATE** yapmadan **Quit** seçin. Uygulamanın ve `goodbyedpi.exe` işleminin kapandığını, `_MEI` temizleme uyarısı olmadığını kontrol edin. Linux'ta menüden ve terminalden açılışı, tarayıcı proxy'sini, tepsiden çıkışı ve `pgrep -af spoofdpi` sonucunu kontrol edin. KDE/Wayland tepsi ve otomatik başlatmayı ayrıca deneyin.

### Katkılar

Arayüz: [MacallanTheRoot](https://github.com/MacallanTheRoot). Windows motoru: [cagritaskn/GoodbyeDPI-Turkey](https://github.com/cagritaskn/goodbyedpi-turkey). Linux motoru: [SpoofDPI](https://github.com/xvzc/SpoofDPI). Lisanslar için `bin/licenses/` ve [LICENSE](LICENSE) dosyalarına bakın.
