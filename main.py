#!/bin/python3

from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

from Myth.MainWindow import MainWindow

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    app.setOrganizationName("svsoft")
    app.setApplicationName("rcssspriteed")

    editor = MainWindow()
    sys.exit(app.exec_())
