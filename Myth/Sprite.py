from PySide2.QtCore import QRect

class Sprite:
    QListItemRef = None
    flippedW = False
    flippedH = False

    def __init__(self, name, x, y, w, h):
        self.name = name
        self.setSize(x, y, w, h)

    def setSize(self, x, y, w, h):
        # If the sprite would have negative w/h then
        # shift it into the positive for AABB testing
        if w < 0:
            x += w
            w = abs(w)
            self.flippedW = True
        if h < 0:
            y += h
            h = abs(h)
            self.flippedH = True
        self.rect = QRect(x, y, w, h)

    def aabbTest(self, p):
        rx = self.rect.x()
        ry = self.rect.y()
        rw = self.rect.width()
        rh = self.rect.height()
        px = p.x()
        py = p.y()

        if px > rx and py > ry and px < (rx + rw) and py < (ry + rh):
            return True
        return False

    def toRCSS(self):
        x = self.rect.x()
        y = self.rect.y()
        w = self.rect.width()
        h = self.rect.height()

        # NOTE: if we shifted the image during image loading then shift it back, as
        # otherwise mirrored images will be wrong in RmlUI.
        if self.flippedW:
            x -= w
            w = -w
        if self.flippedH:
            y += h
            h = -h

        return f"{self.name}: {x}px {y}px {w}px {h}px;"
