from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from ui_elements import LabeledBox


class DivisionWidget(QWidget):
    num_divs_pressed = pyqtSignal()
    start_angle_pressed = pyqtSignal()
    stop_angle_pressed = pyqtSignal()


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.data_valid_pen = QPen(Qt.black, 1.5)
        self.data_entry_pen = QPen(Qt.gray, 1.5)
        self.data_entry_brush = QBrush(Qt.white)
        self.label_pen = QPen(Qt.black, 1.5)

        self.num_divs_box = LabeledBox('NUM DIVISIONS')
        self.start_angle_box = LabeledBox('START ANGLE')
        self.stop_angle_box = LabeledBox('STOP_ANGLE')

        for box in [self.num_divs_box, self.start_angle_box, self.stop_angle_box]:
            box.set_label_pen(self.label_pen)
            box.set_text_pen(self.data_valid_pen)
            box.set_shaded_text_pen(self.data_entry_pen)
            box.set_entry_brush(self.data_entry_brush)


    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.HighQualityAntialiasing)

        w, h = self.width(), self.height()

        div_rect = QRectF(0, h * 0.2, w, h * 0.2)
        start_rect = QRectF(0, h * 0.45, w, h * 0.2)
        stop_rect = QRectF(0, h * 0.7, w, h * 0.2)

        self.num_divs_box.draw(painter, div_rect)
        self.start_angle_box.draw(painter, start_rect)
        self.stop_angle_box.draw(painter, stop_rect)
