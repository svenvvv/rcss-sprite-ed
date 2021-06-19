from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from Myth.UiLoader import UiLoader

class SpriteEditModal(QDialog):
    def __init__(self, sprite=None, parent=None):
        QDialog.__init__(self)
        UiLoader.load_ui("ui/edit.ui", self)

        self.parent = parent

        if sprite:
            self.startName = sprite.name()
            self.startX = sprite.x()
            self.startY = sprite.y()
            self.startW = sprite.width()
            self.startH = sprite.height()

            self.sprite = sprite
            self.nameEdit.setText(sprite.name())
            self.xSpinBox.setValue(sprite.x())
            self.ySpinBox.setValue(sprite.y())
            self.widthSpinBox.setValue(sprite.width())
            self.heightSpinBox.setValue(sprite.height())

            self.nameEdit.textChanged.connect(lambda v: self._cb_change("name", v))
            self.xSpinBox.valueChanged.connect(lambda v: self._cb_change("x", v))
            self.ySpinBox.valueChanged.connect(lambda v: self._cb_change("y", v))
            self.widthSpinBox.valueChanged.connect(lambda v: self._cb_change("w", v))
            self.heightSpinBox.valueChanged.connect(lambda v: self._cb_change("h", v))

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.show()

    def _cb_change(self, prop, val):
        if prop == "name":
            self.sprite.setName(val)
        elif prop == "x":
            # NOTE: for both x and y edits reset the width/height as well, because otherwise
            # the rect gets smaller during x/y movement (even though the width/height are never
            # changed). I'm unsure if this is the correct way to cause a rect update, but it works.
            self.sprite.setX(val)
            self.sprite.setWidth(self.widthSpinBox.value())
        elif prop == "y":
            self.sprite.setY(val)
            self.sprite.setHeight(self.heightSpinBox.value())
        elif prop == "w":
            self.sprite.setWidth(val)
        elif prop == "h":
            self.sprite.setHeight(val)
        else:
            print(f"Unsupported prop: {e}")

        if self.parent:
            self.parent.repaint()

    def resetSprite(self):
        if self.sprite:
            self.sprite.setName(self.startName)
            self.sprite.setX(self.startX)
            self.sprite.setY(self.startY)
            self.sprite.setWidth(self.startW)
            self.sprite.setHeight(self.startH)

        if self.parent:
            self.parent.repaint()

    def accept(self):
        self.resetSprite()

        self.newValues = {
            "name": self.nameEdit.text(),
            "x": self.xSpinBox.value(),
            "y": self.ySpinBox.value(),
            "w": self.widthSpinBox.value(),
            "h": self.heightSpinBox.value()
        }

        self.done(1)

    def reject(self):
        self.resetSprite()
        self.done(0)
