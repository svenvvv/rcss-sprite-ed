from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

from Myth.Models.SpriteListModel import *

class SpritesheetListModel(QAbstractListModel):
    _selected = None

    def __init__(self, *args, sheets=[], **kwargs):
        super(SpritesheetListModel, self).__init__(*args, **kwargs)
        self._sheets = sheets

    def data(self, index, role):
        if role == Qt.DisplayRole:
            ss = self._sheets[index.row()]
            return ss.name()

    def rowCount(self, index):
        return len(self._sheets)

    def getSheetListModel(self, sheetName):
        for s in self._sheets:
            if s.name() == sheetName:
                return SpriteListModel(sprites=s.sprites(), sheet=s)

    def setSheetImage(self, sheet, image):
        sheet.setSource(image)

    def getSheetImage(self, sheetName=None):
        if sheetName is None:
            sheetName = self._selected.name()

        for s in self._sheets:
            if s.name() == sheetName:
                return f"{s.basepath()}/{s.source()}"

    def sheets(self):
        return self._sheets

    def selected(self):
        return self._selected

    def setSelectedByName(self, sheetName):
        for s in self._sheets:
            if s.name() == sheetName:
                self._selected = s
                return True
        return False

    def clearSelection(self):
        self._selected = None
