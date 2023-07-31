from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from position import PositionWidget
from keypad import KeypadWidget
from mode import ModeSelectWidget, MoveWidget
from presenter import Presenter
from motion import FakeMotorController

import argparse
import sys


class Stack(QStackedWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setContentsMargins(0, 0, 0, 0)


class LeftStack(Stack):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.addWidget(QWidget())

        self.position = PositionWidget()
        self.addWidget(self.position)

    def clear(self):
        self.setCurrentIndex(0)

    def show_position(self):
        self.setCurrentIndex(1)


class RightStack(Stack):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.main_menu = ModeSelectWidget()
        self.addWidget(self.main_menu)

        self.mode_move = MoveWidget()
        self.addWidget(self.mode_move)

        self.position_keypad = KeypadWidget()
        self.addWidget(self.position_keypad)

        self.target_keypad = KeypadWidget()
        self.addWidget(self.target_keypad)

        self.setCurrentIndex(1)

    def show_main_menu(self):
        self.setCurrentIndex(0)

    def show_mode_move(self):
        self.setCurrentIndex(1)

    def show_position_keypad(self):
        self.setCurrentIndex(2)

    def show_target_keypad(self):
        self.setCurrentIndex(3)


class MainWindow(QMainWindow):
    def __init__(self, window=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        width, height = 800, 480
        width_l = height
        width_r = width - width_l

        self.setWindowTitle('Martins snurrbord')
        self.setFixedSize(width, height)

        self.left_stack = LeftStack()
        self.left_stack.setFixedSize(width_l, height)

        self.right_stack = RightStack()
        self.right_stack.setFixedSize(width_r, height)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.left_stack)
        layout.addWidget(self.right_stack)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        if not window:
            self.showFullScreen()


def main(window=False, fake=False):
    app = QApplication(sys.argv)

    win = MainWindow(window)
    win.show()

    if fake:
        ctrl = FakeMotorController()
    else:
        raise NotImplementedError('no real controller yet')

    pres = Presenter(ctrl, win.left_stack, win.right_stack)

    sys.exit(app.exec())


if __name__ == '__main__':
    p = argparse.ArgumentParser('rotary')

    p.add_argument('-w', '--window', action='store_true', help='run in windowed mode')
    p.add_argument('-f', '--fake', action='store_true', help='run with fake motor controller')

    args = p.parse_args()

    main(window=args.window, fake=args.fake)