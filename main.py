#!/bin/python3

from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

from Myth.Sprite import Sprite
from Myth.ImageSelect import ImageSelect
from Myth.RCSSParser import RCSSParser
from Myth.SpriteEditModal import SpriteEditModal

class QListWidgetSprite(QListWidgetItem):
    def __init__(self, sprite):
        super().__init__(sprite.name)
        self.sprite = sprite

class ImageViewer(QMainWindow):
    curCss = None
    sprites = []
    editSprite = None
    windowTitle = "RCSS Spritesheet Editor"

    def __init__(self):
        super(ImageViewer, self).__init__()

        self.scaleFactor = 0.0

        self.imageLabel = ImageSelect()
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.dockWidget = QDockWidget(self)
        self.dockWidget.setWindowTitle("Sprites")
        self.dockWidgetContents = QWidget()
        self.gridLayout = QGridLayout(self.dockWidgetContents)

        self.spritesList = QListWidget(self.dockWidgetContents)
        self.spritesList.itemSelectionChanged.connect(self.handleSpriteSelectionChanged)
        self.spritesList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.spritesList.customContextMenuRequested.connect(self.createListEditMenu)

        self.gridLayout.addWidget(self.spritesList, 0, 0, 1, 1)

        self.dockWidget.setWidget(self.dockWidgetContents)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockWidget)

        self.imageLabel.rectSelected.connect(lambda r: self.createSprite(r))
        self.imageLabel.paintStarted.connect(self.paintSprites)
        self.imageLabel.contextMenu.connect(lambda p: self.showContextMenu(p))

        self.imageLabel.setMouseTracking(True)

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.imageLabel)
        self.setCentralWidget(self.scrollArea)

        self.createActions()
        self.createMenus()

        self.setWindowTitle(self.windowTitle)
        self.resize(640, 480)

        self.parseStylesheet("../../data/gui/invader.rcss")

    def handleSpriteSelectionChanged(self):
        sel = self.spritesList.selectedItems()
        if len(sel) > 0:
            self.selectSpriteFromList(sel[0])
        else:
            for s in self.sprites:
                s.highlight = False

    def parseStylesheet(self, filename):
        parser = RCSSParser()
        css = parser.parse_stylesheet_file(filename)

        if len(css.errors):
            print("Errors parsing stylesheets:")
            print(css.errors)

        spritesheets = list(filter(lambda r: r.at_keyword == "@spritesheet", css.rules))

        if len(spritesheets) > 1:
            QMessageBox.error(self, self.windowTitle,
                              f"File contained {len(spritesheets)} spritesheets, currently only one is supported")
            return

        for ss in spritesheets:
            self.curCss = ss
            for d in ss.declarations:
                it = QListWidgetSprite(d)
                self.spritesList.addItem(it)

                d.QListItemRef = it
                self.sprites.append(d)

    def writeStylesheet(self):
        ss = self.curCss

        print(f"@stylesheet {ss.name}")
        print("{")
        print(f"\tsrc: {ss.props['src']}")
        print(f"\tresolution: {ss.props['resolution']}x")

        for s in self.sprites:
            print(f"\t{s.toRCSS()}")
        print("}")

    def repaint(self):
        self.imageLabel.update()

    def selectSpriteFromList(self, item):
        ourSprite = self.findSpriteFromQItem(item)
        if ourSprite:
            for s in self.sprites:
                s.highlight = False
            ourSprite.highlight = True
            self.repaint()

    def findSpriteFromQItem(self, item):
        for s in self.sprites:
            if s.QListItemRef == item:
                return s

    def findSpriteByName(self, name):
        for s in self.sprites:
            if s.name == name:
                return s

    def createListEditMenu(self, pos):
        it = self.spritesList.selectedItems()[0]
        target = self.findSpriteFromQItem(it)
        self.spriteContextMenu(target, QCursor.pos())

    def createSelectSpriteContextMenu(self, pos, sprites):
        def selectSpriteFromCtx(act):
            self.editSprite = self.findSpriteByName(act.text())
            # NOTE: Pop up at cursor, because it feels better ;)
            self.ctxEditMenu.popup(QCursor.pos())

        menu = QMenu(self)
        menu.triggered.connect(selectSpriteFromCtx)

        for spr in sprites:
            act = QAction(spr.name, self)
            menu.addAction(act)

        menu.popup(pos)

    def spriteContextMenu(self, sprite, pos):
        self.editSprite = sprite
        self.ctxEditMenu.popup(pos)

    def showContextMenu(self, target):
        hit = []
        for spr in self.sprites:
            if spr.aabbTest(target):
                hit.append(spr)

        if len(hit) == 0:
            return

        # Show the popup at cursor position, not target pos
        pos = QCursor.pos()

        if len(hit) > 1:
            print("Multiple hits: ", hit)
            self.createSelectSpriteContextMenu(pos, hit)
            return

        selHit = hit[0]
        if selHit.QListItemRef:
            it = selHit.QListItemRef
            l = it.listWidget()
            l.setCurrentItem(it)
            self.spriteContextMenu(selHit, pos)
        else:
            QMessageBox.error(self, self.windowTitle, "Sprite is missing list ref!")

    def paintSprites(self, painter):
        if not self.drawRectsAct.isChecked():
            return

        for spr in self.sprites:
            rect = spr.rect
            x = rect.x()
            y = rect.y()
            w = rect.width()
            h = rect.height()

            if spr.highlight:
                painter.setPen(QPen(Qt.red, 3))
            else:
                painter.setPen(QPen(Qt.black))

            painter.drawRect(rect)

            if self.drawDiagonalsAct.isChecked():
                painter.drawLine(x, y, x + w, y + h)
                painter.drawLine(x + w, y, x, y + h)

            if self.drawNamesAct.isChecked():
                text_fm = QFontMetrics(painter.font())
                text_width = text_fm.width(spr.name)
                painter.drawText(x + w/2 - text_width/2, y + h/2, spr.name)

    def createSprite(self, r):
        name, ok = QInputDialog().getText(self, "Create sprite", "Sprite name:",
                                          QLineEdit.Normal, "unnamed")

        if name and ok:
            spr = Sprite(name, r.x(), r.y(), r.width(), r.height())

            it = QListWidgetSprite(spr)
            self.spritesList.addItem(it)

            spr.QListItemRef = it
            self.sprites.append(spr)

    def open(self):
        fileName,_ = QFileDialog.getOpenFileName(self, "Open File", QDir.currentPath())
        if fileName:
            self.openFile(fileName)

    def openFile(self, fileName):
        image = QImage(fileName)
        if image.isNull():
            QMessageBox.information(self, self.windowTitle, f"Cannot load {fileName}.")
            return

        self.imageLabel.setPixmap(QPixmap.fromImage(image))
        self.scaleFactor = 1.0
        self.imageLabel.adjustSize()

    def save(self):
        self.writeStylesheet()

    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    def about(self):
        QMessageBox.about(self, "About",
                "<b>RCSS Sprite Editor</b>"
                "<p>"
                "<p>By svenvvv, <a href=\"https://github.com/svenvvv\">Github</a></p>"
                "WIP sprite editor for RmlUi spritesheets"
                "</p>"
                "<br><br><b>License</b>"
                "<p>"
                "This program is free software: you can redistribute it and/or modify "
                "it under the terms of the GNU General Public License as published by "
                "the Free Software Foundation, version 3."
                "<br><br>"
                "This program is distributed in the hope that it will be useful, but "
                "WITHOUT ANY WARRANTY; without even the implied warranty of "
                "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU "
                "General Public License for more details."
                "<br><br>"
                "You should have received a copy of the GNU General Public License "
                "along with this program. If not, see <http://www.gnu.org/licenses/>."
                "</p>")

    def createActions(self):
        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O",
                triggered=self.open)
        self.openAct.setIcon(QIcon.fromTheme("document-open"))

        self.saveAct = QAction("&Save...", self, shortcut="Ctrl+S",
                triggered=self.save)
        self.saveAct.setIcon(QIcon.fromTheme("document-save"))

        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)
        self.exitAct.setIcon(QIcon.fromTheme("window-close"))

        self.zoomInAct = QAction("Zoom &In (25%)", self,
                shortcut="Ctrl++", triggered=self.zoomIn)
        self.zoomInAct.setIcon(QIcon.fromTheme("zoom-in"))

        self.zoomOutAct = QAction("Zoom &Out (25%)", self,
                shortcut="Ctrl+-", triggered=self.zoomOut)
        self.zoomOutAct.setIcon(QIcon.fromTheme("zoom-out"))

        self.normalSizeAct = QAction("&Normal Size", self,
                shortcut="Ctrl+Z", triggered=self.normalSize)
        self.normalSizeAct.setIcon(QIcon.fromTheme("zoom-original"))

        self.drawRectsAct = QAction("Draw sprite out&lines", self, checkable=True)
        self.drawRectsAct.setChecked(True)
        self.drawNamesAct = QAction("Draw spri&te names", self, checkable=True)
        self.drawDiagonalsAct = QAction("Draw sprite &diagonals", self, checkable=True)
        self.drawPrevRectsOnDrawAct = QAction("Draw other sprites when creating a new sprite", self,
                                              checkable=True, triggered=self.changeDrawPrevRectsOnDrawAct)
        self.drawPrevRectsOnDrawAct.setChecked(True)

        self.aboutAct = QAction("&About", self, triggered=self.about)

    def createMenus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.viewMenu = QMenu("&View", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.drawRectsAct)
        self.viewMenu.addAction(self.drawNamesAct)
        self.viewMenu.addAction(self.drawDiagonalsAct)
        self.viewMenu.addAction(self.drawPrevRectsOnDrawAct)

        self.helpMenu = QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.helpMenu)

        self.ctxEditMenu = QMenu(self)

        editAction = QAction('Edit', self, triggered=self.ctxEditEdit)
        editAction.setIcon(QIcon.fromTheme("document-properties"))
        self.ctxEditMenu.addAction(editAction)

        deleteAction = QAction('Delete', self, triggered=self.ctxEditDelete)
        deleteAction.setIcon(QIcon.fromTheme("edit-delete"))
        self.ctxEditMenu.addAction(deleteAction)

    def changeDrawPrevRectsOnDrawAct(self):
        if self.drawPrevRectsOnDrawAct.isChecked():
            self.imageLabel.paintStarted.connect(self.paintSprites)
            self.imageLabel.paintFinished.disconnect(self.paintSprites)
        else:
            self.imageLabel.paintStarted.disconnect(self.paintSprites)
            self.imageLabel.paintFinished.connect(self.paintSprites)

    def ctxEditEdit(self):
        ed = SpriteEditModal()
        # ed.show()
        # ed.exec_()

    def ctxEditDelete(self):
        s = self.editSprite
        if s.QListItemRef:
            lw = s.QListItemRef.listWidget()
            lw.takeItem(lw.row(s.QListItemRef))

        self.sprites.remove(self.editSprite)
        self.editSprite = None
        self.spritesList.setCurrentItem(None)

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

    app = QApplication(sys.argv)
    imageViewer = ImageViewer()
    imageViewer.openFile("/home/admin/projects/mythos/data/gui/invader.png")
    imageViewer.show()
    sys.exit(app.exec_())
