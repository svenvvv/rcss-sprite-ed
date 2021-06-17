# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'editAbYuff.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(251, 136)
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.nameEdit = QLineEdit(Dialog)
        self.nameEdit.setObjectName(u"nameEdit")

        self.gridLayout.addWidget(self.nameEdit, 0, 1, 1, 3)

        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.xPosEdit = QLineEdit(Dialog)
        self.xPosEdit.setObjectName(u"xPosEdit")

        self.gridLayout.addWidget(self.xPosEdit, 1, 1, 1, 1)

        self.label_4 = QLabel(Dialog)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 1, 2, 1, 1)

        self.yPosEdit = QLineEdit(Dialog)
        self.yPosEdit.setObjectName(u"yPosEdit")

        self.gridLayout.addWidget(self.yPosEdit, 1, 3, 1, 1)

        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)

        self.widthEdit = QLineEdit(Dialog)
        self.widthEdit.setObjectName(u"widthEdit")

        self.gridLayout.addWidget(self.widthEdit, 2, 1, 1, 1)

        self.label_5 = QLabel(Dialog)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 2, 2, 1, 1)

        self.heightEdit = QLineEdit(Dialog)
        self.heightEdit.setObjectName(u"heightEdit")

        self.gridLayout.addWidget(self.heightEdit, 2, 3, 1, 1)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 4)

        QWidget.setTabOrder(self.nameEdit, self.xPosEdit)
        QWidget.setTabOrder(self.xPosEdit, self.yPosEdit)
        QWidget.setTabOrder(self.yPosEdit, self.widthEdit)
        QWidget.setTabOrder(self.widthEdit, self.heightEdit)

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Edit sprite", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Name", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Position", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"x", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"Width/height", None))
        self.label_5.setText(QCoreApplication.translate("Dialog", u"x", None))
    # retranslateUi


