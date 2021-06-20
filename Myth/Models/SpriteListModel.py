from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *


class SpriteListModel(QAbstractListModel):
    _selected = None
    _redrawing = None

    def __init__(self, *args, sprites=[], sheet=None, **kwargs):
        super(SpriteListModel, self).__init__(*args, **kwargs)
        self._sheet = sheet
        self._sprites = sprites

    def data(self, index, role):
        if role == Qt.DisplayRole:
            ss = self._sprites[index.row()]
            return ss.name()

    def rowCount(self, index):
        return len(self._sprites)

    def sprites(self):
        return self._sprites

    def findDupes(self, name):
        dupes = filter(lambda s: s.name() == name, self._sprites)
        if len(list(dupes)) > 0:
            return True
        return False

    def insertRow(self, sprite):
        if self.findDupes(sprite.name()):
            return False

        l = len(self._sprites)
        self.beginInsertRows(QModelIndex(), l, l+1)
        self._sprites.append(sprite)
        self.endInsertRows()
        return True

    def removeRow(self, sprite):
        idx = self._sprites.index(sprite)
        self.beginRemoveRows(QModelIndex(), idx, idx)
        if self._selected == sprite:
            self._selected = None
        self._sprites.remove(sprite)
        self.endRemoveRows()

    def hitTest(self, pos):
        hit = []
        for spr in self._sprites:
            if spr.aabbTest(pos):
                hit.append(spr)
        return hit

    def selected(self):
        return self._selected

    def setSelected(self, sprite):
        self._selected = sprite

    def setSelectedByName(self, spriteName):
        for spr in self._sprites:
            if spr.name() == spriteName:
                self._selected = spr
                return True
        return False

    def clearSelection(self):
        self._selected = None

    def sheet(self):
        return self._sheet
