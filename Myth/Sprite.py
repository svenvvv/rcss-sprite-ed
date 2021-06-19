from PySide2.QtCore import QRect

class Sprite(QRect):
    QListItemRef = None
    flippedW = False
    flippedH = False

    def __init__(self, name, x, y, w, h):
        super().__init__()

        self._name = name
        self.setSize(x, y, w, h)

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name
        if self.QListItemRef:
            self.QListItemRef.setText(self._name)

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
        self.setX(x)
        self.setY(y)
        self.setWidth(w)
        self.setHeight(h)

    def aabbTest(self, p):
        rx = self.x()
        ry = self.y()
        rw = self.width()
        rh = self.height()
        px = p.x()
        py = p.y()

        if px > rx and py > ry and px < (rx + rw) and py < (ry + rh):
            return True
        return False

    def toRCSS(self):
        x = self.x()
        y = self.y()
        w = self.width()
        h = self.height()

        # NOTE: if we shifted the image during image loading then shift it back, as
        # otherwise mirrored images will be wrong in RmlUI.
        if self.flippedW:
            w = -w
            x -= w
        if self.flippedH:
            h = -h
            y -= h

        return f"{self.name()}: {x}px {y}px {w}px {h}px;"
