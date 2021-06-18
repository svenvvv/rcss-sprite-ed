from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import QUiLoader

# Class UiLoader was found online.
# Slightly modified to make load_ui() a static method.
# Posted by Andy Davis on 3 Oct 2017.
# Source: https://robonobodojo.wordpress.com/2017/10/03/loading-a-pyside-ui-via-a-class/
class UiLoader(QUiLoader):
    def __init__(self, base_instance):
        QUiLoader.__init__(self, base_instance)
        self.base_instance = base_instance

    def createWidget(self, class_name, parent=None, name=''):
        if parent is None and self.base_instance:
            return self.base_instance
        else:
            # create a new widget for child widgets
            widget = QUiLoader.createWidget(self, class_name, parent, name)
            if self.base_instance:
                setattr(self.base_instance, name, widget)
            return widget

    @staticmethod
    def load_ui(file, base_instance=None):
        loader = UiLoader(base_instance)
        widget = loader.load(file)
        QMetaObject.connectSlotsByName(widget)
        return widget
