# 1.0.1rc1 release gates

Historical Phase 6A snapshot from 2026-10-04, before native Windows sign-off
and the Phase 6B compliance review. The later release notes, release assets and
GitHub Actions run provide the current RC evidence. The statuses below record
what was known at the end of Phase 6A.

| Gate | Status | Evidence / action |
| --- | --- | --- |
| Version consistency | DONE | `src/metadata.py` is the application version authority; Debian derives `1.0.1~rc1`; Windows resources use numeric tuple and string version. Desktop-entry `Version` is unrelated. |
| Unit and Qt tests | DONE | 56 tests passed headless after final changes. |
| Compile, shell syntax, desktop entry, pip check, diff whitespace | DONE | Final commands passed. |
| Linux clean onedir build | DONE | `./build_linux.sh`; measured bytes and warning in Phase 6A report. |
| Linux source and packaged live behavior | DONE | System/Light/Dark, minimized, tray restore, real SpoofDPI HTTPS HTTP 200, Disable, Quit; no orphan/port listener; KDE proxy unchanged. |
| Debian metadata, contents and extraction | DONE | `dpkg-deb --info`, `--contents`, temp extraction and path/mode checks. |
| Staged manual install/reinstall/uninstall | DONE | `DESTDIR` checks preserved unrelated file and per-user config. |
| Portable archive and checksums | DONE | Intended RC artifacts recorded in `dist/SHA256SUMS` and `dist/release-manifest.txt`. |
| README and release notes | DONE | English/Turkish README, `docs/release-notes-v1.0.1.md`, `CHANGELOG.md`. |
| Third-party inventory and notices | DONE | `THIRD_PARTY_NOTICES.md` and existing `bin/licenses/` notices. |
| LGPL distribution compliance review | BLOCKED | Confirm corresponding library source and modified-library use/relink path for Qt and WinDivert, especially the Windows onefile EXE. The current notices do not resolve that distribution question. |
| Windows source transfer ZIP | DONE | Deterministic ZIP of current working tree, built after docs/scripts. |
| CI workflow run | PENDING | Workflow defined; this unpushed tree has not run. |
| Native Windows PyInstaller build | PENDING | Run `build.bat` on real Windows and return EXE size/hash and build log. |
| Native Windows functional verification | PENDING | Complete `docs/windows-release-validation.md` and return result template. |
| Final version decision and clean committed tree | PENDING | After sign-off, decide whether to promote from RC and make reviewed commits. |
| Release tag, GitHub Release and artifact upload | PENDING | Phase 6B only. |

## Phase 6B sequence (do not execute in 6A)

1. Resolve LGPL distribution review and Windows defects, choose final version, update metadata/docs/artifact names, and rebuild all final artifacts and checksums.
2. Review whole diff, make logical commits, verify a clean tree, then push the reviewed branch. Run CI and inspect Ubuntu and Windows logs/artifacts.
3. Run or repeat native Windows sign-off against the exact final Windows artifact and record its SHA-256.
4. Once all gates pass, create and push the final tag, draft a GitHub Release with final notes, upload the `.deb`, portable Linux archive, Windows EXE and checksum manifest, then publish after inspecting the draft.
