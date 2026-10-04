#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python_bin="python3"
if [[ -x .venv/bin/python ]]; then
  python_bin=".venv/bin/python"
fi
"$python_bin" -m PyInstaller --noconfirm --clean --windowed --onedir \
  --name goodbyedpi-turkey \
  --collect-all customtkinter \
  --hidden-import pystray \
  --hidden-import PIL._tkinter_finder \
  --add-data "assets:assets" \
  src/main.py
echo "Built dist/goodbyedpi-turkey. Install with sudo packaging/linux/install.sh"
