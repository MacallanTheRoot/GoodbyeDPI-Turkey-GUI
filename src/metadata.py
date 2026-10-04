"""Single source of identity for the release candidate and package builders."""

APP_NAME = "GoodbyeDPI Turkey"
EXECUTABLE_NAME = "GoodbyeDPI-Turkey"
LINUX_COMMAND = "goodbyedpi-turkey"
DESKTOP_ID = "goodbyedpi-turkey.desktop"
PROJECT_URL = "https://github.com/MacallanTheRoot/GoodbyeDPI-Turkey-GUI"
ORGANIZATION = "MacallanTheRoot"
MAINTAINER = "macallantheroot <hamzaefesahinbas@protonmail.com>"

# v1.0.0 is an existing repository tag. Keep this successor explicitly pre-release.
VERSION = "1.0.1rc1"
DISPLAY_VERSION = f"v{VERSION}"
DEBIAN_VERSION = VERSION.replace("rc", "~rc")
WINDOWS_FILE_VERSION = tuple(int(part) for part in VERSION.split("rc")[0].split(".")) + (0,)
