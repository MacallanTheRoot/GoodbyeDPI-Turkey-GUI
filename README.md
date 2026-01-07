<div align="center">

# GoodbyeDPI-Turkey GUI 🛡️

**[English](#english)** | **[Türkçe](#türkçe)**

</div>

---

<br>

<a id="english"></a>
## 🇬🇧 English

A modern, user-friendly, and secure interface for GoodbyeDPI, tailored for Turkey's network conditions.
**Developed by [MacallanTheRoot](https://github.com/MacallanTheRoot)**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![Version](https://img.shields.io/badge/version-1.0.0-green.svg)

### 🌟 Features

- **Modern UI**: Sleek, dark-themed interface built with `customtkinter`.
- **One-Click Privacy**: Activate reliable DPI circumvention with a single button.
- **Smart Persistence**: Remembers your preferred DNS provider and startup settings automatically.
- **System Tray Support**: Minimizes to tray to run silently in the background.
- **Secure Process Management**: Uses Windows Job Objects to ensure no background processes are left alive if the app closes.
- **DNS Options**: Pre-configured with popular, fast, and secure DNS providers:
  - Turkey DNSRedir (Recommended)
  - Yandex, Google, Cloudflare, OpenDNS

### 🚀 Installation & Usage

#### Option 1: Standalone EXE (Recommended)
1. Download the latest `GoodbyeDPI-Turkey.exe` from releases.
2. Double-click to run. (Requires Administrator privileges to modify network settings).
3. Select your DNS provider and click **ACTIVATE**.

#### Option 2: Run from Source
1. Clone the repository:
   ```bash
   git clone https://github.com/MacallanTheRoot/GoodbyeDPI-Turkey-GUI.git
   cd GoodbyeDPI-Turkey-GUI
   ```
2. Create settings environment and install dependencies:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python src/main.py
   ```

### 🛠️ Building (Developer)

To build a standalone `.exe` yourself:

1. Ensure you have the `venv` setup as above.
2. Double-click **`build.bat`**.
3. The executable will be generated in the `dist/` folder.

### 🤝 Credits

- **GUI & Logic**: Developed by [MacallanTheRoot](https://github.com/MacallanTheRoot).
- **Core Engine**: Powered by [cagritaskn/GoodbyeDPI-Turkey](https://github.com/cagritaskn/goodbyedpi-turkey).

### 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<br>

<a id="türkçe"></a>
## 🇹🇷 Türkçe

GoodbyeDPI için Türkiye ağ koşullarına özel olarak hazırlanmış modern, kullanıcı dostu ve güvenli bir arayüz.
**Geliştirici: [MacallanTheRoot](https://github.com/MacallanTheRoot)**

![Lisans](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![Versiyon](https://img.shields.io/badge/version-1.0.0-green.svg)

### 🌟 Özellikler

- **Modern Arayüz**: `customtkinter` ile oluşturulmuş şık, karanlık temalı arayüz.
- **Tek Tıkla Gizlilik**: Tek bir düğme ile güvenilir DPI atlatmayı etkinleştirin.
- **Akıllı Hafıza**: Tercih ettiğiniz DNS sağlayıcısını ve başlangıç ayarlarını otomatik olarak hatırlar.
- **Sistem Tepsisi Desteği**: Arka planda sessizce çalışmak için sistem tepsisine küçülür.
- **Güvenli İşlem Yönetimi**: Uygulama kapandığında arka plan işlemlerinin açık kalmamasını sağlamak için Windows İş Nesneleri kullanır.
- **DNS Seçenekleri**: Popüler, hızlı ve güvenli DNS sağlayıcıları ile önceden yapılandırılmıştır:
  - Turkey DNSRedir (Önerilen)
  - Yandex, Google, Cloudflare, OpenDNS

### 🚀 Kurulum ve Kullanım

#### Seçenek 1: Tek Dosya EXE (Önerilen)
1. Sürümler (Releases) kısmından en son `GoodbyeDPI-Turkey.exe` dosyasını indirin.
2. Çalıştırmak için çift tıklayın. (Ağ ayarlarını değiştirmek için Yönetici izinleri gerektirir).
3. DNS sağlayıcınızı seçin ve **ACTIVATE** (Etkinleştir) düğmesine tıklayın.

#### Seçenek 2: Kaynak Koddan Çalıştırma
1. Depoyu klonlayın:
   ```bash
   git clone https://github.com/MacallanTheRoot/GoodbyeDPI-Turkey-GUI.git
   cd GoodbyeDPI-Turkey-GUI
   ```
2. Sanal ortamı oluşturun ve bağımlılıkları yükleyin:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Uygulamayı çalıştırın:
   ```bash
   python src/main.py
   ```

### 🛠️ Derleme (Geliştirici)

Kendi `.exe` dosyanızı oluşturmak için:

1. Yukarıdaki gibi `venv` kurulumunu yaptığınızdan emin olun.
2. **`build.bat`** dosyasına çift tıklayın.
3. Çalıştırılabilir dosya `dist/` klasöründe oluşturulacaktır.

### 🤝 Emeği Geçenler

- **Arayüz ve Mantık**: [MacallanTheRoot](https://github.com/MacallanTheRoot) tarafından geliştirilmiştir.
- **Çekirdek Motor**: [cagritaskn/GoodbyeDPI-Turkey](https://github.com/cagritaskn/goodbyedpi-turkey) tarafından desteklenmektedir.

### 📄 Lisans

Bu proje açık kaynaktır ve [MIT Lisansı](LICENSE) altındadır.
