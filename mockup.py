import math
import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class PositionWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedSize(480, 480)
        self.pos = 0
        self.targets = range(15, 360, 45)
        self.current_target = self.targets[0]

        self.timer = QTimer()
        self.timer.timeout.connect(self.step)
        self.timer.start(50)

    
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.HighQualityAntialiasing)

        # Draw rose
        painter.setPen(QPen(Qt.black, 3))
        painter.drawArc(10, 10, 460, 460, 0, 16*360)
        r1 = 229
        cx, cy = 240, 240
        painter.setPen(QPen(Qt.black, 3))
        for i in range(0, 360, 10):
            if i % 90 == 0:
                r2 = 216
            elif i % 30 == 0:
                r2 = 220
            else:
                r2 = 224
            angle = math.radians(i)
            x1, y1 = cx + math.sin(angle) * r1, cy - math.cos(angle) * r1
            x2, y2 = cx + math.sin(angle) * r2, cy - math.cos(angle) * r2
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        # Draw targets
        painter.setPen(QPen(Qt.black, 1.5))
        r1, r2 = 220, 10
        for tgt in self.targets:
            angle = math.radians(tgt)
            x, y = cx + math.sin(angle) * r1, cy - math.cos(angle) * r1
            painter.drawEllipse(QPointF(x, y), r2, r2)

        # Draw current target
        painter.setBrush(Qt.green)
        painter.setPen(QPen(Qt.green, 1.0))
        r1, r2 = 220, 6
        if self.current_target is not None:
            angle = math.radians(self.current_target)
            x, y = cx + math.sin(angle) * r1, cy - math.cos(angle) * r1
            painter.drawEllipse(QPointF(x, y), r2, r2)

        # Draw current position
        painter.setBrush(Qt.green)
        painter.setPen(QPen(Qt.black, 1.5))
        angle = math.radians(self.pos)
        dev = math.radians(3)
        r1, r2 = 215, 190
        poly = QPolygonF([
            QPointF(cx + math.sin(angle) * r1, cy - math.cos(angle) * r1),
            QPointF(cx + math.sin(angle + dev) * r2, cy - math.cos(angle + dev) * r2),
            QPointF(cx + math.sin(angle - dev) * r2, cy - math.cos(angle - dev) * r2),
        ])
        painter.drawConvexPolygon(poly)

        # Print current position
        w, h = 350, 100
        x, y = cx - w / 2, cy - h
        rect = QRectF(x, y, w, h)
        font = painter.font()
        font.setFamily('Monospace')
        font.setPointSize(48)
        painter.setFont(font)
        pos = f'{self.pos:8.3f}°'
        painter.drawText(rect, Qt.AlignHCenter + Qt.AlignVCenter, pos)

        # Print target position
        x, y = cx - w / 2, cy
        rect = QRectF(x, y, w, h)
        painter.setFont(font)
        tgt = f'{self.current_target:8.3f}°'
        painter.drawText(rect, Qt.AlignHCenter + Qt.AlignVCenter, tgt)

    def step(self):
        self.pos = (self.pos + 0.75) % 360
        self.current_target = self.targets[0]
        for tgt in self.targets:
            if tgt > self.pos:
                self.current_target = tgt
                break
        self.repaint()


class Keypad(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        buttons = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            [',', '0', '±'],
            ['⌫', ' ', '⏎'],
        ]

        layout = QGridLayout()
        for r in range(len(buttons)):
            for c in range(len(buttons[r])):
                b = QPushButton(buttons[r][c])
                font = b.font()
                font.setFamily('Monospace')
                font.setPointSize(40)
                b.setFont(font)
                b.setFixedSize(75, 75)
                layout.addWidget(b, r+1, c)

        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('Martins snurrbord')
        self.setFixedSize(800, 480)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        dial = QDial()
        layout.addWidget(PositionWidget())
        layout.addWidget(Keypad())

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        #self.showFullScreen()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    win = MainWindow()
    win.show()

    sys.exit(app.exec())
