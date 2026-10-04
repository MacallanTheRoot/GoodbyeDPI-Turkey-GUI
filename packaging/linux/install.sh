#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "$0")/../.." && pwd)"
destdir="${DESTDIR:-}"
destdir="${destdir%/}"
if [[ -n "$destdir" && "$destdir" != /* ]]; then
  echo "DESTDIR must be an absolute path." >&2; exit 1
fi
if [[ -z "$destdir" && "$(id -u)" -ne 0 ]]; then
  echo "Run this installer with sudo; the installed GUI runs as your user." >&2; exit 1
fi
if [[ -z "$destdir" ]] && command -v dpkg-query >/dev/null &&
   [[ "$(dpkg-query -W -f='${Status}' goodbyedpi-turkey 2>/dev/null || true)" == "install ok installed" ]]; then
  echo "The Debian package owns this app; use apt to manage it." >&2; exit 1
fi

bundle="$repo_dir/dist/goodbyedpi-turkey"
appdir="$destdir/opt/goodbyedpi-turkey"
launcher="$destdir/usr/local/bin/goodbyedpi-turkey"
desktop="$destdir/usr/share/applications/goodbyedpi-turkey.desktop"
icon="$destdir/usr/share/icons/hicolor/128x128/apps/goodbyedpi-turkey.png"
marker="$appdir/.goodbyedpi-turkey-install"
if [[ ! -x "$bundle/goodbyedpi-turkey" || ! -d "$bundle/_internal" || ! -f "$bundle/_internal/assets/icon.png" ]]; then
  echo "Complete Qt onedir build missing. Run ./build_linux.sh first." >&2; exit 1
fi
if [[ -e "$appdir" || -L "$appdir" ]] && [[ -L "$appdir" || ! -f "$marker" ]]; then
  echo "Refusing to replace an unrecognized /opt tree: $appdir" >&2; exit 1
fi
if [[ -e "$launcher" || -L "$launcher" ]] &&
   [[ "$(readlink "$launcher" 2>/dev/null || true)" != "/opt/goodbyedpi-turkey/goodbyedpi-turkey" ]]; then
  echo "Refusing to replace unrelated launcher: $launcher" >&2; exit 1
fi
if [[ ! -f "$marker" ]]; then
  for path in "$desktop" "$icon"; do
    if [[ -e "$path" || -L "$path" ]]; then
      echo "Refusing to replace unrelated file: $path" >&2; exit 1
    fi
  done
fi

install -d -m 755 "$destdir/opt" "$destdir/usr/local/bin" \
  "$destdir/usr/share/applications" "$destdir/usr/share/icons/hicolor/128x128/apps"
if [[ -f "$marker" ]]; then
  rm -rf -- "$appdir"
fi
install -d -m 755 "$appdir"
cp -a "$bundle/." "$appdir/"
chmod -R u=rwX,go=rX "$appdir"
printf 'GoodbyeDPI Turkey onedir\n' > "$marker"
chmod 644 "$marker"
if [[ -z "$destdir" ]]; then
  chown -R root:root "$appdir"
fi
ln -sfn /opt/goodbyedpi-turkey/goodbyedpi-turkey "$launcher"
install -m 644 "$repo_dir/packaging/linux/goodbyedpi-turkey.desktop" "$desktop"
install -m 644 "$repo_dir/assets/icon.png" "$icon"
echo "Installed. Launch as a normal user. Install SpoofDPI separately."
