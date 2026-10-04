# -*- mode: python ; coding: utf-8 -*-
"""Audited Linux Qt Widgets bundle; retain xcb, Wayland, tray and TLS plugins."""

from pathlib import Path
from subprocess import run

project_root = Path(SPECPATH).resolve().parents[1]

block_binary_names = {
    # The application supplies its own QPalette/QSS and runs on KDE. The GTK3
    # platform theme alone pulls in these libraries; readelf showed no retained
    # binary needs them after excluding libqgtk3.so.
    'libqgtk3.so', 'libgtk-3.so.0', 'libgdk-3.so.0',
    'libgdk_pixbuf-2.0.so.0', 'libglycin-2.so.0',
    # The host does not have libtiff.so.5; PNG is the app's packaged icon format.
    'libqtiff.so',
}


def retained(entry):
    return Path(entry[0]).name not in block_binary_names


def assert_no_missing_dependency(entries):
    removed = block_binary_names - {'libqtiff.so', 'libqgtk3.so'}
    for destination, source, _kind in entries:
        path = Path(source)
        if not path.is_file() or '.so' not in path.name:
            continue
        dynamic = run(['readelf', '-d', str(path)], capture_output=True, text=True, check=True).stdout
        for library in removed:
            if f'[{library}]' in dynamic:
                raise RuntimeError(f'{destination} still requires excluded {library}')


a = Analysis(
    [str(project_root / 'src/main.py')],
    pathex=[], binaries=[], datas=[(str(project_root / 'assets'), 'assets'),
                                   (str(project_root / 'LICENSE'), '.'),
                                   (str(project_root / 'THIRD_PARTY_NOTICES.md'), '.'),
                                   (str(project_root / 'packaging/licenses'), 'licenses')], hiddenimports=[],
    hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[],
    noarchive=False, optimize=0,
)
a.binaries = [item for item in a.binaries if retained(item)]
assert_no_missing_dependency(a.binaries)
# No Qt UI strings are translated; all app copy is English in this phase.
a.datas = [item for item in a.datas if not item[0].startswith('PySide6/Qt/translations/')]
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='goodbyedpi-turkey',
          debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
          console=False, disable_windowed_traceback=False)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False,
               name='goodbyedpi-turkey')
