"""User-level autostart for Windows and freedesktop Linux desktops."""
import os
import subprocess
import sys
from pathlib import Path


def startup_path(platform_name=None, environ=None, home=None):
    platform_name = platform_name or sys.platform
    environ = os.environ if environ is None else environ
    home = Path.home() if home is None else Path(home)
    if platform_name == "win32":
        appdata = Path(environ.get("APPDATA") or home / "AppData/Roaming")
        return appdata / "Microsoft/Windows/Start Menu/Programs/Startup/GoodbyeDPI-Turkey GUI.lnk"
    config_home = Path(environ.get("XDG_CONFIG_HOME") or home / ".config")
    return config_home / "autostart/goodbyedpi-turkey.desktop"


def is_enabled():
    return startup_path().exists()


def _launch_command():
    if getattr(sys, "frozen", False):
        return sys.executable, "--minimized"
    executable = sys.executable
    if sys.platform == "win32":
        windowless = executable.replace("python.exe", "pythonw.exe")
        if Path(windowless).exists():
            executable = windowless
    return executable, f'"{Path(__file__).resolve().parents[1] / "main.py"}" --minimized'


def set_enabled(enabled: bool):
    path = startup_path()
    if not enabled:
        path.unlink(missing_ok=True)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    executable, arguments = _launch_command()
    if sys.platform == "win32":
        def quote(value):
            return "'" + str(value).replace("'", "''") + "'"
        script = (
            "$s=(New-Object -ComObject WScript.Shell).CreateShortcut(" + quote(path) + ");"
            "$s.TargetPath=" + quote(executable) + ";"
            "$s.Arguments=" + quote(arguments) + ";$s.Save()"
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", script], check=True)
    else:
        # The installed launch command is stable even when /opt is read-only.
        command = "goodbyedpi-turkey" if getattr(sys, "frozen", False) else f'"{executable}" {arguments.removesuffix(" --minimized")}'
        path.write_text(
            "[Desktop Entry]\nType=Application\nName=GoodbyeDPI Turkey\n"
            f"Exec={command} --minimized\nTerminal=false\n"
            "X-GNOME-Autostart-enabled=true\n", encoding="utf-8")
