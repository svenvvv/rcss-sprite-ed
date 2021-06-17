#!/bin/python3

from PySide2 import QtCore, QtWidgets, QtPrintSupport, QtGui
from PySide2.QtGui import QColor, QBrush, QPen, QPainter, QPaintEvent
from PySide2.QtCore import Qt, QRect, QPoint

from Myth.Sprite import Sprite
from Myth.ImageSelect import ImageSelect

class ImageViewer(QtWidgets.QMainWindow):
    sprites = []
    def __init__(self):
        super(ImageViewer, self).__init__()

        self.printer = QtPrintSupport.QPrinter()
        self.scaleFactor = 0.0

        self.imageLabel = ImageSelect()
        self.imageLabel.setSizePolicy(QtWidgets.QSizePolicy.Ignored,
                QtWidgets.QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.imageLabel.rectSelected.connect(lambda r: self.createSprite(r))
        self.imageLabel.paintFinished.connect(lambda p: self.paintSprites(p))
        self.imageLabel.contextMenu.connect(lambda p: self.showContextMenu(p))

        self.imageLabel.setMouseTracking(True)

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidget(self.imageLabel)
        self.setCentralWidget(self.scrollArea)

        self.menu = QtWidgets.QMenu(self)

        editAction = QtWidgets.QAction('Edit', self)
        self.menu.addAction(editAction)

        replaceAction = QtWidgets.QAction('Re-place', self)
        self.menu.addAction(replaceAction)

        deleteAction = QtWidgets.QAction('Delete', self)
        self.menu.addAction(deleteAction)

        self.createActions()
        self.createMenus()

        self.setWindowTitle("RCSS Spritesheet Editor")
        self.resize(500, 400)

    def repaint(self):
        self.imageLabel.update()

    def removeHighlight(self, spr):
        spr.highlight = False
        self.repaint()

    def showContextMenu(self, target):
        hit = None
        for spr in self.sprites:
            if spr.aabbTest(target):
                hit = spr
                break

        if hit:
            spr.highlight = True
            self.repaint()
            self.menu.aboutToHide.connect(lambda: self.removeHighlight(spr))
            # Show the popup at cursor position, not target pos
            self.menu.popup(QtGui.QCursor.pos())

    def paintSprites(self, painter):
        for spr in self.sprites:
            rect = spr.rect
            x = rect.x()
            y = rect.y()
            w = rect.width()
            h = rect.height()

            if spr.highlight:
                painter.setPen(QPen(Qt.red))
            else:
                painter.setPen(QPen(Qt.black))

            painter.drawRect(rect)

            # Draw diagonals
            painter.drawLine(x, y, x + w, y + h)
            painter.drawLine(x + w, y, x, y + h)

            text_fm = QtGui.QFontMetrics(painter.font())
            text_width = text_fm.width(spr.name)

            painter.drawText(x + w/2 - text_width/2, y + h/2, spr.name)

    def createSprite(self, r):
        spr = Sprite("aa", r)
        self.sprites.append(spr)
        print(self.sprites)

    def open(self):
        fileName,_ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File",
                QtCore.QDir.currentPath())
        if fileName:
            self.openFile(fileName)

    def openFile(self, fileName):
        image = QtGui.QImage(fileName)
        if image.isNull():
            QtWidgets.QMessageBox.information(self, "Image Viewer",
                    "Cannot load %s." % fileName)
            return

        self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(image))
        self.scaleFactor = 1.0

        self.printAct.setEnabled(True)
        self.fitToWindowAct.setEnabled(True)
        self.updateActions()

        if not self.fitToWindowAct.isChecked():
            self.imageLabel.adjustSize()

    def print_(self):
        dialog = QtWidgets.QPrintDialog(self.printer, self)
        if dialog.exec_():
            painter = QtWidgets.QPainter(self.printer)
            rect = painter.viewport()
            size = self.imageLabel.pixmap().size()
            size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.imageLabel.pixmap().rect())
            painter.drawPixmap(0, 0, self.imageLabel.pixmap())

    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.scrollArea.setWidgetResizable(fitToWindow)
        if not fitToWindow:
            self.normalSize()

        self.updateActions()

    def about(self):
        QtWidgets.QMessageBox.about(self, "About Image Viewer",
                "<p>The <b>Image Viewer</b> example shows how to combine "
                "QLabel and QScrollArea to display an image. QLabel is "
                "typically used for displaying text, but it can also display "
                "an image. QScrollArea provides a scrolling view around "
                "another widget. If the child widget exceeds the size of the "
                "frame, QScrollArea automatically provides scroll bars.</p>"
                "<p>The example demonstrates how QLabel's ability to scale "
                "its contents (QLabel.scaledContents), and QScrollArea's "
                "ability to automatically resize its contents "
                "(QScrollArea.widgetResizable), can be used to implement "
                "zooming and scaling features.</p>"
                "<p>In addition the example shows how to use QPainter to "
                "print an image.</p>")

    def createActions(self):
        self.openAct = QtWidgets.QAction("&Open...", self, shortcut="Ctrl+O",
                triggered=self.open)

        self.printAct = QtWidgets.QAction("&Print...", self, shortcut="Ctrl+P",
                enabled=False, triggered=self.print_)

        self.exitAct = QtWidgets.QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)

        self.zoomInAct = QtWidgets.QAction("Zoom &In (25%)", self,
                shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)

        self.zoomOutAct = QtWidgets.QAction("Zoom &Out (25%)", self,
                shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)

        self.normalSizeAct = QtWidgets.QAction("&Normal Size", self,
                shortcut="Ctrl+S", enabled=False, triggered=self.normalSize)

        self.fitToWindowAct = QtWidgets.QAction("&Fit to Window", self,
                enabled=False, checkable=True, shortcut="Ctrl+F",
                triggered=self.fitToWindow)

        self.aboutAct = QtWidgets.QAction("&About", self, triggered=self.about)

    def createMenus(self):
        self.fileMenu = QtWidgets.QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.viewMenu = QtWidgets.QMenu("&View", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)

        self.helpMenu = QtWidgets.QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.helpMenu)

    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())

    def scaleImage(self, factor):
        self.scaleFactor *= factor
        # self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())
        self.imageLabel.setScale(self.scaleFactor)

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

        self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
        self.zoomOutAct.setEnabled(self.scaleFactor > 0.333)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                                + ((factor - 1) * scrollBar.pageStep()/2)))


if __name__ == '__main__':

    import sys

    app = QtWidgets.QApplication(sys.argv)
    imageViewer = ImageViewer()
    imageViewer.openFile("/home/admin/projects/mythos/data/gui/invader.png")
    imageViewer.show()
    sys.exit(app.exec_())
