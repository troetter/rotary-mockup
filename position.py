from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from ui_elements import LabeledBox

import math

class PositionWidget(QWidget):
    position_pressed = pyqtSignal()
    target_pressed = pyqtSignal()
    power_pressed = pyqtSignal()
    direction_pressed = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Margin from widget edge, and length of longest line
        self.rose_margin = 20
        self.rose_width = 14

        # Margin outside rose
        self.target_margin = 3

        # Margin from outside of rose, length of arrow in pixels
        # and width in degrees
        self.arrow_margin = 4
        self.arrow_length = 20
        self.arrow_angle = 5

        green = QColor(0, 196, 0)
        red = QColor(255, 0, 0)
        black = Qt.black
        white = Qt.white
        gray = Qt.gray

        self.arc_pen = QPen(black, 3)
        self.marker_pen = QPen(black, 2)

        self.target_ring_pen = QPen(black, 1.5)
        self.target_pen = QPen(green, 1.0)
        self.target_brush = QBrush(green)

        self.home_arrow_pen = QPen(green, 1.5)
        self.home_arrow_brush = QBrush(green)
        self.away_arrow_pen = QPen(red, 1.5)
        self.away_arrow_brush = QBrush(red)
        self.data_valid_pen = QPen(black, 1.5)
        self.data_entry_pen = QPen(gray, 1.5)
        self.data_entry_brush = QBrush(white)
        self.label_pen = QPen(black, 1.5)

        self.power_off_pen = QPen(gray, 7.5, cap=Qt.RoundCap)
        self.power_on_pen = QPen(green, 7.5, cap=Qt.RoundCap)
        self.direction_pen = QPen(black, 4.5, cap=Qt.RoundCap)

        self.position_value = None
        self.position_field = None
        self.position_box = LabeledBox('POSITION')
        self.target_value = None
        self.target_field = None
        self.target_box = LabeledBox('TARGET')
        self.divisions = []

        for box in [self.position_box, self.target_box]:
            box.set_label_pen(self.label_pen)
            box.set_text_pen(self.data_valid_pen)
            box.set_shaded_text_pen(self.data_entry_pen)
            box.set_entry_brush(self.data_entry_brush)

        self.powered = False
        self.direction_cw = True


    def set_position_value(self, position_value):
        self.position_value = position_value


    def set_position_field(self, position_string, show_shaded, show_entry):
        self.position_field = position_string, show_shaded, show_entry


    def set_target_value(self, target_value):
        self.target_value = target_value


    def set_target_field(self, target_string, show_shaded, show_entry):
        self.target_field = target_string, show_shaded, show_entry


    def set_divisions(self, divisions):
        self.divisions = divisions


    def set_power_state(self, powered):
        self.powered = powered


    def set_direction(self, direction_cw):
        self.direction_cw = direction_cw


    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            if self.position_rect.contains(ev.pos()):
                print('mouse press position')
                self.position_pressed.emit()
            elif self.target_rect.contains(ev.pos()):
                print('mouse press target')
                self.target_pressed.emit()
            elif self.power_rect.contains(ev.pos()):
                print('mouse press power')
                self.power_pressed.emit()
            elif self.direction_rect.contains(ev.pos()):
                print('mouse press direction')
                self.direction_pressed.emit()


    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.HighQualityAntialiasing)

        self.size = min(self.width(), self.height())
        self.cx = self.size / 2
        self.cy = self.size / 2
        self.cnt_w = self.size * 0.72
        self.cnt_h = self.size * 0.2
        self.cnt_m = self.size * 0.05
        self.sym_w = self.size * 0.08
        self.sym_h = self.size * 0.08
        self.sym_m = self.size * 0.55

        self.position_rect = QRectF(
            self.cx - self.cnt_w / 2,
            self.cy - self.cnt_h - self.cnt_m / 2,
            self.cnt_w,
            self.cnt_h)

        self.target_rect = QRectF(
            self.cx - self.cnt_w / 2,
            self.cy + self.cnt_m / 2,
            self.cnt_w,
            self.cnt_h)

        self.power_rect = QRectF(
            self.cx - self.sym_w / 2,
            self.cy - self.sym_h - self.sym_m / 2,
            self.sym_w,
            self.sym_h)
        
        self.direction_rect = QRectF(
            self.cx - self.sym_w / 2,
            self.cy + self.sym_m / 2,
            self.sym_w,
            self.sym_h)

        self.draw_rose(painter)
        self.draw_targets(painter)
        self.draw_position_arrow(painter)
        self.draw_position_counter(painter)
        self.draw_target_counter(painter)
        self.draw_symbols(painter)


    def draw_rose(self, painter):
        arc_ul = self.rose_margin
        arc_wh = self.size - 2 * self.rose_margin
        radius_outer = arc_wh / 2 - 2
        radius_90 = radius_outer - self.rose_width
        radius_30 = radius_outer - self.rose_width / 2
        radius_10 = radius_outer - self.rose_width / 3

        # Draw arc
        painter.setPen(self.arc_pen)
        painter.drawArc(arc_ul, arc_ul, arc_wh, arc_wh, 0, 16*360)

        # Draw markers
        painter.setPen(self.marker_pen)
        r1 = radius_outer
        for i in range(0, 360, 10):
            if i % 90 == 0:
                r2 = radius_90
            elif i % 30 == 0:
                r2 = radius_30
            else:
                r2 = radius_10
            angle = math.radians(i)
            x1 = self.cx + math.sin(angle) * r1
            y1 = self.cy - math.cos(angle) * r1
            x2 = self.cx + math.sin(angle) * r2
            y2 = self.cy - math.cos(angle) * r2
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))


    def draw_targets(self, painter):
        ring_size = self.rose_margin - self.target_margin * 2
        target_size = ring_size - 4

        # Draw target rings
        painter.setPen(self.target_ring_pen)
        r1 = self.size / 2 - self.rose_margin / 2
        r2 = ring_size / 2
        for div in self.divisions:
            angle = math.radians(div)
            x = self.cx + math.sin(angle) * r1
            y = self.cy - math.cos(angle) * r1
            painter.drawEllipse(QPointF(x, y), r2, r2)

        # Draw current target
        if self.target_value is not None:
            target = self.target_value
            painter.setBrush(self.target_brush)
            painter.setPen(self.target_pen)
            r2 = target_size / 2
            if target is not None:
                angle = math.radians(target)
                x = self.cx + math.sin(angle) * r1
                y = self.cy - math.cos(angle) * r1
                painter.drawEllipse(QPointF(x, y), r2, r2)


    def draw_position_arrow(self, painter):
        # Draw current position
        position = self.position_value
        target = self.target_value
        if position is not None:
            if target is not None and position == target:
                painter.setBrush(self.home_arrow_brush)
                painter.setPen(self.home_arrow_pen)
            else:
                painter.setBrush(self.away_arrow_brush)
                painter.setPen(self.away_arrow_pen)

            angle = math.radians(position)
            dev = math.radians(self.arrow_angle / 2)
            outer_radius = self.size / 2 - self.rose_margin - self.arrow_margin
            inner_radius = outer_radius - self.arrow_length
            r1, r2 = outer_radius, inner_radius
            poly = QPolygonF([
                QPointF(self.cx + math.sin(angle) * r1,
                        self.cy - math.cos(angle) * r1),
                QPointF(self.cx + math.sin(angle + dev) * r2,
                        self.cy - math.cos(angle + dev) * r2),
                QPointF(self.cx + math.sin(angle - dev) * r2,
                        self.cy - math.cos(angle - dev) * r2),
            ])
            painter.drawConvexPolygon(poly)


    def draw_position_counter(self, painter):
        if self.position_value is not None:
            string, shaded, entry = self.position_field
            rect = self.position_rect
            self.position_box.set_text(' ' + string + '°')
            self.position_box.set_entry(entry)
            self.position_box.set_shaded(shaded)
            self.position_box.draw(painter, rect)


    def draw_target_counter(self, painter):
        if self.target_value is not None:
            string, shaded, entry = self.target_field
            rect = self.target_rect
            self.target_box.set_text(' ' + string + '°')
            self.target_box.set_entry(entry)
            self.target_box.set_shaded(shaded)
            self.target_box.draw(painter, rect)


    def draw_symbols(self, painter):
        if self.powered:
            painter.setPen(self.power_on_pen)
        else:
            painter.setPen(self.power_off_pen)

        painter.drawArc(self.power_rect, 135 * 16, 270 * 16)
        p1 = self.power_rect.center()
        p2 = p1 + QPointF(0, -self.power_rect.height() / 2)
        painter.drawLine(p1, p2)

        if self.direction_cw:
            start = -60
            span = 240
        else:
            start = -120
            span = -240

        r = self.direction_rect.width() / 2

        x = math.cos(math.radians(start)) * r
        y = -math.sin(math.radians(start)) * r
        l = r - abs(x)

        p1 = self.direction_rect.center() + QPointF(x, y)
        p2 = p1 + QPointF(0, -l)
        p3 = p1 + QPointF(math.copysign(l, x), 0)

        painter.setPen(self.direction_pen)
        painter.drawArc(self.direction_rect, start * 16, span * 16)
        painter.drawLines([QLineF(p1, p2), QLineF(p1, p3)])
