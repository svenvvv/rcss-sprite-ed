from PySide2.QtCore import QRect

class Sprite:
    def __init__(self, name, rect):
        x = rect.x()
        y = rect.y()
        w = rect.width()
        h = rect.height()

        # If the sprite would have negative w/h then
        # shift it into the positive for AABB testing
        if w < 0:
            x += w
            w = abs(w)
        if h < 0:
            y += h
            h = abs(h)

        self.name = name
        self.rect = QRect(x, y, w, h)
        self.highlight = False

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
