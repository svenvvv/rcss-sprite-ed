from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

class PropertiesModel(QAbstractTableModel):
    def __init__(self, *args, obj, **kwargs):
        super(PropertiesModel, self).__init__(*args, **kwargs)
        self._obj = obj

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

        prop = self._obj._properties[index.row()]
        v = prop.type(value)
        prop.setter(v)
        return True

    def flags(self, index):
        ret = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if index.column() == 1:
            ret |= Qt.ItemIsEditable

            if self._obj._properties[index.row()].type == bool:
                ret |= Qt.ItemIsUserCheckable

            return ret
        else:
            return ret

    def rowCount(self, index):
        return len(self._obj._properties)

    def columnCount(self, index):
        return 2
