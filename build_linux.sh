#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
case "$(uname -m)" in
  x86_64|amd64) ;;
  *) echo "Linux builds currently support x86_64/amd64 only." >&2; exit 1 ;;
esac
if [[ ! -x .venv/bin/python ]]; then
  echo "Create .venv and install requirements.txt before building." >&2
  exit 1
fi
python_bin=".venv/bin/python"
if ! command -v readelf >/dev/null; then
  echo "binutils (readelf) is required to audit Qt bundle dependencies." >&2
  exit 1
fi
"$python_bin" -c 'import PyInstaller, PySide6.QtWidgets' || {
  echo "Build dependencies are missing in .venv; install requirements.txt." >&2
  exit 1
}
"$python_bin" -m PyInstaller --noconfirm --clean packaging/linux/goodbyedpi-turkey.spec
echo "Built dist/goodbyedpi-turkey. Install with sudo packaging/linux/install.sh"
