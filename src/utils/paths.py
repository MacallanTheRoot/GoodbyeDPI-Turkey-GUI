"""Locations shared by source, frozen Windows, and installed Linux builds."""
import os
import sys
from pathlib import Path


def resource_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]


def resource_path(*parts: str) -> Path:
    return resource_root().joinpath(*parts)


def config_dir(platform_name: str | None = None, environ=None, home=None) -> Path:
    platform_name = platform_name or sys.platform
    environ = os.environ if environ is None else environ
    home = Path.home() if home is None else Path(home)
    if platform_name == "win32":
        base = environ.get("APPDATA") or str(home / "AppData/Roaming")
        return Path(base) / "GoodbyeDPI-Turkey"
    base = environ.get("XDG_CONFIG_HOME") or str(home / ".config")
    return Path(base) / "goodbyedpi-turkey"
