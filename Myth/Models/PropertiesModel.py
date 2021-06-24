from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

class PropertiesModel(QAbstractTableModel):
    def __init__(self, *args, obj, **kwargs):
        super(PropertiesModel, self).__init__(*args, **kwargs)
        self._obj = obj

    def data(self, index, role):
        if role == Qt.DisplayRole:
            props = self._obj._properties
            if index.column() == 1:
                return props[index.row()].getter()
            else:
                return props[index.row()].name

    def rowCount(self, index):
        return len(self._obj._properties)

    def columnCount(self, index):
        return 2
