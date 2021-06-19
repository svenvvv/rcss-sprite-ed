
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

class CommandSetProp(QUndoCommand):
    def __init__(self, mainwin, dst, prop, new):
        super().__init__()

        self.win = mainwin
        self.dst = dst
        self.prop = prop
        self.new = new

        if isinstance(dst, dict):
            self.prev = dst[prop]
            self.setter = lambda d, p, v: d.update({ p: v })
        else:
            print(f"CommandSetProp unsupported type: {type(dst)}")
            raise

        if self.new != self.prev:
            self.win.undo.push(self)
        else:
            self.win.statusBar().showMessage("Old and new value are the same, ignoring")

    def redo(self):
        self.setter(self.dst, self.prop, self.new)
        self.win.statusBar().showMessage(f"Set {self.prop} from {self.prev} to {self.new}")

    def undo(self):
        self.setter(self.dst, self.prop, self.prev)
        self.win.statusBar().showMessage(f"Set {self.prop} from {self.new} to {self.prev}")

class CommandSetImage(QUndoCommand):
    def __init__(self, mainwin, new):
        super().__init__()

        self.win = mainwin
        self.new = new
        self.prev = self.win.css.props["src"]

        if os.path.basename(self.new) != self.prev:
            self.win.undo.push(self)
        else:
            self.win.statusBar().showMessage("Selected image has already been loaded, ignoring")

    def do(self, new):
        if self.win.loadImage(new):
            self.win.css.props["src"] = os.path.basename(new)
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

    def undo(self):
        self.win.deleteSprite(self.sprite)
        self.win.repaint()

class CommandDeleteSprite(QUndoCommand):
    def __init__(self, mainwin, sprite):
        super().__init__()

        self.win = mainwin
        self.sprite = sprite

        self.win.undo.push(self)

    def redo(self):
        self.win.deleteSprite(self.sprite)
        self.win.repaint()

    def undo(self):
        self.win.addSprite(self.sprite)
        self.win.repaint()


class CommandModifySprite(QUndoCommand):
    def __init__(self, mainwin, sprite, x, y, w, h, newname=None):
        super().__init__()

        self.win = mainwin
        self.sprite = sprite

        self.newName = newname
        self.prevName = sprite.name

        self.newSize = {
            "x": x,
            "y": y,
            "w": w,
            "h": h
        }

        self.oldSize = {
            "x": sprite.rect.x(),
            "y": sprite.rect.y(),
            "w": sprite.rect.width(),
            "h": sprite.rect.height()
        }

        self.win.undo.push(self)

    def redo(self):
        self.sprite.setSize(**self.newSize)
        if self.newName:
            self.sprite.name = self.newName
        self.win.repaint()

    def undo(self):
        self.sprite.setSize(**self.oldSize)
        self.sprite.name = self.prevName
        self.win.repaint()
