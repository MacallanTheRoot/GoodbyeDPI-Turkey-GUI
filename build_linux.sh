#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m PyInstaller --noconfirm --clean --windowed --onedir \
  --name goodbyedpi-turkey \
  --collect-all customtkinter \
  --hidden-import pystray \
  --add-data "assets:assets" \
  src/main.py
echo "Built dist/goodbyedpi-turkey. Install with sudo packaging/linux/install.sh"
