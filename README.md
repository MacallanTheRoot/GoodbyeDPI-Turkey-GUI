# GoodbyeDPI-Turkey GUI 🛡️

A modern, user-friendly, and secure interface for GoodbyeDPI, tailored for Turkey's network conditions.
**Developed by [MacallanTheRoot](https://github.com/MacallanTheRoot)**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![Version](https://img.shields.io/badge/version-1.0.0-green.svg)

## 🌟 Features

- **Modern UI**: Sleek, dark-themed interface built with `customtkinter`.
- **One-Click Privacy**: Activate reliable DPI circumvention with a single button.
- **Smart Persistence**: Remembers your preferred DNS provider and startup settings automatically.
- **System Tray Support**: Minimizes to tray to run silently in the background.
- **Secure Process Management**: Uses Windows Job Objects to ensure no background processes are left alive if the app closes.
- **DNS Options**: Pre-configured with popular, fast, and secure DNS providers:
  - Turkey DNSRedir (Recommended)
  - Yandex, Google, Cloudflare, OpenDNS

## 🚀 Installation & Usage

### Option 1: Standalone EXE (Recommended)
1. Download the latest `GoodbyeDPI-Turkey.exe` from releases.
2. Double-click to run. (Requires Administrator privileges to modify network settings).
3. Select your DNS provider and click **ACTIVATE**.

### Option 2: Run from Source
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

## 🛠️ Building (Developer)

To build a standalone `.exe` yourself:

1. Ensure you have the `venv` setup as above.
2. Double-click **`build.bat`**.
3. The executable will be generated in the `dist/` folder.

## 🤝 Credits

- **GUI & Logic**: Developed by [MacallanTheRoot](https://github.com/MacallanTheRoot).
- **Core Engine**: Powered by [cagritaskn/GoodbyeDPI-Turkey](https://github.com/cagritaskn/goodbyedpi-turkey).

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
