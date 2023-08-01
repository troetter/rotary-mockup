from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

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
        black = Qt.black
        gray = Qt.gray

        self.arc_pen = QPen(black, 3)
        self.marker_pen = QPen(black, 2)

        self.target_ring_pen = QPen(black, 1.5)
        self.target_pen = QPen(green, 1.0)
        self.target_brush = QBrush(green)

        self.certain_arrow_pen = QPen(green, 1.5)
        self.certain_arrow_brush = QBrush(green)
        self.uncertain_arrow_pen = QPen(gray, 1.5)
        self.uncertain_arrow_brush = QBrush(gray)
        self.certain_counter_pen = QPen(black, 1.5)
        self.uncertain_counter_pen = QPen(gray, 1.5)
        self.label_pen = QPen(black, 1.5)

        self.power_off_pen = QPen(gray, 7.5, cap=Qt.RoundCap)
        self.power_on_pen = QPen(green, 7.5, cap=Qt.RoundCap)
        self.direction_pen = QPen(black, 4.5, cap=Qt.RoundCap)

        self.position_field = None
        self.target_field = None
        self.targets = []

        #self.set_position(0.0, True, False, 0, 0)
        #self.current_target = None

        self.powered = False
        self.direction_cw = True


    def set_position(self, position_field):
        self.position_field = position_field


    def set_target(self, target_field):
        self.target_field = target_field


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
        self.cnt_w = self.size * 0.75
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
        for tgt in self.targets:
            angle = math.radians(tgt)
            x = self.cx + math.sin(angle) * r1
            y = self.cy - math.cos(angle) * r1
            painter.drawEllipse(QPointF(x, y), r2, r2)

        # Draw current target
        if self.target_field is not None:
            target = self.target_field.get_position()
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
        if self.position_field is not None:
            value = self.position_field.get_position()
            uncertain, _, _, _ = self.position_field.get_uncertainty()
            if uncertain:
                painter.setBrush(self.uncertain_arrow_brush)
                painter.setPen(self.uncertain_arrow_pen)
            else:
                painter.setBrush(self.certain_arrow_brush)
                painter.setPen(self.certain_arrow_pen)

            angle = math.radians(value)
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
        if self.position_field is not None:
            self.draw_counter(painter,
                              self.position_rect,
                              self.position_field,
                              'POSITION')


    def draw_target_counter(self, painter):
        if self.target_field is not None:
            self.draw_counter(painter,
                              self.target_rect,
                              self.target_field,
                              'TARGET')


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


    def draw_counter(self, painter, rect, field, label):
        label_px = self.cnt_h * 0.25
        counter_px = self.cnt_h * 0.7
        font = painter.font()
        font.setFamily('Monospace')

        font.setPixelSize(int(label_px))
        painter.setFont(font)
        painter.setPen(self.label_pen)
        painter.drawText(rect, Qt.AlignHCenter + Qt.AlignTop, label)

        font.setPixelSize(int(counter_px))
        painter.setFont(font)

        value = field.get_position()
        ret = field.get_uncertainty()
        uncertain, valid_dec_sep, num_valid_int, num_valid_frac = ret

        if value is None:
            val_str = '---.---'
            pad_str = ' ' * len(val_str)
            painter.setPen(self.uncertain_counter_pen)
            painter.drawText(rect,
                             Qt.AlignHCenter + Qt.AlignBottom,
                             ' ' + val_str + ' ')
            painter.setPen(self.certain_counter_pen)
            painter.drawText(rect,
                             Qt.AlignHCenter + Qt.AlignBottom,
                             ' ' + pad_str + '°')

        elif uncertain:
            fraction, integer = math.modf(value)

            int_str = f'{int(integer):3d}'
            if num_valid_int:
                int_str_cert = int_str[-num_valid_int:]
                int_str_uncert = int_str[:-num_valid_int]
            else:
                int_str_cert = ''
                int_str_uncert = int_str
            
            frac_str = f'{int(round(fraction * 1000)):03d}'
            if num_valid_frac:
                frac_str_cert = frac_str[:num_valid_frac]
                frac_str_uncert = frac_str[num_valid_frac:]
            else:
                frac_str_cert = ''
                frac_str_uncert = frac_str
            
            if valid_dec_sep:
                dec_cert = '.'
                dec_uncert = ' '
            else:
                dec_cert = ' '
                dec_uncert = '.'

            str_cert = int_str_cert + dec_cert + frac_str_cert
            pfx_cert = ' ' * len(int_str_uncert)
            sfx_cert = ' ' * len(frac_str_uncert)
            padded_str_cert =  pfx_cert + str_cert + sfx_cert

            int_sfx_uncert = ' ' * len(int_str_cert)
            frac_pfx_uncert = ' ' * len(frac_str_cert)
            mid_uncert = int_sfx_uncert + dec_uncert + frac_pfx_uncert
            padded_str_uncert = int_str_uncert + mid_uncert + frac_str_uncert

            painter.setPen(self.uncertain_counter_pen)
            painter.drawText(rect,
                             Qt.AlignHCenter + Qt.AlignBottom,
                             ' ' + padded_str_uncert + ' ')

            painter.setPen(self.certain_counter_pen)
            painter.drawText(rect,
                             Qt.AlignHCenter + Qt.AlignBottom,
                             ' ' + padded_str_cert + '°')

        else:
            val_str = f'{value:8.3f}°'
            painter.setPen(self.certain_counter_pen)
            painter.drawText(rect, Qt.AlignHCenter + Qt.AlignBottom, val_str)

