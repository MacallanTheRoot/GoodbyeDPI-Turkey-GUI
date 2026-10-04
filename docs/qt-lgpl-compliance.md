# Qt / PySide6 source and relinking for v1.0.1-rc1

This release uses the community PySide6 Essentials and Shiboken6 **6.10.3**
packages under their LGPL-3.0-only option. The bundled Qt 6.10.3 libraries
are dynamically linked to the PySide6 bindings. No Qt or PySide6 source was
modified for this release. The application code is MIT licensed. The LGPL and
GPL license texts and component notices are in `packaging/licenses/` and
`THIRD_PARTY_NOTICES.md`; they are also packaged with the frozen application.

The GitHub release includes `GoodbyeDPI-Turkey-1.0.1rc1-third-party-source.zip`. It
contains the unmodified official 6.10.3 source archives and upstream SHA-256
files for `qtbase`, `qtsvg`, `qtimageformats`, `qtwayland`, and `pyside-setup`
(including the PySide6 bindings and Shiboken6). Those modules cover the Qt
libraries and plugins bundled by the Windows and Linux builds. The same
archive includes WinDivert v2.2.0 and GoodbyeDPI v0.2.3rc3 source. The
bundled GoodbyeDPI, WinDivert DLL and signed driver files match the official
GoodbyeDPI v0.2.3rc3-2 release byte for byte; the x64 WinDivert DLL also
matches the upstream WinDivert v2.2.0-C release. The release
also includes `GoodbyeDPI-Turkey-1.0.1rc1-windows-build-source.zip`, with the
application source, build scripts, specs, notices and license texts. These
release assets provide a distributor-controlled copy of the corresponding
library and application sources; an external source URL alone is not the
source provision for this release. The original archives and checksums come
from [Qt 6.10.3 submodule sources](https://download.qt.io/official_releases/qt/6.10/6.10.3/submodules/)
and [Qt for Python 6.10.3 source](https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-6.10.3-src/).

## Use a modified Qt library

The project places no restriction on reverse engineering for debugging a
modified LGPL library. Recipients may change Qt or PySide6, rebuild them from
the supplied sources, and run the application with the changed libraries.

- On Linux, unpack the portable archive and replace a compatible Qt shared
  library or plugin in `goodbyedpi-turkey/_internal/PySide6/Qt/`. Keep the
  library ABI and its dependencies compatible. Run the unpacked executable.
- On Windows, the onefile EXE extracts its libraries to a temporary directory
  at launch. The durable way to run modified Qt is to rebuild the open-source
  application: extract the build-source ZIP, create a Python environment, build
  PySide6/Shiboken6 and the needed Qt modules from the supplied 6.10.3 source,
  install those locally built wheels in that environment, then run `build.bat`.
  The build script uses `packaging/windows/goodbyedpi-turkey.spec`; it creates
  a new onefile EXE carrying the modified libraries. Install the required
  build dependencies from `requirements.txt` first, then replace the PySide6
  Essentials and Shiboken6 wheels with the locally built compatible wheels
  before invoking `build.bat`. The recipient can also run `src/main.py` from
  that environment without freezing it.

Qt's [LGPL obligations](https://www.qt.io/development/open-source-lgpl-obligations)
explain the source, relinking, execution and reverse-engineering rights.
For WinDivert, the Windows build source contains the unmodified DLL and
drivers as separate files. Recipients may replace a compatible DLL before
rebuilding the onefile EXE. Windows requires a valid signature or test mode
for a modified kernel driver; that platform requirement does not restrict
the LGPL rights granted for the library and driver source.

This document describes the concrete route for this release; the license
texts govern the recipient's rights.
