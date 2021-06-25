import Myth.Util

from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

from Myth.Commands import CommandSetProperty


class PropertiesModel(QAbstractTableModel):
    def __init__(self, *args, obj, **kwargs):
        super(PropertiesModel, self).__init__(*args, **kwargs)
        self._obj = obj
        self._win = Myth.Util.getMainWindow()

    def data(self, index, role):
        prop = self._obj._properties[index.row()]
        if role == Qt.DisplayRole:
            if index.column() == 1:
                if prop.type != bool:
                    val = prop.getter()
                    return val
            else:
                return prop.name
        elif role == Qt.CheckStateRole:
            if index.column() == 1:
                val = prop.getter()
                if prop.type == bool:
                    if val:
                        return Qt.Checked
                    else:
                        return Qt.Unchecked

    def setData(self, index, value, role):
        if index.column() != 1:
            return False

        if isinstance(value, str) and len(value) == 0:
            return False

        prop = self._obj._properties[index.row()]
        v = prop.type(value)
        self._win.createCommand(CommandSetProperty, prop.setter, v, prop.getter(), prop.name)

        return True

    def flags(self, index):
        ret = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if index.column() == 1:
            prop = self._obj._properties[index.row()]

            if prop.setter:
                ret |= Qt.ItemIsEditable

            if prop.type == bool:
                ret |= Qt.ItemIsUserCheckable

            return ret
        else:
            return ret

    def rowCount(self, index):
        return len(self._obj._properties)

    def columnCount(self, index):
        return 2
