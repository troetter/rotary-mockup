from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from ui_elements import LabeledBox

class ModeSelectWidget(QWidget):
    item_pressed = pyqtSignal(str)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pen = QPen(Qt.black, 1.5)
        self.modes = []
        self.rects = []


    def set_modes(self, mode_names):
        self.modes = []
        for name in mode_names:
            box = LabeledBox('MODE')
            box.set_label_pen(self.pen)
            box.set_text_pen(self.pen)
            box.set_text(name)
            self.modes.append((name, box))


    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            for name, rect in self.rects:
                if rect.contains(ev.pos()):
                    print('mouse press mode ' + name)
                    self.item_pressed.emit(name)


    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.HighQualityAntialiasing)

        h = self.height()
        top = h * 0.3
        step = h * 0.3
        box_w = self.width()
        box_h = h * 0.2

        self.rects = []
        for i, (name, box) in enumerate(self.modes):
            rect = QRectF(0, top + i * step, box_w, box_h)
            box.draw(painter, rect)
            self.rects.append((name, rect))


class MovementWidget(QWidget):
    mode_pressed = pyqtSignal()
    start_pressed = pyqtSignal()
    stop_pressed = pyqtSignal()
    speed_increase = pyqtSignal()
    speed_decrease = pyqtSignal()
    prev_target = pyqtSignal()
    next_target = pyqtSignal()


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.speed = 0.0
        self.speed_active = True
        self.target_visible = True
        self.target_active = True
        self.start_active = True
        self.stop_active = False

        self.speed_margin = 4

        black = Qt.black
        gray = Qt.gray
        green = QColor(0, 196, 0)
        red = Qt.red

        self.pen_active = QPen(black, 1.5)
        self.brush_inactive = QBrush(gray)
        self.pen_inactive = QPen(gray, 1.5)

        self.speed_fill_brush_active = QBrush(green)
        self.speed_fill_pen_active = QPen(green, 1.5)
        
        self.speed_btn_pen_active = QPen(black, 7.5, cap=Qt.RoundCap)
        self.speed_btn_pen_inactive = QPen(gray, 7.5, cap=Qt.RoundCap)

        self.target_btn_pen_active = QPen(black, 12.5, cap=Qt.RoundCap)
        self.target_btn_pen_inactive = QPen(gray, 12.5, cap=Qt.RoundCap)

        self.start_brush_active = QBrush(green)
        self.start_pen_active = QPen(green, 1.5)

        self.stop_brush_active = QBrush(red)
        self.stop_pen_active = QPen(red, 1.5)

        self.mode_box = LabeledBox('MODE')
        self.mode_box.set_label_pen(self.pen_active)
        self.mode_box.set_text_pen(self.pen_active)


    def set_mode(self, mode):
        self.mode_box.set_text(mode)


    def set_speed(self, speed):
        self.speed = speed


    def set_speed_active(self, active):
        self.speed_active = active


    def set_target_active(self, active):
        self.target_active = active


    def set_target_visible(self, visible):
        self.target_visible = visible


    def set_start_active(self, active):
        self.start_active = active


    def set_stop_active(self, active):
        self.stop_active = active


    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            if self.mode_rect.contains(ev.pos()):
                print('mouse press main menu')
                self.mode_pressed.emit()
            elif self.speed_increase_rect.contains(ev.pos()):
                print('mouse press plus')
                self.speed_increase.emit()
            elif self.speed_decrease_rect.contains(ev.pos()):
                print('mouse press minus')
                self.speed_decrease.emit()
            elif self.prev_rect.contains(ev.pos()):
                print('mouse press prev')
                self.prev_target.emit()
            elif self.next_rect.contains(ev.pos()):
                print('mouse press next')
                self.next_target.emit()
            elif self.start_rect.contains(ev.pos()):
                print('mouse press start')
                self.start_pressed.emit()
            elif self.stop_rect.contains(ev.pos()):
                print('mouse press stop')
                self.stop_pressed.emit()


    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.HighQualityAntialiasing)

        w, h = self.width(), self.height()
        self.mode_rect = QRectF(0, 0, w, h * 0.2)
        self.speed_rect = QRectF(w * 0.12, h * 0.25, w * 0.76, h * 0.1)
        self.prev_rect = QRectF(w * 0.1, h - w * 0.7, w * 0.2, w * 0.2)
        self.next_rect = QRectF(w * 0.7, h - w * 0.7, w * 0.2, w * 0.2)
        self.start_rect = QRectF(w * 0.1, h - w * 0.3, w * 0.2, w * 0.2)
        self.stop_rect = QRectF(w * 0.7, h - w * 0.3, w * 0.2, w * 0.2)

        self.draw_mode(painter)
        self.draw_speed(painter)
        self.draw_target(painter)
        self.draw_start(painter)
        self.draw_stop(painter)


    def draw_mode(self, painter):
        self.mode_box.draw(painter, self.mode_rect)


    def draw_speed(self, painter):
        m = self.speed_margin
        sr = self.speed_rect

        self.speed_decrease_rect = sr.adjusted(0, 0, -sr.width() / 2, 0)
        self.speed_increase_rect = sr.adjusted(sr.width() / 2, 0, 0, 0)

        m_rect = QRectF(sr)
        m_rect.setRight(sr.left() + sr.height())
        p_rect = QRectF(sr)
        p_rect.setLeft(sr.right() - sr.height())
        
        outline_rect = QRectF(sr)
        outline_rect.setLeft(m_rect.right())
        outline_rect.setRight(p_rect.left())
        outline_rect.adjust(m_rect.width() * 0.3, 0, -p_rect.width() * 0.3, 0)
        
        fill_rect = outline_rect.adjusted(m, m, -m, -m)
        fill_rect.setWidth(fill_rect.width() * self.speed)

        if self.speed_active:
            painter.setPen(self.pen_active)
        else:
            painter.setPen(self.pen_inactive)
        painter.drawRect(outline_rect)

        if self.speed_active:
            painter.setPen(self.speed_fill_pen_active)
            painter.setBrush(self.speed_fill_brush_active)
        else:
            painter.setPen(self.pen_inactive)
            painter.setBrush(self.brush_inactive)
        painter.drawRect(fill_rect)

        mtl = m_rect.topLeft()
        mtr = m_rect.topRight()
        mbl = m_rect.bottomLeft()
        mbr = m_rect.bottomRight()

        ptl = p_rect.topLeft()
        ptr = p_rect.topRight()
        pbl = p_rect.bottomLeft()
        pbr = p_rect.bottomRight()

        lines = [
            # minus
            QLineF((mtl + mbl) / 2, (mtr + mbr) / 2),

            # plus
            QLineF((ptl + pbl) / 2, (ptr + pbr) / 2),
            QLineF((ptl + ptr) / 2, (pbl + pbr) / 2),
        ]

        if self.speed_active:
            painter.setPen(self.speed_btn_pen_active)
        else:
            painter.setPen(self.speed_btn_pen_inactive)
        painter.drawLines(lines)


    def draw_target(self, painter):
        if self.target_visible:
            ptl = self.prev_rect.topLeft()
            ptr = self.prev_rect.topRight()
            pbl = self.prev_rect.bottomLeft()
            pbr = self.prev_rect.bottomRight()
            pcc = self.prev_rect.center()
            ptc = (ptl + ptr) / 2
            pbc = (pbl + pbr) / 2
            pcl = (ptl + pbl) / 2

            ntl = self.next_rect.topLeft()
            ntr = self.next_rect.topRight()
            nbl = self.next_rect.bottomLeft()
            nbr = self.next_rect.bottomRight()
            ncc = self.next_rect.center()
            ntc = (ntl + ntr) / 2
            nbc = (nbl + nbr) / 2
            ncr = (ntr + nbr) / 2

            lines = [
                # prev
                QLineF(pcl, ptc),
                QLineF(pcl, pbc),
                QLineF(pcc, ptr),
                QLineF(pcc, pbr),

                # next
                QLineF(ncr, ntc),
                QLineF(ncr, nbc),
                QLineF(ncc, ntl),
                QLineF(ncc, nbl),
            ]

            if self.target_active:
                painter.setPen(self.target_btn_pen_active)
            else:
                painter.setPen(self.target_btn_pen_inactive)
            painter.drawLines(lines)


    def draw_start(self, painter):
        tl = self.start_rect.topLeft()
        tr = self.start_rect.topRight()
        bl = self.start_rect.bottomLeft()
        br = self.start_rect.bottomRight()
        start_poly = QPolygonF([
            tl,
            (tr + br) / 2,
            bl
        ])

        if self.start_active:
            painter.setPen(self.start_pen_active)
            painter.setBrush(self.start_brush_active)
        else:
            painter.setPen(self.pen_inactive)
            painter.setBrush(self.brush_inactive)
        painter.drawConvexPolygon(start_poly)


    def draw_stop(self, painter):
        tl = self.stop_rect.topLeft()
        tr = self.stop_rect.topRight()
        bl = self.stop_rect.bottomLeft()
        br = self.stop_rect.bottomRight()
        f1, f2 = 0.7, 0.3
        stop_poly = QPolygonF([
            tl * f1 + tr * f2,
            tl * f2 + tr * f1,
            tr * f1 + br * f2,
            tr * f2 + br * f1,
            br * f1 + bl * f2,
            br * f2 + bl * f1,
            bl * f1 + tl * f2,
            bl * f2 + tl * f1,

        ])

        if self.stop_active:
            painter.setPen(self.stop_pen_active)
            painter.setBrush(self.stop_brush_active)
        else:
            painter.setPen(self.pen_inactive)
            painter.setBrush(self.brush_inactive)
        painter.drawConvexPolygon(stop_poly)


