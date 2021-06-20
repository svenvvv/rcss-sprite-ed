import os

from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import QUiLoader

from Myth.SpriteEditModal import SpriteEditModal
from Myth.AboutWindow import AboutWindow

from Myth.ImageSelect import ImageSelect
from Myth.Sprite import Sprite
from Myth.RCSSParser import RCSSParser
from Myth.UiLoader import UiLoader
from Myth.Commands import *


class QListWidgetSprite(QListWidgetItem):
    def __init__(self, sprite):
        super().__init__(sprite.name())
        self.sprite = sprite

class SpritesheetError(ValueError):
    def __init__(self, message):
        super().__init__(message)

class Spritesheet:
    requiredProps = [ "src" ]
    _sprites = []
    _props = []
    _basepath = None

    def __init__(self, css):
        self._name = css.name
        self._sprites = css.declarations
        self._props = css.props

        for p in self.requiredProps:
            if not p in self._props:
                raise SpritesheetError(f"Missing required property: {p}")

    def setBasepath(self, path):
        self._basepath = path

    def basepath(self):
        return self._basepath

    def resolution(self):
        return self._props["resolution"]

    def setResolution(self, res):
        self._props["resolution"] = res

    def source(self):
        return self._props["src"]

    def sourceLongPath(self):
        return f"{self.basepath()}/{self.source()}"

    def setSource(self, source):
        self._props["src"] = source

    def name(self):
        return self._name

    def sprites(self):
        return self._sprites

    def props(self):
        return self._props

    def serialize(self):
        ret = f"@spritesheet {self._name}\n"
        ret += "{\n"

        ret += f"\t/* Path: {self.sourceLongPath()} */\n"
        ret += f"\tsrc: {self._props['src']};\n"

        if self._props["resolution"]:
            ret += f"\tresolution: {self._props['resolution']}x;\n"

        ret += "\n"

        for s in self._sprites:
            ret += f"\t{s.toRCSS()}\n"

        ret += "}\n"

        return ret


class SpriteListModel(QAbstractListModel):
    _selected = None
    _redrawing = None

    def __init__(self, *args, sprites=[], sheet=None, **kwargs):
        super(SpriteListModel, self).__init__(*args, **kwargs)
        self._sheet = sheet
        self._sprites = sprites
        self._undoStack = QUndoStack(self)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            ss = self._sprites[index.row()]
            return ss.name()

    def rowCount(self, index):
        return len(self._sprites)

    def sprites(self):
        return self._sprites

    def findDupes(self, name):
        dupes = filter(lambda s: s.name() == name, self._sprites)
        if len(list(dupes)) > 0:
            return True
        return False

    def insertRow(self, sprite):
        if self.findDupes(sprite.name()):
            return False

        l = len(self._sprites)
        self.beginInsertRows(QModelIndex(), l, l+1)
        self._sprites.append(sprite)
        self.endInsertRows()
        return True

    def removeRow(self, sprite):
        idx = self._sprites.index(sprite)
        self.beginRemoveRows(QModelIndex(), idx, idx)
        if self._selected == sprite:
            self._selected = None
        self._sprites.remove(sprite)
        self.endRemoveRows()

    def hitTest(self, pos):
        hit = []
        for spr in self._sprites:
            if spr.aabbTest(pos):
                hit.append(spr)
        return hit

    def selected(self):
        return self._selected

    def setSelected(self, sprite):
        print(f"Setselected {sprite.name()}")
        self._selected = sprite

    def setSelectedByName(self, spriteName):
        for spr in self._sprites:
            if spr.name() == spriteName:
                self._selected = spr
                return True
        return False

    def clearSelection(self):
        self._selected = None

    def sheet(self):
        return self._sheet


class SpritesheetListModel(QAbstractListModel):
    _selected = None
    itemSelectionChanged = Signal(Spritesheet)

    def __init__(self, *args, sheets=[], **kwargs):
        super(SpritesheetListModel, self).__init__(*args, **kwargs)
        self._sheets = sheets

    def data(self, index, role):
        if role == Qt.DisplayRole:
            ss = self._sheets[index.row()]
            return ss.name()

    def rowCount(self, index):
        return len(self._sheets)

    def getSheetListModel(self, sheetName):
        for s in self._sheets:
            if s.name() == sheetName:
                return SpriteListModel(sprites=s.sprites(), sheet=s)

    def setSheetImage(self, sheet, image):
        sheet.setSource(image)

    def getSheetImage(self, sheetName=None):
        if sheetName is None:
            sheetName = self._selected.name()

        for s in self._sheets:
            if s.name() == sheetName:
                return f"{s.basepath()}/{s.source()}"

    def sheets(self):
        return self._sheets

    def selected(self):
        return self._selected

    def setSelectedByName(self, sheetName):
        for s in self._sheets:
            if s.name() == sheetName:
                self._selected = s
                self.itemSelectionChanged.emit(s)
                return True
        return False

    def clearSelection(self):
        self._selected = None

class MainWindow(QMainWindow):
    redrawingSprite = None
    windowTitle = "RCSS Spritesheet Editor"
    scale = 1.0

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        UiLoader.load_ui("ui/main.ui", self)

        self._setupImageSelect()
        self._setupActions()
        self._setupMenus()
        self._setupUndo()

        self.loadStylesheet("tests/data/multiple-spritesheets.rcss")

        self.show()

    def _setupUndo(self):
        self.undo = QUndoStack(self)

        self.undo.canUndoChanged.connect(lambda v: self.actionUndo.setEnabled(v))
        self.undo.canRedoChanged.connect(lambda v: self.actionRedo.setEnabled(v))

        self.actionUndo.setEnabled(False)
        self.actionRedo.setEnabled(False)

    def _setupImageSelect(self):
        self.imageSelect = ImageSelect()
        self.scrollArea.setWidget(self.imageSelect)
        self.scrollArea.setWidgetResizable(False)

        self.imageSelect.rectStarted.connect(self._cb_spriteStarted)
        self.imageSelect.rectFinished.connect(self._cb_spriteFinished)
        self.imageSelect.paintStarted.connect(self._cb_paintStarted)
        self.imageSelect.contextMenu.connect(self.tryOpenCtxMenu)

    def _setupActions(self):
        self.actionSave.setEnabled(False)
        self.actionSaveAs.setEnabled(False)

        self.actionOpen.triggered.connect(self._cb_actionOpen)
        self.actionSave.triggered.connect(self._cb_actionSave)
        self.actionSaveAs.triggered.connect(self._cb_actionSave)
        self.actionReload.triggered.connect(self._cb_actionReload)
        self.actionQuit.triggered.connect(self.close)

        self.actionUndo.triggered.connect(lambda: self.undo.undo())
        self.actionRedo.triggered.connect(lambda: self.undo.redo())

        self.actionReplaceImage.triggered.connect(self._cb_actionReplaceImage)
        self.actionSetResolution.triggered.connect(self._cb_actionSetResolution)

        self.actionZoomIn.triggered.connect(self._cb_actionZoomIn)
        self.actionZoomOut.triggered.connect(self._cb_actionZoomOut)
        self.actionZoomReset.triggered.connect(self._cb_actionZoomReset)

        self.actionDrawSpritesDuringSketching.triggered.connect(self._cb_actionDrawSpritesDuringSketching)
        self.actionFlipImageX.triggered.connect(self._cb_actionReload)
        self.actionFlipImageY.triggered.connect(self._cb_actionReload)

        self.actionAbout.triggered.connect(self._cb_actionAbout)

    def _setupMenus(self):
        # self.spritesList.itemSelectionChanged.connect(self._cb_spritesListSelectItem)
        self.spritesList.customContextMenuRequested.connect(lambda: self.ctxEditMenu.popup(QCursor.pos()))

        # self.spritesList.clicked.connect(self._cb_spritesListSelectItem)
        # self.spritesheetsList.clicked.connect(self._cb_spritesheetsListSelectItem)

        self.ctxEditMenu = QMenu(self)

        def cb_edit():
            s = self.spritesList.model().selected()
            d = SpriteEditModal(s, self)
            if d.exec() == QDialog.Accepted:
                CommandModifySprite(self, s, **d.newValues)

        def cb_redraw():
            s = self.spritesList.model().selected()
            self.redrawingSprite = s
            self.statusBar().showMessage(f"Redrawing sprite {s.name()}...")

        def cb_delete():
            s = self.spritesList.model().selected()
            CommandDeleteSprite(self, s)

        editAction = QAction("Edit", self, triggered=cb_edit)
        editAction.setIcon(QIcon.fromTheme("document-properties"))
        self.ctxEditMenu.addAction(editAction)

        redrawAction = QAction("Redraw", self, triggered=cb_redraw)
        redrawAction.setIcon(QIcon.fromTheme("list-add"))
        self.ctxEditMenu.addAction(redrawAction)

        deleteAction = QAction("Delete", self, triggered=cb_delete)
        deleteAction.setIcon(QIcon.fromTheme("edit-delete"))
        self.ctxEditMenu.addAction(deleteAction)

        def cb_cancel():
            self.statusBar().showMessage(f"Canceled redrawing sprite {self.redrawingSprite.name()}")
            self.redrawingSprite = None

        self.ctxRedrawMenu = QMenu(self)
        cancelAction = QAction("Cancel redrawing", self, triggered=cb_cancel)
        cancelAction.setIcon(QIcon.fromTheme("go-previous"))
        self.ctxRedrawMenu.addAction(cancelAction)

    def updateTitle(self, filename=None):
        if filename:
            self.setWindowTitle(f"{self.windowTitle} - {filename}")
        else:
            self.setWindowTitle(self.windowTitle)

    def deleteAllSprites(self):
        self.redrawingSprite = None

    def selectSpritesheet(self, name):
        self.redrawingSprite = None

        ssmod = self.spritesheetsList.model()
        ssmod.setSelectedByName(name)
        mod = ssmod.getSheetListModel(name)

        self.spritesList.setModel(mod)
        self.loadImage(ssmod.getSheetImage(name))

        self.statusBar().showMessage(f"Selected spritesheet {name}")

    def loadStylesheet(self, filename):
        parser = RCSSParser()
        css = parser.parse_stylesheet_file(filename)

        if parser.hadSpritesheetError:
            print("CSS errors:", css.errors)
            QMessageBox.critical(self, self.windowTitle, f"Error loading file {filename}")
            return

        spritesheets = list(filter(lambda r: r.at_keyword == "@spritesheet", css.rules))

        if len(spritesheets) == 0:
            QMessageBox.critical(self, self.windowTitle, f"Stylesheet does not contain any spritesheets!")
            return

        self.deleteAllSprites()

        parsedSheets = []
        basepath = os.path.dirname(filename)
        for ss in spritesheets:
            try:
                s = Spritesheet(ss)
                s.setBasepath(basepath)
                parsedSheets.append(s)
            except SpritesheetError as e:
                QMessageBox.critical(self, self.windowTitle, f"Error parsing \"{ss.name}\": {e}")
                return

        mod = SpritesheetListModel(sheets=parsedSheets)
        self.spritesheetsList.setModel(mod)

        self.selectSpritesheet(parsedSheets[0].name())
        self.updateTitle(os.path.basename(filename))

        self.spritesheetsList.model().itemSelectionChanged.connect(self._cb_spritesheetsListSelectItem)

        self.statusBar().showMessage(f"Successfully loaded {len(parsedSheets)} spritesheets")

    def saveStylesheet(self):
        ret = ""
        for ss in self.spritesheetsList.model().sheets():
            ret += ss.serialize()
        return ret

    def repaint(self):
        self.imageSelect.update()

    def openCtxSpriteSelectMenu(self, pos, sprites):
        def cb_select(act):
            self.spritesList.model().setSelectedByName(act.text())
            self.ctxEditMenu.popup(pos)
            self.repaint()

        def cb_hover(act):
            self.spritesList.model().setSelectedByName(act.text())
            self.repaint()

        menu = QMenu(self)
        menu.triggered.connect(cb_select)
        menu.hovered.connect(cb_hover)

        for spr in sprites:
            act = QAction(spr.name(), self)
            menu.addAction(act)

        menu.popup(pos)

    def tryOpenCtxMenu(self, target):
        # Show the popup at cursor position, not target pos
        pos = QCursor.pos()

        if self.redrawingSprite:
            self.ctxRedrawMenu.popup(pos)
            return

        hit = self.spritesList.model().hitTest(target)

        if len(hit) == 0:
            return

        if len(hit) > 1:
            self.spritesList.model().clearSelection()
            self.repaint()
            self.openCtxSpriteSelectMenu(pos, hit)
            return

        selHit = hit[0]
        self.spritesList.model().setSelected(selHit)
        self.repaint()
        self.ctxEditMenu.popup(pos)

    def loadImage(self, filename):
        image = QImage(filename)
        if image.isNull():
            # TODO: rewrite to use QImageReader. Seems like QImage errors go to stderr by default
            # and thus we can't show them in the message box (?)
            QMessageBox.warning(self, self.windowTitle, f"Cannot load {filename}.")
            return False

        pixmap = QPixmap.fromImage(image)
        flipX = self.actionFlipImageX.isChecked()
        flipY = self.actionFlipImageY.isChecked()
        self.imageSelect.setPixmap(pixmap, flipX, flipY)
        self.scale = 1.0
        self.imageSelect.adjustSize()

        self.actionSave.setEnabled(True)
        self.actionSaveAs.setEnabled(True)
        self.actionReplaceImage.setEnabled(True)
        self.actionSetResolution.setEnabled(True)
        self.actionReload.setEnabled(True)

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

        for spr in self.spritesList.model().sprites():
            x = spr.x()
            y = spr.y()
            w = spr.width()
            h = spr.height()

            if spr == self.spritesList.model().selected():
                painter.setPen(QPen(Qt.red, 3))
            else:
                painter.setPen(QPen(Qt.black))

            painter.drawRect(spr)

            if self.actionDrawSpriteDiagonals.isChecked():
                painter.drawLine(x, y, x + w, y + h)
                painter.drawLine(x + w, y, x, y + h)

            if self.actionDrawSpriteNames.isChecked():
                text_fm = QFontMetrics(painter.font())
                text_width = text_fm.width(spr.name())
                painter.drawText(x + w/2 - text_width/2, y + h/2, spr.name())

    def _cb_spriteStarted(self):
        self.spritesList.model().clearSelection()

    def _cb_spriteFinished(self, r):
        if self.redrawingSprite:
            name = self.redrawingSprite.name()
            CommandModifySprite(self, self.redrawingSprite, r.x(), r.y(), r.width(), r.height())
            self.statusBar().showMessage(f"Finished redrawing sprite {self.redrawingSprite.name()}")
            self.redrawingSprite = None
        else:
            name, ok = QInputDialog().getText(self, "Create sprite", "Sprite name:",
                                              QLineEdit.Normal, "unnamed")
            if not ok or not len(name):
                self.statusBar().showMessage("Failed to get name for sprite")
                return

            spr = Sprite(name, r.x(), r.y(), r.width(), r.height())
            CommandCreateSprite(self, spr)

    def _cb_actionReload(self):
        # NOTE: this isn't a CommandReload because we can't undo a reload anyways :-)
        if not self.loadImage(self.spritesList.model().sheet().sourceLongPath()):
            self.statusBar().showMessage("Image reload failed!")

    def _cb_actionReplaceImage(self):
        filename,_ = QFileDialog.getOpenFileName(self, "Open image", QDir.currentPath())
        if filename:
            CommandSetImage(self, filename)

    def _cb_actionSetResolution(self):
        sheet = self.spritesList.model().sheet()
        res, ok = QInputDialog().getInt(self, "Set resolution", "New resolution:",
                                    int(sheet.resolution()), minValue=1)
        if res and ok:
            CommandSetResolution(self, res)

    def _cb_spritesheetsListSelectItem(self, it):
        self.selectSpritesheet(it.data())

    def _cb_actionOpen(self):
        filename,_ = QFileDialog.getOpenFileName(self, "Open File", QDir.currentPath())
        if filename:
            self.loadStylesheet(filename)

    def _cb_actionSave(self):
        ss = self.saveStylesheet()
        res, ok = QInputDialog().getMultiLineText(self, "Output",
                                                  "Saving into RCSS file isn't implemented yet.", ss)

    def _cb_actionZoomIn(self):
        self.scaleImage(1.25)

    def _cb_actionZoomOut(self):
        self.scaleImage(0.8)

    def _cb_actionZoomReset(self):
        self.imageSelect.adjustSize()
        self.scale = 1.0
        self.imageSelect.setScale(1.0)

    def _cb_actionAbout(self):
        AboutWindow().exec()

    def _cb_actionDrawSpritesDuringSketching(self):
        if self.actionDrawSpritesDuringSketching.isChecked():
            self.imageSelect.paintStarted.connect(self._cb_paintStarted)
            self.imageSelect.paintFinished.disconnect(self._cb_paintStarted)
        else:
            self.imageSelect.paintStarted.disconnect(self._cb_paintStarted)
            self.imageSelect.paintFinished.connect(self._cb_paintStarted)
