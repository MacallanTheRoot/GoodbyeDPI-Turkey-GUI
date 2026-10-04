#!/usr/bin/env bash
set -euo pipefail
repo_dir="$(cd "$(dirname "$0")/../.." && pwd)"
destdir="${DESTDIR:-}"
destdir="${destdir%/}"
if [[ -z "$destdir" && "$(id -u)" -ne 0 ]]; then
  echo "Run this installer with sudo; the installed GUI runs as your user." >&2
  exit 1
fi
if [[ ! -x "$repo_dir/dist/goodbyedpi-turkey/goodbyedpi-turkey" ]]; then
  echo "Build first with ./build_linux.sh" >&2
  exit 1
fi
install -d -m 755 "$destdir/opt/goodbyedpi-turkey" "$destdir/usr/local/bin" \
  "$destdir/usr/share/applications" "$destdir/usr/share/icons/hicolor/128x128/apps"
cp -a "$repo_dir/dist/goodbyedpi-turkey/." "$destdir/opt/goodbyedpi-turkey/"
if [[ -z "$destdir" ]]; then
  chown -R root:root /opt/goodbyedpi-turkey
fi
chmod -R go-w "$destdir/opt/goodbyedpi-turkey"
ln -sfn /opt/goodbyedpi-turkey/goodbyedpi-turkey "$destdir/usr/local/bin/goodbyedpi-turkey"
install -m 644 "$repo_dir/packaging/linux/goodbyedpi-turkey.desktop" "$destdir/usr/share/applications/"
install -m 644 "$repo_dir/assets/icon.png" "$destdir/usr/share/icons/hicolor/128x128/apps/goodbyedpi-turkey.png"
echo "Installed. Launch 'goodbyedpi-turkey' as a normal user. Install SpoofDPI separately."
