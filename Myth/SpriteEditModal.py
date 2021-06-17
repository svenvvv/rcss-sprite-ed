from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from Myth.ui.SpriteEditModal import Ui_Dialog

class SpriteEditModal(QDialog):
    def __init__(self):
        super(SpriteEditModal, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)

        self.ui._exec()

    def accept(self):
        self.accept()

    def reject(self):
        self.close()
