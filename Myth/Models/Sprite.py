from PySide2.QtCore import QRect


class Property:
    def __init__(self, name, getter, setter, type):
        self.name = name
        self.getter = getter
        self.setter = setter
        self.type = type


class Sprite(QRect):
    _flippedW = False
    _flippedH = False

    def __init__(self, name, x, y, w, h):
        super().__init__()

        self._name = name
        self.setSize(x, y, w, h)

        self._properties = [
            Property("x", self.x, self.setX, int),
            Property("y", self.y, self.setY, int),
            Property("width", self.width, self.setWidth, int),
            Property("height", self.height, self.setHeight, int)
        ]

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name

    def isFlippedX(self):
        return self._flippedW

    def isFlippedY(self):
        return self._flippedH

    def flipX(self):
        self._flippedW = not self._flippedW

    def flipY(self):
        self._flippedH = not self._flippedH

    def setSize(self, x, y, w, h):
        # If the sprite would have negative w/h then
        # shift it into the positive for AABB testing
        if w < 0:
            x += w
            w = abs(w)
            self._flippedW = True
        if h < 0:
            y += h
            h = abs(h)
            self._flippedH = True
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
        if self._flippedW:
            w = -w
            x -= w
        if self._flippedH:
            h = -h
            y -= h

        return f"{self.name()}: {x}px {y}px {w}px {h}px;"
