import os

from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *


class CommandSetResolution(QUndoCommand):
    def __init__(self, mainwin, new):
        super().__init__()

        self.win = mainwin
        self.new = new
        self.prev = self.win.spritesList.model().sheet().resolution()

        if self.new != self.prev:
            self.win.undo.push(self)
        else:
            self.win.statusBar().showMessage("Old and new resolution are the same, ignoring")

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

        if os.path.basename(self.new) != self.prev:
            self.win.undo.push(self)
        else:
            self.win.statusBar().showMessage("Selected image has already been loaded, ignoring")

    def do(self, new):
        if self.win.loadImage(new):
            self.win.spritesList.model().sheet().setBasepath(os.path.dirname(new))
            self.win.spritesList.model().sheet().setSource(os.path.basename(new))
        else:
            print(f"Failed to load image {new}")

    def redo(self):
        self.do(self.new)

    def undo(self):
        self.do(self.prev)


class CommandCreateSprite(QUndoCommand):
    def __init__(self, mainwin, sprite):
        super().__init__()

        self.win = mainwin
        self.sprite = sprite

        self.win.undo.push(self)

    def redo(self):
        self.win.addSprite(self.sprite)
        self.win.repaint()
        self.win.statusBar().showMessage(f"Added sprite {self.sprite.name()}")

    def undo(self):
        self.win.deleteSprite(self.sprite)
        self.win.selectedSprite = None
        self.win.repaint()
        self.win.statusBar().showMessage(f"Deleted sprite {self.sprite.name()}")


class CommandDeleteSprite(QUndoCommand):
    def __init__(self, mainwin, sprite):
        super().__init__()

        self.win = mainwin
        self.sprite = sprite

        self.win.undo.push(self)

    def redo(self):
        self.win.deleteSprite(self.sprite)
        self.win.selectedSprite = None
        self.win.repaint()
        self.win.statusBar().showMessage(f"Deleted sprite {self.sprite.name()}")

    def undo(self):
        self.win.addSprite(self.sprite)
        self.win.repaint()
        self.win.statusBar().showMessage(f"Added sprite {self.sprite.name()}")


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

        self.win.undo.push(self)

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
