#!/usr/bin/env bash
set -euo pipefail
repo_dir="$(cd "$(dirname "$0")/../.." && pwd)"
if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run this installer with sudo; the installed GUI runs as your user." >&2
  exit 1
fi
if [[ ! -x "$repo_dir/dist/goodbyedpi-turkey/goodbyedpi-turkey" ]]; then
  echo "Build first with ./build_linux.sh" >&2
  exit 1
fi
install -d -m 755 /opt/goodbyedpi-turkey /usr/share/applications /usr/share/icons/hicolor/128x128/apps
cp -a "$repo_dir/dist/goodbyedpi-turkey/." /opt/goodbyedpi-turkey/
chown -R root:root /opt/goodbyedpi-turkey
chmod -R go-w /opt/goodbyedpi-turkey
ln -sfn /opt/goodbyedpi-turkey/goodbyedpi-turkey /usr/local/bin/goodbyedpi-turkey
install -m 644 "$repo_dir/packaging/linux/goodbyedpi-turkey.desktop" /usr/share/applications/
install -m 644 "$repo_dir/assets/icon.png" /usr/share/icons/hicolor/128x128/apps/goodbyedpi-turkey.png
echo "Installed. Launch 'goodbyedpi-turkey' as a normal user. Install SpoofDPI separately."
