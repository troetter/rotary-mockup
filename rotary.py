from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from ui import MainWindow
from configuration import Configuration
from presenter import Presenter
from motion import MotionController
from motor import FakeMotor, PololuT249
import ui

import argparse
import sys


def main(config_file, fake=False):
    from PyQt5.QtCore import pyqtRemoveInputHook
    pyqtRemoveInputHook()
    
    app = QApplication(sys.argv)

    ui = MainWindow()
    ui.show()

    config = Configuration(config_file)

    if fake:
        motor = FakeMotor()
    else:
        motor = PololuT249()

    ctrl = MotionController(motor, config)
    pres = Presenter(ctrl, ui)

    sys.exit(app.exec())


if __name__ == '__main__':
    p = argparse.ArgumentParser('rotary')

    p.add_argument('-c', '--config', default='rotary.ini', help='configuration file')
    p.add_argument('-f', '--fake', action='store_true', help='run with fake motor controller')

    p.add_argument('-d', '--debug', action='store_true', help='start in debugger')

    args = p.parse_args()


    if args.debug:
        import pdb
        pdb.set_trace()

    main(config_file=args.config, fake=args.fake)