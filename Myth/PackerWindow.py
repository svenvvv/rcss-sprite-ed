import functools
import os
import Myth.Util

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from Myth.Models.Spritesheet import Spritesheet
from Myth.UiLoader import UiLoader

from MythPack.SpritePacker import SpritePacker, PackerException

class PackerWindow(QDialog):
    _color = 0x00000000

    def __init__(self):
        QDialog.__init__(self)
        UiLoader.load_ui("ui/packer.ui", self)

        self.previewButton.clicked.connect(self._cb_generatePreview)
        self.bgColorButton.clicked.connect(self._cb_selectColor)

        self.inputBrowseButton.clicked.connect(self._cb_inputBrowse)
        self.outputBrowseButton.clicked.connect(self._cb_outputBrowse)

        self.show()

    def generate(self, loadPath):
        kwargs = {
            "max_width": self.maxWidthSpinBox.value(),
            "max_height": self.maxHeightSpinBox.value(),
            "bg_color": self._color,
            "border_padding": self.borderPaddingSpinBox.value(),
            "shape_padding": self.shapePaddingSpinBox.value(),
            "inner_padding": self.innerPaddingSpinBox.value(),
            "force_square": self.squareOutputCheckBox.isChecked(),
            "enable_rotated": False
        }

        try:
            packer = SpritePacker(loadPath, True)
            return packer.pack(**kwargs)
        except PackerException as e:
            QMessageBox.critical(self, self.windowTitle(), str(e))

    def _cb_selectColor(self):
        color = QColorDialog.getColor(parent=self, title="Choose background color",
                                      options=QColorDialog.ShowAlphaChannel)
        if not color:
            return
        hexcol = color.name()[1:] + hex(color.alpha())[2:].zfill(2)
        self._color = int(hexcol, 16)

    def _cb_generatePreview(self):
        loadPath = self.inputEdit.text()

        if not loadPath:
            QMessageBox.warning(self, self.windowTitle(), "Please enter the input directory")
            return

        img, sprites, error = self.generate(loadPath)
        if not img:
            self.infoLabel.setStyleSheet("color: rgb(255, 0, 4);")
            self.infoLabel.setText(error)
            return

        if error:
            self.infoLabel.setStyleSheet("color: rgb(255, 0, 4);")
            self.infoLabel.setText(error)
        else:
            self.infoLabel.setStyleSheet("color: rgb(0, 255, 4);")
            self.infoLabel.setText(f"Successfully generated sheet {img.width()}x{img.height()} with {len(sprites)} sprites")

        self.imageLabel.setPixmap(QPixmap.fromImage(img))

    def _cb_inputBrowse(self):
        loadPath = QFileDialog.getExistingDirectory(self,
                                                    "Open image directory", QDir.currentPath())
        if not loadPath:
            return
        self.inputEdit.setText(loadPath)

    def _cb_outputBrowse(self):
        imgFmts = Myth.Util.supportedImageWriteFormats()
        imagePath, fmt = QFileDialog.getSaveFileName(self, "Select output image file",
                                                     QDir.currentPath(), imgFmts)
        if not imagePath or not fmt:
            return

        self._outFmt = Myth.Util.supportedImageFormatToExt(fmt)

        if self._outFmt and not imagePath.lower().endswith(self._outFmt.lower()):
            imagePath += "." + self._outFmt.lower()
        self.outputEdit.setText(imagePath)

    def accept(self):
        loadPath = self.inputEdit.text()
        imagePath = self.outputEdit.text()

        if not loadPath or not imagePath:
            QMessageBox.warning(self, self.windowTitle(),
                                "Please enter input and output directories")
            return

        img, sprites, error = self.generate(loadPath)
        if not img or not sprites or error:
            errmsg = error if error else "Failed to generate spritesheet"
            QMessageBox.critical(self, self.windowTitle(), errmsg)
            return

        if not self._outFmt:
            _,ext = os.path.splitext(imagePath)
            if len(ext) == 0:
                self._outFmt = "PNG"
                imagePath += ".png"


        writer = QImageWriter(imagePath, self._outFmt)

        if not writer.write(img):
            QMessageBox.critical(self, self.windowTitle(),
                                 f"Error writing image: {writer.error()}")
            return

        file = os.path.basename(imagePath)
        base = os.path.dirname(imagePath)

        if len(base) == 0:
            base = "."

        self.generatedSheet = Spritesheet(base, "packed", sprites, file)

        self.done(1)

    def reject(self):
        self.done(0)

