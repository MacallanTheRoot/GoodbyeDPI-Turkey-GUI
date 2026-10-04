"""Regenerate the Windows ICO from the project's original PNG mark."""
import struct
import sys
from pathlib import Path

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, Qt
from PySide6.QtGui import QImage

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/icon.png"
TARGET = ROOT / "assets/icon.ico"
SIZES = (16, 24, 32, 48, 64, 128)


def main():
    source = QImage(str(SOURCE))
    if source.isNull():
        raise RuntimeError(f"Cannot load {SOURCE}")
    images = []
    for size in SIZES:
        scaled = source.scaled(size, size, Qt.AspectRatioMode.IgnoreAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
        data = QByteArray()
        buffer = QBuffer(data)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        if not scaled.save(buffer, "PNG"):
            raise RuntimeError(f"Cannot encode {size}px icon")
        images.append((size, bytes(data)))
    offset = 6 + 16 * len(images)
    with TARGET.open("wb") as target:
        target.write(struct.pack("<HHH", 0, 1, len(images)))
        for size, blob in images:
            target.write(struct.pack("<BBBBHHII", size, size, 0, 0, 1, 32,
                                     len(blob), offset))
            offset += len(blob)
        for _, blob in images:
            target.write(blob)
    print(TARGET)


if __name__ == "__main__":
    sys.exit(main())
