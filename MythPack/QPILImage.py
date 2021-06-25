"""
    NOTE: importing this file will nuke PIL from modules.
        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        !!! Do not use when you intend to use PIL !!!
        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
"""
import sys

from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *


try:
    del sys.modules["PIL"]
except KeyError:
    # Gobble up the error if we never had PIL in the first place
    pass

sys.modules["PIL"] = sys.modules[__name__]


class Image:
    """
    Implements a minimal subset of PIL.Image used by PyTexturePacker.
    """

    ROTATE_270 = 1

    def __init__(self, image):
        self._img = image

    def close(self):
        pass

    def copy(self):
        return Image(self._img.copy())

    def transpose(self, method):
        raise RuntimeError("Transpose unimplemented")

    def crop(self, bbox=None):
        if not bbox:
            # NOTE: this is what PIL does. Probably an old-but-cant-remove method :)
            return self.copy()
        raise RuntimeError("Bbox crop unimplemented")

    def paste(self, image, rect):
        painter = QPainter(self._img)

        # NOTE from Pillow docs: If a 4-tuple is given, the size of the pasted image
        # must match the size of the region. So just blit by x,y coords.
        painter.drawImage(rect[0], rect[1], image.getQImage())

        painter.end()

    def getQImage(self):
        return self._img

    @property
    def size(self):
        qsize = self._img.size()
        return (qsize.width(), qsize.height())

    @staticmethod
    def open(filename):
        return Image(QImage(filename))

    @staticmethod
    def pilColorToQt(col):
        # swap BGRA to ARGB
        r = (col >> 24) & 0xFF
        g = (col >> 16) & 0xFF
        b = (col >> 8) & 0xFF
        a = (col) & 0xFF
        return QColor(r, g, b, a)

    @staticmethod
    def new(mode, size, bg=None):
        fmt = None
        if mode == "RGBA":
            fmt = QImage.Format_ARGB32_Premultiplied
        else:
            raise RuntimeError("Unhandled image format, add it ;)")

        qimg = QImage(size[0], size[1], fmt)
        qimg.fill(Qt.transparent);

        if bg:
            c = Image.pilColorToQt(bg)
            qimg.fill(c)

        return Image(qimg)
