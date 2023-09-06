from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from position import PositionWidget
from division import DivisionWidget
from keypad import KeypadWidget
from mode import ModeSelectWidget, MovementWidget
from presenter import Presenter
from motion import Tmc5160Controller, FakeMotorController

import argparse
import configparser
import os
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

        self.division = DivisionWidget()
        self.addWidget(self.division)

    def clear(self):
        self.setCurrentIndex(0)

    def show_position(self):
        self.setCurrentIndex(1)

    def show_division(self):
        self.setCurrentIndex(2)


class RightStack(Stack):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.addWidget(QWidget())

        self.main_menu = ModeSelectWidget()
        self.addWidget(self.main_menu)

        self.mode_move = MovementWidget()
        self.addWidget(self.mode_move)

        self.position_keypad = KeypadWidget()
        self.addWidget(self.position_keypad)

        self.target_keypad = KeypadWidget()
        self.addWidget(self.target_keypad)

    def clear(self):
        self.setCurrentIndex(0)

    def show_main_menu(self):
        self.setCurrentIndex(1)

    def show_movement(self):
        self.setCurrentIndex(2)

    def show_position_keypad(self):
        self.setCurrentIndex(3)

    def show_target_keypad(self):
        self.setCurrentIndex(4)


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


def main(config_file, window=False, fake=False):
    if not os.path.isfile(config_file):
        raise RuntimeError('config file cannot be found')

    config = configparser.ConfigParser()
    config.read(config_file)

    app = QApplication(sys.argv)

    win = MainWindow(window)
    win.show()

    if fake:
        ctrl = FakeMotorController(config)
    else:
        ctrl = Tmc5160Controller(config)

    pres = Presenter(ctrl, win.left_stack, win.right_stack)

    sys.exit(app.exec())


if __name__ == '__main__':
    p = argparse.ArgumentParser('rotary')

    p.add_argument('-c', '--config', default='rotary.ini', help='configuration file')
    p.add_argument('-w', '--window', action='store_true', help='run in windowed mode')
    p.add_argument('-f', '--fake', action='store_true', help='run with fake motor controller')

    p.add_argument('-d', '--debug', action='store_true', help='start in debugger')

    args = p.parse_args()


    if args.debug:
        import pdb
        pdb.set_trace()

    main(config_file=args.config, window=args.window, fake=args.fake)