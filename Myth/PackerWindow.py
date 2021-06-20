from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

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

    def generate(self):
        loadPath = self.inputEdit.text()
        imagePath = self.outputEdit.text()

        print(self._color)

        kwargs = {
            "max_width": self.maxWidthSpinBox.value(),
            "max_height": self.maxHeightSpinBox.value(),
            "bg_color": self._color,
            "border_padding": self.borderPaddingSpinBox.value(),
            "shape_padding": self.shapePaddingSpinBox.value(),
            "inner_padding": self.innerPaddingSpinBox.value(),
            "force_square": self.squareOutputCheckBox.isChecked()
        }

        if not loadPath or not imagePath:
            QMessageBox.warning(self, self.windowTitle(), "Please enter input and output paths")
            return None

        try:
            packer = SpritePacker(loadPath, True)
        except PackerException as e:
            QMessageBox.critical(self, self.windowTitle(), str(e))

        return packer.pack(**kwargs)

        # img.save(imagePath, "PNG")

        # file = os.path.basename(imagePath)
        # base = os.path.dirname(imagePath)

        # print(imagePath, file, base)

        # ss = Spritesheet(base, "packed", sprites, file)

    def _cb_selectColor(self):
        color = QColorDialog.getColor(parent=self, title="Choose background color", options=QColorDialog.ShowAlphaChannel)
        if not color:
            return
        hexcol = color.name()[1:] + hex(color.alpha())[2:]
        print(hexcol)
        self._color = int(hexcol, 16)

    def _cb_generatePreview(self):
        img, _ = self.generate()
        self.imageLabel.setPixmap(QPixmap.fromImage(img))
        pass

    def _cb_inputBrowse(self):
        loadPath = QFileDialog.getExistingDirectory(self,
                                                    "Open image directory", QDir.currentPath())
        if not loadPath:
            return
        self.inputEdit.setText(loadPath)

    def _cb_outputBrowse(self):
        imagePath,_ = QFileDialog.getSaveFileName(self,
                                                  "Select output image file", QDir.currentPath())
        if not imagePath:
            return
        self.outputEdit.setText(imagePath)

