"""Create a reproducible source snapshot from the current working tree."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo
import hashlib
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from metadata import VERSION  # noqa: E402

ROOT_NAME = f"GoodbyeDPI-Turkey-{VERSION}-windows-build-source"
INCLUDE_DIRS = (".github", "assets", "bin", "docs", "packaging", "src", "tests", "tools")
INCLUDE_FILES = (".gitignore", "LICENSE", "README.md", "CHANGELOG.md",
                 "THIRD_PARTY_NOTICES.md", "requirements.txt", "build.bat",
                 "build_linux.sh", "run.cmd")
EXCLUDED_PARTS = {".git", ".venv", "venv", "build", "dist", "__pycache__",
                  ".pytest_cache", ".mypy_cache", ".ruff_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".deb", ".gz", ".zip", ".log"}


def files():
    candidates = [ROOT / name for name in INCLUDE_FILES]
    for name in INCLUDE_DIRS:
        candidates.extend((ROOT / name).rglob("*"))
    for path in sorted(candidates):
        relative = path.relative_to(ROOT)
        if (not path.is_file() or path.is_symlink() or
                EXCLUDED_PARTS.intersection(relative.parts) or
                path.suffix.lower() in EXCLUDED_SUFFIXES or
                "screenshot" in path.name.lower() or
                "secret" in path.name.lower() or
                "credential" in path.name.lower() or
                ".env" in path.name.lower()):
            continue
        yield path, relative


def main():
    output = ROOT / "dist" / f"{ROOT_NAME}.zip"
    output.parent.mkdir(exist_ok=True)
    included = list(files())
    if not included or not any(str(rel) == "build.bat" for _, rel in included):
        raise RuntimeError("Source inputs missing")
    with ZipFile(output, "w", ZIP_DEFLATED, compresslevel=9) as archive:
        for path, relative in included:
            info = ZipInfo(f"{ROOT_NAME}/{relative.as_posix()}", (1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = (0o100644 << 16)
            archive.writestr(info, path.read_bytes(), compress_type=ZIP_DEFLATED, compresslevel=9)
    with ZipFile(output) as archive:
        names = archive.namelist()
        if len(names) != len(included) or archive.testzip() is not None:
            raise RuntimeError("Archive verification failed")
        if any(any(part in EXCLUDED_PARTS for part in Path(name).parts) for name in names):
            raise RuntimeError("Excluded content in archive")
    print(f"{output}\n{output.stat().st_size} bytes\nSHA-256 {hashlib.sha256(output.read_bytes()).hexdigest()}\n{len(included)} files")


if __name__ == "__main__":
    main()
