from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class ModeSelectWidget(QWidget):
    move_pressed = pyqtSignal()


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pen = QPen(Qt.black, 1.5)

        self.modes = [
            ('MOVE', self.move_pressed, 0.3),
        ]


    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            for rect, text, sig in self.rects:
                if rect.contains(ev.pos()):
                    print('mouse press ' + text)
                    sig.emit()


    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.HighQualityAntialiasing)

        w, h = self.width(), self.height()
        text_height = h * 0.1

        font = painter.font()
        font.setFamily('Monospace')
        font.setPixelSize(int(text_height))
        painter.setFont(font)
        painter.setPen(self.pen)

        self.rects = []
        for text, sig, y_offset in self.modes:
            rect = QRectF(0, h * y_offset, w, text_height)
            painter.drawText(rect, Qt.AlignCenter, text)
            self.rects.append((rect, text, sig))


class MoveWidget(QWidget):
    mode_pressed = pyqtSignal()
    start_pressed = pyqtSignal()
    stop_pressed = pyqtSignal()
    speed_increase = pyqtSignal()
    speed_decrease = pyqtSignal()


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.speed = 0.0
        self.speed_active = True
        self.start_active = True
        self.stop_active = False

        self.speed_margin = 4

        black = Qt.black
        gray = Qt.gray
        green = QColor(0, 196, 0)
        red = Qt.red

        self.mode_string = "MOVE"

        self.pen_active = QPen(black, 1.5)
        self.brush_inactive = QBrush(gray)
        self.pen_inactive = QPen(gray, 1.5)

        self.speed_fill_brush_active = QBrush(green)
        self.speed_fill_pen_active = QPen(green, 1.5)
        
        self.speed_btn_pen_active = QPen(black, 7.5, cap=Qt.RoundCap)
        self.speed_btn_pen_inactive = QPen(gray, 7.5, cap=Qt.RoundCap)

        self.start_brush_active = QBrush(green)
        self.start_pen_active = QPen(green, 1.5)

        self.stop_brush_active = QBrush(red)
        self.stop_pen_active = QPen(red, 1.5)


    def set_speed(self, speed):
        self.speed = speed


    def set_speed_active(self, active):
        self.speed_active = active


    def set_start_active(self, active):
        self.start_active = active


    def set_stop_active(self, active):
        self.stop_active = active


    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            if self.mode_rect.contains(ev.pos()):
                print('mouse press mode')
                self.mode_pressed.emit()
            elif self.start_rect.contains(ev.pos()):
                print('mouse press start')
                self.start_pressed.emit()
            elif self.stop_rect.contains(ev.pos()):
                print('mouse press stop')
                self.stop_pressed.emit()
            elif self.speed_increase_rect.contains(ev.pos()):
                print('mouse press plus')
                self.speed_increase.emit()
            elif self.speed_decrease_rect.contains(ev.pos()):
                print('mouse press minus')
                self.speed_decrease.emit()


    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.HighQualityAntialiasing)

        w, h = self.width(), self.height()
        self.mode_rect = QRectF(0, 0, w, h * 0.2)
        self.speed_rect = QRectF(w * 0.12, h * 0.45, w * 0.76, h * 0.1)
        self.start_rect = QRectF(w * 0.1, h - w * 0.3, w * 0.2, w * 0.2)
        self.stop_rect = QRectF(w * 0.7, h - w * 0.3, w * 0.2, w * 0.2)

        self.draw_mode(painter)
        self.draw_speed(painter)
        self.draw_buttons(painter)


    def draw_mode(self, painter):
        mode_px = self.mode_rect.height() / 2
        font = painter.font()
        font.setFamily('Monospace')
        font.setPixelSize(int(mode_px))
        painter.setFont(font)
        painter.setPen(self.pen_active)
        painter.drawText(self.mode_rect, Qt.AlignCenter, self.mode_string)


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


    def draw_buttons(self, painter):
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

        tl = self.stop_rect.topLeft()
        tr = self.stop_rect.topRight()
        bl = self.stop_rect.bottomLeft()
        br = self.stop_rect.bottomRight()
        heavy, light = 0.7, 0.3
        stop_poly = QPolygonF([
            tl * heavy + tr * light,
            tl * light + tr * heavy,
            tr * heavy + br * light,
            tr * light + br * heavy,
            br * heavy + bl * light,
            br * light + bl * heavy,
            bl * heavy + tl * light,
            bl * light + tl * heavy,

        ])

        if self.stop_active:
            painter.setPen(self.stop_pen_active)
            painter.setBrush(self.stop_brush_active)
        else:
            painter.setPen(self.pen_inactive)
            painter.setBrush(self.brush_inactive)
        painter.drawConvexPolygon(stop_poly)
