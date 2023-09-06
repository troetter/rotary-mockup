from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class LabeledBox:
    def __init__(self, label=''):
        self.label = label
        self.label_pen = None
        self.text_pen = None
        self.shaded_text_pen = None
        self.entry_brush = None
        self.text = ''
        self.entry = False
        self.shaded = False


    def set_label_pen(self, pen):
        self.label_pen = pen


    def set_text_pen(self, pen):
        self.text_pen = pen


    def set_shaded_text_pen(self, pen):
        self.shaded_text_pen = pen


    def set_entry_brush(self, brush):
        self.entry_brush = brush


    def set_text(self, text):
        self.text = text


    def set_entry(self, entry):
        self.entry = entry


    def set_shaded(self, shaded):
        self.shaded = shaded


    def draw(self, painter, rect):
        h = rect.height()
        label_px = h * 0.2
        text_px = h * 0.65

        if self.entry and self.entry_brush is not None:
            path = QPainterPath()
            path.addRoundedRect(
                rect.x(),
                rect.y(),
                rect.width(),
                rect.height(),
                rect.height()/3,
                rect.height()/3)
            painter.fillPath(path, self.entry_brush)

        font = painter.font()
        font.setFamily('Monospace')

        if self.label_pen is not None:
            font.setPixelSize(int(label_px))
            painter.setFont(font)
            painter.setPen(self.label_pen)
            painter.drawText(rect, Qt.AlignHCenter + Qt.AlignTop, self.label)

        if self.shaded:
            pen = self.shaded_text_pen
        else:
            pen = self.text_pen

        if pen is not None:
            painter.setPen(pen)
            font.setPixelSize(int(text_px))
            painter.setFont(font)

            painter.drawText(
                rect,
                Qt.AlignHCenter + Qt.AlignBottom,
                self.text)
