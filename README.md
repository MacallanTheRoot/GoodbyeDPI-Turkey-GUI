# GoodbyeDPI Turkey

A PySide6 / Qt Widgets desktop controller for DPI circumvention. Windows runs the bundled GoodbyeDPI engine; Linux runs a separately installed SpoofDPI local HTTP proxy. The engines behave differently. The current source version is the `1.0.1rc1` release candidate, following the existing `v1.0.0` tag. [Qt/PySide6 source and relinking information](docs/qt-lgpl-compliance.md) accompanies the release.

## English

### Windows

1. Download `GoodbyeDPI-Turkey-1.0.1rc1-windows-x86_64.exe` from this project's Releases page, or build it using the instructions below.
2. Run the EXE. If needed, the app relaunches itself through one Windows UAC prompt because GoodbyeDPI uses WinDivert. A launch with `--minimized` keeps that argument after elevation.
3. Choose a DNS provider and select **Enable**. Select **Disable** to stop the engine.

Closing the window hides it in the system tray. On Windows, left-click the tray icon to restore the window; right-click opens **Show** and **Quit**. **Quit** stops and reaps GoodbyeDPI, closes its pipes, stops the tray, then exits. You do not need to deactivate first. The Windows build remains a PyInstaller `--onefile` executable; its engine is extracted under PyInstaller's temporary `_MEI...` directory while the app runs.

**Run on startup** creates a shortcut in `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`. Windows may prompt for elevation at each login. Configuration is stored in `%APPDATA%\GoodbyeDPI-Turkey\config.json`.

### Debian / Kali Linux

The manual installer puts the GUI in `/opt/goodbyedpi-turkey/`, a launcher in `/usr/local/bin`, a desktop entry in `/usr/share/applications/`, and an icon in `/usr/share/icons/hicolor/128x128/apps/`. The `.deb` uses `/usr/bin` for its launcher. Installation uses `sudo`; **run the GUI as your normal desktop user**. The local proxy needs no root privileges.

Build and install the GUI:

```bash
sudo apt install python3 python3-venv binutils
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python src/main.py  # source development launch
./build_linux.sh
sudo packaging/linux/install.sh
goodbyedpi-turkey
```

Alternatively, after `./build_linux.sh`, build and install the Debian/Kali package without root during the build:

```bash
packaging/debian/build_deb.sh
sudo apt install ./dist/goodbyedpi-turkey_1.0.1~rc1_amd64.deb
```

Use `sudo apt remove goodbyedpi-turkey` to remove a `.deb` installation. Use `sudo packaging/linux/uninstall.sh` for a manual installation. Do not mix the two installation methods. For a rootless manual layout check, run `DESTDIR="$(mktemp -d)" packaging/linux/install.sh` and inspect the staged `opt/` and `usr/` trees.

SpoofDPI is a separate upstream program. The Linux CLI integration targets the reviewable [SpoofDPI v0.12.0 source tag](https://github.com/xvzc/SpoofDPI/tree/v0.12.0); with Go 1.21 or newer, install that exact version as your user:

```bash
go install github.com/xvzc/SpoofDPI/cmd/spoofdpi@v0.12.0
~/go/bin/spoofdpi -help
```

The PySide6 / Qt Widgets GUI looks for `spoof-dpi` or `spoofdpi` in `PATH`, `~/.spoof-dpi/bin`, `~/go/bin`, `/usr/local/bin`, `/usr/bin`, and `/opt/goodbyedpi-turkey/bin`. If missing, **Enable** shows an actionable error. The installer does not fetch or execute a remote shell script. Review upstream source or a release and its checksum before installing a binary.

Linux packages currently support x86_64/amd64 only. Build the PyInstaller bundle on the target Debian/Kali generation; Linux frozen builds depend on the host's shared-library baseline. The application installer does not install SpoofDPI.

On Linux, **Enable** starts SpoofDPI v0.12.0's HTTP proxy on `127.0.0.1:8080`. Configure a browser to use that proxy. The selected DNS address **and port** are passed to SpoofDPI for standard DNS; the default choice uses `77.88.8.8:1253`. DoH is not enabled because these provider addresses are not all DoH endpoints. This is not Windows GoodbyeDPI DNS redirection. The app passes `-system-proxy=false` and leaves desktop proxy settings alone; SpoofDPI v0.12.0's system proxy implementation does not configure Linux desktops. The GUI runs as a normal user and cannot protect applications that do not use its proxy. Newer SpoofDPI versions may have different flags and are not yet supported. If you close the window, it hides to tray where supported; tray click behavior depends on the desktop backend. KDE/Wayland may require an AppIndicator compatible tray. Use the tray's **Quit** command for full cleanup.

**Run on startup** writes `$XDG_CONFIG_HOME/autostart/goodbyedpi-turkey.desktop` (or `~/.config/autostart/...`). Configuration is in `$XDG_CONFIG_HOME/goodbyedpi-turkey/config.json` (or `~/.config/goodbyedpi-turkey/config.json`). Both uninstall methods preserve user settings and SpoofDPI. The app does not change KDE or system proxy settings.

### Build and test

Windows: create `.venv` with `py -m venv .venv`, install `requirements.txt` with `.venv\Scripts\python -m pip install -r requirements.txt`, then run `build.bat`. The dedicated spec produces the GUI onefile executable at `dist\GoodbyeDPI-Turkey.exe` with the icon, version information, and both Windows engine architectures. Its manifest does not request administrator access; `src/main.py` performs the single `runas` relaunch.

Linux: `./build_linux.sh` produces the PyInstaller `--onedir` application in `dist/goodbyedpi-turkey/`. `packaging/debian/build_deb.sh` packages that exact tree. The Linux Qt image plugin analysis may warn about a missing host `libtiff.so.5`; the TIFF plugin is excluded from the final bundle because this app uses PNG assets. See [packaging validation](docs/packaging-rc.md).

Unit and headless Qt tests (no engine required):

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -m unittest discover -s tests -v
```

For native Windows sign-off, use the [build and validation steps](docs/windows-release-validation.md) and return the [result template](docs/windows-release-validation-result-template.md). Active Quit must leave no `goodbyedpi.exe`, WinDivert resource or `_MEI` cleanup warning. Linux mocks and CI builds do not replace this test.

For a Linux desktop check: install the GUI and pinned engine, launch `goodbyedpi-turkey` from the application menu and terminal, activate, set the browser proxy to `127.0.0.1:8080`, then Quit from tray. Confirm `pgrep -af spoofdpi` shows no remaining child. Test your desktop's autostart and tray behavior, especially on KDE/Wayland.

### Credits

GUI: [MacallanTheRoot](https://github.com/MacallanTheRoot). Windows engine: [cagritaskn/GoodbyeDPI-Turkey](https://github.com/cagritaskn/goodbyedpi-turkey). Linux engine: [SpoofDPI](https://github.com/xvzc/SpoofDPI). See `bin/licenses/` for bundled Windows engine licenses and [LICENSE](LICENSE) for this project.

## Türkçe

### Windows

1. Projenin Releases sayfasından `GoodbyeDPI-Turkey-1.0.1rc1-windows-x86_64.exe` dosyasını indirin veya aşağıdaki adımlarla derleyin.
2. EXE dosyasını açın. Gerekirse uygulama WinDivert için kendisini tek bir UAC istemiyle yönetici olarak yeniden başlatır. `--minimized` parametresi korunur.
3. DNS sağlayıcısını seçip **Enable** düğmesine basın. Durdurmak için **Disable** kullanın.

Pencereyi kapatmak uygulamayı sistem tepsisine gizler. Windows'ta tepsi simgesine sol tık pencereyi açar; sağ tık **Show** ve **Quit** menüsünü gösterir. **Quit**, GoodbyeDPI işlemini durdurup sonlandırılmasını bekler, kaynakları kapatır ve uygulamadan çıkar. Önceden **Disable** düğmesine basmanız gerekmez. Windows sürümü PyInstaller `--onefile` olarak paketlenir.

**Run on startup**, `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup` içine bir kısayol oluşturur. Oturum açılışında yine yönetici izni istenebilir. Ayarlar `%APPDATA%\GoodbyeDPI-Turkey\config.json` konumundadır.

### Debian / Kali Linux

Elle kurulum arayüzü `/opt/goodbyedpi-turkey/` konumuna, komutu `/usr/local/bin` içine, menü kaydını `/usr/share/applications/` içine ve simgeyi hicolor dizinine yerleştirir. `.deb` paketi komut için `/usr/bin` kullanır. Kurulum için `sudo` gerekir; **arayüzü normal masaüstü kullanıcısı olarak çalıştırın**. Yerel proxy için root gerekmez.

```bash
sudo apt install python3 python3-venv binutils
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python src/main.py  # kaynak koddan geliştirme açılışı
./build_linux.sh
sudo packaging/linux/install.sh
goodbyedpi-turkey
```

Alternatif `.deb` kurulumu (paketi oluşturmak için root gerekmez):

```bash
packaging/debian/build_deb.sh
sudo apt install ./dist/goodbyedpi-turkey_1.0.1~rc1_amd64.deb
```

`.deb` kurulumunu `sudo apt remove goodbyedpi-turkey`, elle kurulumu `sudo packaging/linux/uninstall.sh` ile kaldırın. İki yöntemi birlikte kullanmayın. Rootsuz dizin kontrolü için `DESTDIR="$(mktemp -d)" packaging/linux/install.sh` komutunu kullanın.

SpoofDPI ayrıca kurulmalıdır. Linux komut satırı entegrasyonu incelenebilir [v0.12.0 kaynak etiketini](https://github.com/xvzc/SpoofDPI/tree/v0.12.0) hedefler. Go 1.21 veya üstü ile sabit sürümü kullanıcı hesabınızda derleyin:

```bash
go install github.com/xvzc/SpoofDPI/cmd/spoofdpi@v0.12.0
~/go/bin/spoofdpi -help
```

PySide6 / Qt Widgets arayüzü `spoof-dpi` veya `spoofdpi` dosyasını `PATH`, `~/.spoof-dpi/bin`, `~/go/bin`, `/usr/local/bin`, `/usr/bin` ve `/opt/goodbyedpi-turkey/bin` konumlarında arar. Bulamazsa **Enable** açık bir hata gösterir. Kurulum betiği uzaktan kabuk betiği indirip çalıştırmaz. İkili dosya kuracaksanız kaynağı ve sağlama toplamını inceleyin.

Linux paketi şu anda yalnızca x86_64/amd64 mimarisini destekler. PyInstaller paketini hedef Debian/Kali sürümünde derleyin; Linux paketi derleme sistemindeki paylaşımlı kitaplık tabanına bağlıdır. Uygulama kurucusu SpoofDPI'yi kurmaz.

Linux'ta **Enable**, SpoofDPI v0.12.0 HTTP proxy'sini `127.0.0.1:8080` adresinde başlatır. Tarayıcınızı bu proxy'yi kullanacak şekilde ayarlayın. Seçilen DNS adresi **ve portu** SpoofDPI'ye standart DNS için aktarılır; varsayılan seçim `77.88.8.8:1253` kullanır. Tüm sağlayıcı adresleri DoH uç noktası olmadığı için DoH açılmaz. Bu, Windows GoodbyeDPI DNS yönlendirmesinden farklıdır. Uygulama `-system-proxy=false` parametresini kullanır ve masaüstü proxy ayarlarını değiştirmez; SpoofDPI v0.12.0'ın sistem proxy kodu Linux masaüstünü yapılandırmaz. Arayüz normal kullanıcı olarak çalışır; proxy'yi kullanmayan uygulamaları koruyamaz. Yeni SpoofDPI sürümlerinin parametreleri farklı olabilir ve henüz desteklenmez. Pencere kapatılınca desteklenen masaüstlerinde tepsiye gizlenir; KDE/Wayland üzerinde AppIndicator uyumlu tepsi gerekebilir. Tam çıkış için tepsideki **Quit** komutunu kullanın.

**Run on startup**, `$XDG_CONFIG_HOME/autostart/goodbyedpi-turkey.desktop` (veya `~/.config/autostart/...`) dosyasını oluşturur. Ayarlar `$XDG_CONFIG_HOME/goodbyedpi-turkey/config.json` (veya `~/.config/goodbyedpi-turkey/config.json`) dosyasındadır. Her iki kaldırma yöntemi kullanıcı ayarlarını ve SpoofDPI'yi korur. Uygulama KDE veya sistem proxy ayarlarını değiştirmez.

### Derleme ve test

Windows'ta `py -m venv .venv` çalıştırın, `.venv\Scripts\python -m pip install -r requirements.txt` ile bağımlılıkları kurun, ardından `build.bat` kullanın. Ayrı Windows spec dosyası simgeyi, sürüm bilgisini ve iki GoodbyeDPI mimarisini içeren `dist\GoodbyeDPI-Turkey.exe` tek dosyasını üretir. Manifest yönetici izni istemez; tek `runas` yeniden başlatmasını `src/main.py` yapar. Linux'ta `./build_linux.sh` onedir dizinini, `packaging/debian/build_deb.sh` aynı dizinden `.deb` paketini üretir. TIFF uyarısının açıklaması [paketleme doğrulamasında](docs/packaging-rc.md) bulunur.

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -m unittest discover -s tests -v
```

Yerel Windows doğrulaması için [derleme ve test adımlarını](docs/windows-release-validation.md) izleyip [sonuç şablonunu](docs/windows-release-validation-result-template.md) doldurun. Etkin durumdan **Quit**, `goodbyedpi.exe` işlemi veya WinDivert kaynağı bırakmamalı ve `_MEI` temizleme uyarısı vermemelidir. Kali üzerindeki testler yerel Windows testinin yerine geçmez. Linux'ta menüden ve terminalden açılışı, tarayıcı proxy'sini, tepsiden çıkışı ve `pgrep -af spoofdpi` sonucunu kontrol edin. KDE/Wayland tepsi ve otomatik başlatmayı ayrıca deneyin.

### Katkılar

Arayüz: [MacallanTheRoot](https://github.com/MacallanTheRoot). Windows motoru: [cagritaskn/GoodbyeDPI-Turkey](https://github.com/cagritaskn/goodbyedpi-turkey). Linux motoru: [SpoofDPI](https://github.com/xvzc/SpoofDPI). Lisanslar için `bin/licenses/` ve [LICENSE](LICENSE) dosyalarına bakın.
