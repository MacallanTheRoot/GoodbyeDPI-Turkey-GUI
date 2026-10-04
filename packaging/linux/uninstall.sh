#!/usr/bin/env bash
set -euo pipefail

destdir="${DESTDIR:-}"
destdir="${destdir%/}"
if [[ -n "$destdir" && "$destdir" != /* ]]; then
  echo "DESTDIR must be an absolute path." >&2; exit 1
fi
if [[ -z "$destdir" && "$(id -u)" -ne 0 ]]; then
  echo "Run this uninstaller with sudo." >&2; exit 1
fi
if [[ -z "$destdir" ]] && command -v dpkg-query >/dev/null &&
   [[ "$(dpkg-query -W -f='${Status}' goodbyedpi-turkey 2>/dev/null || true)" == "install ok installed" ]]; then
  echo "The Debian package owns this app; remove it with apt." >&2; exit 1
fi
appdir="$destdir/opt/goodbyedpi-turkey"
marker="$appdir/.goodbyedpi-turkey-install"
if [[ -e "$appdir" || -L "$appdir" ]] && [[ -L "$appdir" || ! -f "$marker" ]]; then
  echo "Refusing to remove an unrecognized /opt tree: $appdir" >&2; exit 1
fi
launcher="$destdir/usr/local/bin/goodbyedpi-turkey"
if [[ "$(readlink "$launcher" 2>/dev/null || true)" == "/opt/goodbyedpi-turkey/goodbyedpi-turkey" ]]; then
  rm -- "$launcher"
fi
if [[ -f "$marker" ]]; then
  rm -f -- "$destdir/usr/share/applications/goodbyedpi-turkey.desktop"
  rm -f -- "$destdir/usr/share/icons/hicolor/128x128/apps/goodbyedpi-turkey.png"
  rm -rf -- "$appdir"
fi
echo "Application removed. User configuration remains at ${XDG_CONFIG_HOME:-~/.config}/goodbyedpi-turkey; SpoofDPI was kept."
