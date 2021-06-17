from PySide2 import QtCore, QtGui
from PySide2.QtWidgets import QLabel
from PySide2.QtGui import QColor, QBrush, QPen, QPainter, QPaintEvent, QFontMetrics, QTransform
from PySide2.QtCore import Qt, QRect, QPoint

class ImageSelect(QLabel):
    paintFinished = QtCore.Signal(QPaintEvent)
    rectSelected = QtCore.Signal(QPainter)
    contextMenu = QtCore.Signal(QPoint)

    scale = (1.0, 1.0)
    cursor_pos = None
    selection_start = None

    textBgBrush = QBrush(Qt.white)
    selLinePen = QPen(Qt.black, 2)

    flipY = True

    def __init__(self):
        super().__init__()

        selDashes = [1, 4]
        self.selRectBlackLinePen = QPen(Qt.black, 1, Qt.CustomDashLine)
        self.selRectBlackLinePen.setDashPattern(selDashes)
        self.selRectWhiteLinePen = QPen(Qt.white, 1, Qt.CustomDashLine)
        self.selRectWhiteLinePen.setDashPattern(list(reversed(selDashes)))

    def setPixmap(self, pixmap):
        tr = QTransform()
        tr.scale(1.0, -1.0)

        r = super().setPixmap(pixmap.transformed(tr))

        return r

    def paintEvent(self, evt):
        super().paintEvent(evt)

        painter = QPainter(self)
        painter.scale(*self.scale)

        if self.cursor_pos:
            # Paint aiming lines
            cur = self.cursor_pos
            sel = self.selection_start

            painter.setPen(self.selRectWhiteLinePen)
            painter.drawLine(cur.x(), 0, cur.x(), self.pixmap().height())
            painter.drawLine(0, cur.y(), self.pixmap().width(), cur.y())
            painter.setPen(self.selRectBlackLinePen)
            painter.drawLine(cur.x(), 0, cur.x(), self.pixmap().height())
            painter.drawLine(0, cur.y(), self.pixmap().width(), cur.y())

        if self.selection_start:
            # Paint selection rectangle
            size_x = sel.x() - cur.x()
            size_y = sel.y() - cur.y()

            painter.setPen(self.selRectWhiteLinePen)
            painter.drawRect(cur.x(), cur.y(), size_x, size_y)
            painter.setPen(self.selRectBlackLinePen)
            painter.drawRect(cur.x(), cur.y(), size_x, size_y)

            # Paint selection dimensions rect and text
            painter.setPen(self.selLinePen)

            text_x = cur.x()
            text_y = cur.y()

            if size_x < 0:
                text_x = sel.x()
            if size_y < 0:
                text_y = sel.y()

            text_y -= painter.pen().width()

            dim_text = f"{abs(size_x)} x {abs(size_y)}"

            text_fm = QFontMetrics(painter.font())
            text_width = text_fm.width(dim_text)
            text_height = text_fm.height()

            painter.setBrush(self.textBgBrush)
            painter.drawRect(text_x, text_y, text_width + 6, -text_height)

            painter.drawText(text_x + 3, text_y - 3, dim_text)

        # NOTE: don't emit paintFinished when selecting, causes too much clutter :(
        if not self.selection_start:
            self.paintFinished.emit(painter)

        painter.end()

    def _transformPoint(self, p):
        r = QPoint(p.x() / self.scale[0], p.y() / self.scale[1])
        return r

    def mousePressEvent(self, evt):
        if evt.buttons() == QtCore.Qt.LeftButton:
            if not self.selection_start:
                self.selection_start = self._transformPoint(evt.pos())
            else:
                cur = self.selection_start
                end = self._transformPoint(evt.pos())
                rect = QRect(cur.x(), cur.y(),
                             end.x() - cur.x(), end.y() - cur.y())
                self.rectSelected.emit(rect)
                self.selection_start = None
                self.update()
        elif evt.buttons() == QtCore.Qt.RightButton:
            if self.selection_start:
                self.selection_start = None
            else:
                self.contextMenu.emit(self._transformPoint(evt.pos()))

    def mouseMoveEvent(self, evt):
        self.cursor_pos = self._transformPoint(evt.pos())
        self.update()

    def setScale(self, scale):
        self.scale = (scale, scale)
        self.resize(scale * self.pixmap().size())
        self.update()
