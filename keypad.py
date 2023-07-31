from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class KeypadWidget(QWidget):
    keypress = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        buttons = [
            [ '1',  '2',  '3' ],
            [ '4',  '5',  '6' ],
            [ '7',  '8',  '9' ],
            [ '.',  '0',  '⌫' ],
            [None, None,  '⏎' ],
        ]

        self.mapper = QSignalMapper()
        self.mapper.mapped[str].connect(self.keypress_handler)

        layout = QGridLayout()
        for r in range(len(buttons)):
            for c in range(len(buttons[r])):
                char = buttons[r][c]
                if char is not None:
                    b = QPushButton(char)
                    font = b.font()
                    font.setFamily('Monospace')
                    font.setPointSize(40)
                    b.setFont(font)
                    b.setFixedSize(75, 75)
                    layout.addWidget(b, r+1, c)
                    b.clicked.connect(self.mapper.map)
                    self.mapper.setMapping(b, char)

        self.setLayout(layout)

    @pyqtSlot(str)
    def keypress_handler(self, text):
        self.keypress.emit(text)
