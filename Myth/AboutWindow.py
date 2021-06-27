from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from Myth.UiLoader import UiLoader
from Myth.Util import VERSION


class AboutWindow(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        UiLoader.load_ui("ui/about.ui", self)

        self.buttonBox.accepted.connect(lambda: self.done(1))

        self.versionLabel.setText(VERSION)

        self.show()
