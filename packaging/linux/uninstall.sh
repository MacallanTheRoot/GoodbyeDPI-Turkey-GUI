#!/usr/bin/env bash
set -euo pipefail
if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run this uninstaller with sudo." >&2
  exit 1
fi
if [[ "$(readlink /usr/local/bin/goodbyedpi-turkey 2>/dev/null || true)" == "/opt/goodbyedpi-turkey/goodbyedpi-turkey" ]]; then
  rm /usr/local/bin/goodbyedpi-turkey
fi
rm -f /usr/share/applications/goodbyedpi-turkey.desktop
rm -f /usr/share/icons/hicolor/128x128/apps/goodbyedpi-turkey.png
rm -rf /opt/goodbyedpi-turkey
echo "Application removed. Per-user settings and SpoofDPI were kept."
