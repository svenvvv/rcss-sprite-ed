import os
import Myth.Util

from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

class CommandError(ValueError):
    def __init__(self, message):
        super().__init__(message)


class CommandIgnored(ValueError):
    def __init__(self, message):
        super().__init__(message)


class CommandSetProperty(QUndoCommand):
    def __init__(self, setter, new, prev, propName=""):
        super().__init__()

        self.new = new
        self.prev = prev
        self.setter = setter
        self.win = Myth.Util.getMainWindow()

        self.propName = propName

        if self.new == self.prev:
            raise CommandIgnored("Old and new property are the same, ignoring")

    def redo(self):
        self.setter(self.new)
        self.win.statusBar().showMessage(f"Set property {self.propName} from {self.prev} to {self.new}")
        self.win.repaint()

    def undo(self):
        self.setter(self.prev)
        self.win.statusBar().showMessage(f"Set property {self.propName} from {self.prev} to {self.new}")
        self.win.repaint()


class CommandSetResolution(QUndoCommand):
    def __init__(self, mainwin, new):
        super().__init__()

        self.win = mainwin
        self.new = new
        self.prev = self.win.spritesList.model().sheet().resolution()

        if self.new == self.prev:
            raise CommandIgnored("Old and new resolution are the same, ignoring")

    def redo(self):
        self.win.spritesList.model().sheet().setResolution(self.new)
        self.win.statusBar().showMessage(f"Set resolution from {self.prev} to {self.new}")

    def undo(self):
        self.win.spritesList.model().sheet().setResolution(self.prev)
        self.win.statusBar().showMessage(f"Set resolution from {self.new} to {self.prev}")


class CommandSetImage(QUndoCommand):
    def __init__(self, mainwin, new):
        super().__init__()

        self.win = mainwin
        self.new = new
        self.prev = self.win.spritesList.model().sheet().sourceLongPath()

        if os.path.basename(self.new) == self.prev:
            raise CommandIgnored("Selected image has already been loaded, ignoring")

    def do(self, new):
        if self.win.loadImage(new):
            self.win.spritesList.model().sheet().setBasepath(os.path.dirname(new))
            self.win.spritesList.model().sheet().setSource(os.path.basename(new))
        else:
            raise CommandError(f"Failed to load image {new}")

    def redo(self):
        self.do(self.new)

    def undo(self):
        self.do(self.prev)


class CommandCreateSprite(QUndoCommand):
    def __init__(self, mainwin, sprite):
        super().__init__()

        self.win = mainwin
        self.sprite = sprite

        if self.win.spritesList.model().findDupes(sprite.name()):
            raise CommandError(f"Duplicate sprite name: {self.sprite.name()}")

    def redo(self):
        if self.win.spritesList.model().insertRow(self.sprite):
            self.win.repaint()
            self.win.statusBar().showMessage(f"Added sprite {self.sprite.name()}")
        else:
            QMessageBox.warning(self.win, self.win.windowTitle, f"Duplicate sprite name: {self.sprite.name()}")

    def undo(self):
        self.win.spritesList.model().removeRow(self.sprite)
        self.win.repaint()
        self.win.statusBar().showMessage(f"Deleted sprite {self.sprite.name()}")


class CommandDeleteSprite(QUndoCommand):
    def __init__(self, mainwin, sprite):
        super().__init__()

        self.win = mainwin
        self.sprite = sprite

    def redo(self):
        self.win.spritesList.model().removeRow(self.sprite)
        self.win.repaint()
        self.win.statusBar().showMessage(f"Deleted sprite {self.sprite.name()}")

    def undo(self):
        if self.win.spritesList.model().insertRow(self.sprite):
            self.win.repaint()
            self.win.statusBar().showMessage(f"Added sprite {self.sprite.name()}")
        else:
            QMessageBox.warning(self.win, self.win.windowTitle, f"Duplicate sprite name: {self.sprite.name()}")


class CommandModifySprite(QUndoCommand):
    def __init__(self, mainwin, sprite, x, y, w, h, name=None):
        super().__init__()

        self.win = mainwin
        self.sprite = sprite

        self.newName = name
        self.prevName = sprite.name()

        self.newSize = {
            "x": x,
            "y": y,
            "w": w,
            "h": h
        }

        self.oldSize = {
            "x": sprite.x(),
            "y": sprite.y(),
            "w": sprite.width(),
            "h": sprite.height()
        }

    def redo(self):
        self.sprite.setSize(**self.newSize)
        if self.newName:
            self.sprite.setName(self.newName)
        self.win.repaint()
        self.win.statusBar().showMessage(f"Modified sprite {self.sprite.name()}")

    def undo(self):
        self.sprite.setSize(**self.oldSize)
        self.sprite.setName(self.prevName)
        self.win.repaint()
        self.win.statusBar().showMessage(f"Un-modified sprite {self.sprite.name()}")

class CommandFlipSprite(QUndoCommand):
    def __init__(self, mainwin, sprite, axis):
        super().__init__()

        if axis not in [ "x", "y" ]:
            raise CommandError(f"Unsupported axis, expected x or y: {axis}")

        self.win = mainwin
        self.sprite = sprite
        self.axis = axis

    def flipAxis(self):
        if self.axis == "x":
            self.sprite.flipX()
        else:
            self.sprite.flipY()

        self.win.repaint()

    def redo(self):
        self.flipAxis()
        self.win.statusBar().showMessage(f"Flipped sprite {self.sprite.name()}")

    def undo(self):
        self.flipAxis()
        self.win.statusBar().showMessage(f"Un-flipped sprite {self.sprite.name()}")
