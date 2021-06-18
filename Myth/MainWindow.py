import os

from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import QUiLoader

from Myth.ImageSelect import ImageSelect
from Myth.Sprite import Sprite
from Myth.RCSSParser import RCSSParser
from Myth.SpriteEditModal import SpriteEditModal
from Myth.UiLoader import UiLoader


class QListWidgetSprite(QListWidgetItem):
    def __init__(self, sprite):
        super().__init__(sprite.name)
        self.sprite = sprite


class MainWindow(QMainWindow):
    css = None
    sprites = []
    selectedSprite = None
    redrawingSprite = None
    windowTitle = "RCSS Spritesheet Editor"
    scale = 1.0

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        UiLoader.load_ui("ui/main.ui", self)

        self._setupImageSelect()
        self._setupActions()
        self._setupMenus()

        self.loadStylesheet("../../data/gui/invader.rcss")

        self.show()

    def _setupImageSelect(self):
        self.imageSelect = ImageSelect()
        self.scrollArea.setWidget(self.imageSelect)
        self.scrollArea.setWidgetResizable(False)

        self.imageSelect.rectStarted.connect(self._cb_spriteStarted)
        self.imageSelect.rectFinished.connect(self._cb_spriteFinished)
        self.imageSelect.paintStarted.connect(self._cb_paintStarted)
        self.imageSelect.contextMenu.connect(self.tryOpenCtxMenu)

    def _setupActions(self):
        self.actionOpen.triggered.connect(self._cb_actionOpen)
        self.actionSave.triggered.connect(self._cb_actionSave)
        self.actionSaveAs.triggered.connect(self._cb_actionSave)
        self.actionQuit.triggered.connect(self.close)

        self.actionReplaceImage.triggered.connect(self._cb_actionReplaceImage)
        self.actionSetResolution.triggered.connect(self._cb_actionSetResolution)

        self.actionZoomIn.triggered.connect(self._cb_actionZoomIn)
        self.actionZoomOut.triggered.connect(self._cb_ZoomOut)
        self.actionZoomReset.triggered.connect(self._cb_actionZoomReset)
        self.actionDrawSpritesDuringSketching.triggered.connect(self._cb_actionDrawSpritesDuringSketching)
        self.actionAbout.triggered.connect(self._cb_actionAbout)

    def _setupMenus(self):
        self.spritesList.itemSelectionChanged.connect(self._cb_spritesListSelectItem)
        self.spritesList.customContextMenuRequested.connect(self._cb_spritesListOpenCtxMenu)

        self.ctxEditMenu = QMenu(self)

        def cb_edit():
            ed = SpriteEditModal(self.selectedSprite, self)

        def cb_redraw():
            s = self.selectedSprite
            self.redrawingSprite = s
            self.deleteSprite(s)
            self.statusBar().showMessage(f"Redrawing sprite {s.name}...")

        def cb_delete():
            s = self.selectedSprite
            self.deleteSprite(s)

        editAction = QAction('Edit', self, triggered=cb_edit)
        editAction.setIcon(QIcon.fromTheme("document-properties"))
        self.ctxEditMenu.addAction(editAction)

        redrawAction = QAction('Redraw', self, triggered=cb_redraw)
        redrawAction.setIcon(QIcon.fromTheme("list-add"))
        self.ctxEditMenu.addAction(redrawAction)

        deleteAction = QAction('Delete', self, triggered=cb_delete)
        deleteAction.setIcon(QIcon.fromTheme("edit-delete"))
        self.ctxEditMenu.addAction(deleteAction)

    def deleteSprite(self, s):
        if s.QListItemRef:
            lw = s.QListItemRef.listWidget()
            lw.takeItem(lw.row(s.QListItemRef))
            self.sprites.remove(s)
            self.selectedSprite = None
            self.spritesList.setCurrentItem(None)
            self.statusBar().showMessage(f"Deleted sprite {s.name}")


    def loadStylesheet(self, filename):
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
            self.css = ss
            for d in ss.declarations:
                it = QListWidgetSprite(d)
                self.spritesList.addItem(it)

                d.QListItemRef = it
                self.sprites.append(d)

        basepath = os.path.dirname(filename)
        self.openImage(basepath + "/" + self.css.props["src"])

        self.statusBar().showMessage(f"Successfully loaded stylesheet {filename} with {len(self.css.declarations)} sprites")


    def saveStylesheet(self):
        ss = self.css

        print(f"@stylesheet {ss.name}")
        print("{")
        print(f"\tsrc: {ss.props['src']};")
        print(f"\tresolution: {ss.props['resolution']}x;")

        for s in self.sprites:
            print(f"\t{s.toRCSS()}")
        print("}")

    def repaint(self):
        self.imageSelect.update()

    def findSpriteByQItem(self, item):
        for s in self.sprites:
            if s.QListItemRef == item:
                return s

    def findSpriteByName(self, name):
        for s in self.sprites:
            if s.name == name:
                return s

    def openCtxEditMenu(self, sprite, pos):
        self.selectedSprite = sprite
        self.ctxEditMenu.popup(pos)

    def openCtxSpriteSelectMenu(self, pos, sprites):
        def selectSpriteFromCtx(act):
            self.selectedSprite = self.findSpriteByName(act.text())
            self.ctxEditMenu.popup(pos)

        menu = QMenu(self)
        menu.triggered.connect(selectSpriteFromCtx)

        for spr in sprites:
            act = QAction(spr.name, self)
            menu.addAction(act)

        menu.popup(pos)

    def tryOpenCtxMenu(self, target):
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
            self.selectedSprite = None
            self.repaint()

            self.openCtxSpriteSelectMenu(pos, hit)
            return

        selHit = hit[0]
        if selHit.QListItemRef:
            it = selHit.QListItemRef
            l = it.listWidget()
            l.setCurrentItem(it)
            self.openCtxEditMenu(selHit, pos)
        else:
            QMessageBox.error(self, self.windowTitle, "Sprite is missing list ref!")

    def openImage(self, filename):
        image = QImage(filename)
        if image.isNull():
            QMessageBox.information(self, self.windowTitle, f"Cannot load {filename}.")
            return False

        pixmap = QPixmap.fromImage(image)
        self.imageSelect.setPixmap(pixmap)
        self.scale = 1.0
        self.imageSelect.adjustSize()
        self.statusBar().showMessage(f"Successfully loaded image {filename} ({pixmap.width()}x{pixmap.height()})")
        return True

    def scaleImage(self, factor):
        self.scale *= factor
        self.imageSelect.setScale(self.scale)

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

        self.actionZoomIn.setEnabled(self.scale < 3.0)
        self.actionZoomOut.setEnabled(self.scale > 0.333)

    def adjustScrollBar(self, scrollBar, factor):
        val = factor * scrollBar.value() + ((factor - 1) * scrollBar.pageStep()/2)
        scrollBar.setValue(int(val))

    def _cb_paintStarted(self, painter):
        if not self.actionDrawSpriteOutlines.isChecked():
            return

        for spr in self.sprites:
            rect = spr.rect
            x = rect.x()
            y = rect.y()
            w = rect.width()
            h = rect.height()

            if spr == self.selectedSprite:
                painter.setPen(QPen(Qt.red, 3))
            else:
                painter.setPen(QPen(Qt.black))

            painter.drawRect(rect)

            if self.actionDrawSpriteDiagonals.isChecked():
                painter.drawLine(x, y, x + w, y + h)
                painter.drawLine(x + w, y, x, y + h)

            if self.actionDrawSpriteNames.isChecked():
                text_fm = QFontMetrics(painter.font())
                text_width = text_fm.width(spr.name)
                painter.drawText(x + w/2 - text_width/2, y + h/2, spr.name)

    def _cb_spriteStarted(self):
        self.selectedSprite = None

    def _cb_spriteFinished(self, r):
        name = None

        if self.redrawingSprite:
            name = self.redrawingSprite.name
            self.redrawingSprite = None
        else:
            name, ok = QInputDialog().getText(self, "Create sprite", "Sprite name:",
                                              QLineEdit.Normal, "unnamed")
            if not ok:
                self.statusBar().showMessage("Failed to get name for sprite")
                return

        if name:
            spr = Sprite(name, r.x(), r.y(), r.width(), r.height())

            it = QListWidgetSprite(spr)
            self.spritesList.addItem(it)

            spr.QListItemRef = it
            self.sprites.append(spr)
            self.statusBar().showMessage(f"Created sprite {name} ({r.x()},{r.y()},{r.width()},{r.height()})")

    def _cb_actionReplaceImage(self):
        filename,_ = QFileDialog.getOpenFileName(self, "Open image", QDir.currentPath())
        if filename and self.openImage(filename):
            self.css.props["src"] = os.path.basename(filename)

    def _cb_actionSetResolution(self):
        res, ok = QInputDialog().getInt(self, "Set resolution", "New resolution:",
                                    int(self.css.props["resolution"]), minValue=1)
        if res and ok:
            self.css.props["resolution"] = res

    def _cb_spritesListOpenCtxMenu(self, pos):
        it = self.spritesList.selectedItems()[0]
        target = self.findSpriteByQItem(it)
        self.openCtxEditMenu(target, QCursor.pos())

    def _cb_spritesListSelectItem(self):
        sel = self.spritesList.selectedItems()
        if len(sel) > 0:
            spr = self.findSpriteByQItem(sel[0])
            if spr:
                self.selectedSprite = spr
                self.repaint()

    def _cb_actionOpen(self):
        filename,_ = QFileDialog.getOpenFileName(self, "Open File", QDir.currentPath())
        if filename:
            self.openImage(filename)

    def _cb_actionSave(self):
        self.saveStylesheet()

    def _cb_actionZoomIn(self):
        self.scaleImage(1.25)

    def _cb_ZoomOut(self):
        self.scaleImage(0.8)

    def _cb_actionZoomReset(self):
        self.imageSelect.adjustSize()
        self.scale = 1.0
        self.imageSelect.setScale(1.0)

    def _cb_actionAbout(self):
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

    def _cb_actionDrawSpritesDuringSketching(self):
        if self.actionDrawSpritesDuringSketching.isChecked():
            self.imageSelect.paintStarted.connect(self._cb_paintStarted)
            self.imageSelect.paintFinished.disconnect(self._cb_paintStarted)
        else:
            self.imageSelect.paintStarted.disconnect(self._cb_paintStarted)
            self.imageSelect.paintFinished.connect(self._cb_paintStarted)
