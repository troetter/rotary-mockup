from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from enums import TargetMode, MotionState, Direction, DivMode
import math
import sys


green = QColor(0, 196, 0)
red = Qt.red
gray = Qt.gray
black = Qt.black


class Button(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedSize(QSize(64, 64))
        self.margin = 0.2


    def getDrawRect(self):
        w, h = self.width(), self.height()
        m = self.margin
        return QRectF(w * m, h * m, w * (1 - 2 * m), h * (1 - 2 * m))


class EnergizeButton(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.powered = False

        self.power_off_pen = QPen(gray, 7.5, cap=Qt.RoundCap)
        self.power_on_pen = QPen(green, 7.5, cap=Qt.RoundCap)


    def paintEvent(self, e: QPaintEvent):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.HighQualityAntialiasing)

        rect = self.getDrawRect()

        if self.powered:
            painter.setPen(self.power_on_pen)
        else:
            painter.setPen(self.power_off_pen)

        painter.drawArc(rect, 135 * 16, 270 * 16)
        p1 = rect.center()
        p2 = (rect.topLeft() + rect.topRight()) / 2
        painter.drawLine(p1, p2)


class SetupButton(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.wheel_pen = QPen(gray, 5)
        self.cog_pen = QPen(gray, 4, cap=Qt.FlatCap)


    def paintEvent(self, e: QPaintEvent):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.HighQualityAntialiasing)

        cog_rect = self.getDrawRect()
        delta = self.cog_pen.widthF()
        wheel_rect = cog_rect.adjusted(delta, delta, -delta, -delta)

        painter.setPen(self.wheel_pen)
        painter.drawArc(wheel_rect, 0, 360 * 16)

        cogs = 12
        step = 360/cogs
        painter.setPen(self.cog_pen)
        for i in range(cogs):
            start = step * (i * 16 - 4)
            span = step * 8
            painter.drawArc(cog_rect, int(start), int(span))


class StartStopButton(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.enabled = False
        self.start_visible = True

        self.disabled_brush = QBrush(gray)
        self.disabled_pen = QPen(gray, 1.5)

        self.start_brush = QBrush(green)
        self.start_pen = QPen(green, 1.5)

        self.stop_brush = QBrush(red)
        self.stop_pen = QPen(red, 1.5)


    def paintEvent(self, e: QPaintEvent):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.HighQualityAntialiasing)

        rect = self.getDrawRect()

        if self.start_visible:
            painter.setPen(self.start_pen)
            painter.setBrush(self.start_brush)
            poly = self.start_poly(rect)
        else:
            painter.setPen(self.stop_pen)
            painter.setBrush(self.stop_brush)
            poly = self.stop_poly(rect)

        if not self.enabled:
            painter.setPen(self.disabled_pen)
            painter.setBrush(self.disabled_brush)

        painter.drawConvexPolygon(poly)


    def start_poly(self, rect):
        tl = rect.topLeft()
        tr = rect.topRight()
        bl = rect.bottomLeft()
        br = rect.bottomRight()
        return QPolygonF([
            tl,
            (tr + br) / 2,
            bl
        ])


    def stop_poly(self, rect):
        tl = rect.topLeft()
        tr = rect.topRight()
        bl = rect.bottomLeft()
        br = rect.bottomRight()
        f1, f2 = 0.7, 0.3
        return QPolygonF([
            tl * f1 + tr * f2,
            tl * f2 + tr * f1,
            tr * f1 + br * f2,
            tr * f2 + br * f1,
            br * f1 + bl * f2,
            br * f2 + bl * f1,
            bl * f1 + tl * f2,
            bl * f2 + tl * f1,
        ])


class DirectionButton(Button):
    def __init__(self, direction, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.direction = direction
        self.selected = False

        self.selected_pen = QPen(black, 4.5, cap=Qt.RoundCap)
        self.deselected_pen = QPen(gray, 4.5, cap=Qt.RoundCap)


    def paintEvent(self, e: QPaintEvent):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.HighQualityAntialiasing)

        rect = self.getDrawRect()

        if self.direction == Direction.CW:
            start = -60
            span = 240
        else:
            start = -120
            span = -240

        r = rect.width() / 2
        x = math.cos(math.radians(start)) * r
        y = -math.sin(math.radians(start)) * r
        l = r - abs(x)

        p1 = rect.center() + QPointF(x, y)
        p2 = p1 + QPointF(0, -l)
        p3 = p1 + QPointF(math.copysign(l, x), 0)

        if self.selected:
            painter.setPen(self.selected_pen)
        else:
            painter.setPen(self.deselected_pen)
        painter.drawArc(rect, start * 16, span * 16)
        painter.drawLines([QLineF(p1, p2), QLineF(p1, p3)])


class Progress(QProgressBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedHeight(62)

        self.disabled_stylesheet = '''
            QProgressBar {
                border: 1px solid grey;
                border-radius: 3px;
                text-align: center;
                background-color: lightgrey;
            }'''
        self.enabled_stylesheet = '''
            QProgressBar {
                font-size: 36px;
                border: 1px solid grey;
                border-radius: 3px;
                text-align: center;
                background-color: #FF8080;
            }
            QProgressBar::chunk {
                border-radius: 3px;
                background-color: lightgreen;
            }'''

        self.setEnabled(False)


    def setEnabled(self, enabled):
        super().setEnabled(enabled)
        if enabled:
            self.setStyleSheet(self.enabled_stylesheet)
            self.setTextVisible(True)
        else:
            self.setStyleSheet(self.disabled_stylesheet)
            self.setTextVisible(False)


    def setDisabled(self, disabled):
        self.setEnabled(not disabled)


class PositionWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setMinimumWidth(250)
        self.setMinimumHeight(250)

        self.position = 0
        self.current_target = None
        self.targets = []

        self.arc_pen = QPen(black, 3)
        self.marker_pen = QPen(black, 2, cap=Qt.RoundCap)

        self.target_ring_pen = QPen(black, 1.5)
        self.target_pen = QPen(green, 1.0)
        self.target_brush = QBrush(green)

        self.position_pen = QPen(black, 2.5, cap=Qt.RoundCap)


    @pyqtSlot(float)
    def set_position(self, value):
        self.position = value
        self.update()


    @pyqtSlot(list)
    def set_targets(self, targets):
        self.targets = targets
        self.update()


    @pyqtSlot(float)
    def set_current_target(self, value):
        self.current_target = value
        self.update()


    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.HighQualityAntialiasing)

        w, h = self.width(), self.height()
        size = min(w, h)
        cx, cy = w/2, h/2

        bounding_rect = QRectF(cx - size/2, cy - size/2, size, size)

        # Draw rose arc
        m = 5
        draw_rect = bounding_rect.adjusted(m, m, -m, -m)
        painter.setPen(self.arc_pen)
        painter.drawArc(draw_rect, 0, 360*16)

        # Draw rose markers
        painter.setPen(self.marker_pen)
        r1 = draw_rect.width()/2
        radius_90 = r1 - 10
        radius_30 = r1 - 7
        radius_10 = r1 - 4
        for i in range(0, 360, 10):
            if i % 90 == 0:
                r2 = radius_90
            elif i % 30 == 0:
                r2 = radius_30
            else:
                r2 = radius_10
            angle = math.radians(i)
            x1 = cx + math.sin(angle) * r1
            y1 = cy - math.cos(angle) * r1
            x2 = cx + math.sin(angle) * r2
            y2 = cy - math.cos(angle) * r2
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # Draw target rings
        painter.setPen(self.target_ring_pen)
        r1 = size / 2 - 20
        r2 = 15 / 2
        for tgt in self.targets:
            angle = math.radians(tgt)
            x = cx + math.sin(angle) * r1
            y = cy - math.cos(angle) * r1
            painter.drawEllipse(QPointF(x, y), r2, r2)

        # Draw current target
        if self.current_target is not None:
            painter.setBrush(self.target_brush)
            painter.setPen(self.target_pen)
            r2 = 10 / 2
            angle = math.radians(self.current_target)
            x = cx + math.sin(angle) * r1
            y = cy - math.cos(angle) * r1
            painter.drawEllipse(QPointF(x, y), r2, r2)

        # Draw current position
        r1 = draw_rect.width() / 2 - 12
        r2 = draw_rect.width() / 16
        angle = math.radians(self.position)
        x1 = cx + math.sin(angle) * r1
        y1 = cy - math.cos(angle) * r1
        x2 = cx + math.sin(angle) * r2
        y2 = cy - math.cos(angle) * r2
        painter.setPen(self.position_pen)
        painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))


def EnumCombo(enum_type):
    class EnumComboClass(QComboBox):
        itemActivated = pyqtSignal(enum_type)

        def __init__(self, enum_type, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.enum_map = {}
            for i, e in enumerate(enum_type):
                self.enum_map[i] = e
                self.addItem(e.value)
            self.activated.connect(self.activation_slot)
        
        @pyqtSlot(int)
        def activation_slot(self, i):
            self.itemActivated.emit(self.enum_map[i])

    return EnumComboClass(enum_type)


class MainWindow(QMainWindow):
    target_mode_set = pyqtSignal(TargetMode)
    position_set = pyqtSignal(float)
    abs_target_set = pyqtSignal(float)
    rel_target_set = pyqtSignal(float)
    div_target_set = pyqtSignal(int)
    div_parameters_set = pyqtSignal(int, float, float)
    speed_set = pyqtSignal(float)
    cw_pressed = pyqtSignal()
    ccw_pressed = pyqtSignal()
    power_pressed = pyqtSignal()
    start_stop_pressed = pyqtSignal()


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mode_map = {i: m for i, m in enumerate(TargetMode)}

        self.setWindowTitle('Martins snurrbord')
        self.create_widgets()
        self.create_layout()
        self.create_division_dialog()
        self.create_internal_connections()
        self.create_external_signals()

        self.progress.setValue(0)


    @pyqtSlot(TargetMode)
    def target_mode_updated(self, mode):
        self.setup_current_mode(mode)


    @pyqtSlot(float)
    def position_updated(self, value):
        self.position_rose.set_position(value)
        with QSignalBlocker(self.position_spinbox):
            self.position_spinbox.setValue(value)


    @pyqtSlot(float)
    def abs_target_updated(self, value):
        self.position_rose.set_current_target(value)
        with QSignalBlocker(self.abs_tgt_spinbox):
            self.abs_tgt_spinbox.setValue(value)


    @pyqtSlot(float)
    def rel_target_updated(self, abs_angle, rel_angle):
        self.position_rose.set_current_target(abs_angle)
        with QSignalBlocker(self.rel_tgt_spinbox):
            self.rel_tgt_spinbox.setValue(rel_angle)


    @pyqtSlot(float, int)
    def div_target_updated(self, angle, target_num):
        self.position_rose.set_current_target(angle)
        with QSignalBlocker(self.div_tgt_spinbox):
            self.div_tgt_spinbox.setValue(target_num)


    @pyqtSlot(list)
    def divs_updated(self, divs):
        self.position_rose.set_targets(divs)
        with QSignalBlocker(self.div_tgt_spinbox):
            self.div_tgt_spinbox.setRange(1, len(divs))
            self.div_tgt_spinbox.setSuffix(f'/{len(divs)}')


    @pyqtSlot(int, float, float, list)
    def div_parameters_updated(self, num, start, extent):
        with QSignalBlocker(self.div_num_spinbox):
            self.div_num_spinbox.setValue(num)
        with QSignalBlocker(self.div_start_spinbox):
            self.div_start_spinbox.setValue(start)
        with QSignalBlocker(self.div_extent_spinbox):
            self.div_extent_spinbox.setValue(extent)


    @pyqtSlot(float)
    def target_updated(self, value):
        self.position_rose.set_current_target(value)


    @pyqtSlot(Direction)
    def direction_updated(self, direction):
        if direction == Direction.CW:
            self.cw_button.selected = True
            self.ccw_button.selected = False
        else:
            self.cw_button.selected = False
            self.ccw_button.selected = True
        self.cw_button.update()
        self.ccw_button.update()


    @pyqtSlot(float)
    def speed_updated(self, value):
        with QSignalBlocker(self.speed_spinbox):
            self.speed_spinbox.setValue(value)


    @pyqtSlot(MotionState)
    def motion_state_updated(self, state):
        if state == MotionState.UNPOWERED:
            p, e, v = False, False, True
            inp = True
        elif state == MotionState.IDLE:
            p, e, v = True, False, True
            inp = True
        elif state == MotionState.READY_TO_MOVE:
            p, e, v = True, True, True
            inp = True
        elif state == MotionState.MOVING:
            p, e, v = True, True, False
            inp = False
        elif state == MotionState.STOPPING:
            p, e, v = True, False, False
            inp = False

        self.energize_button.powered = p
        self.start_stop_button.enabled = e
        self.start_stop_button.start_visible = v
        self.energize_button.update()
        self.start_stop_button.update()

        fields = [
            self.position_spinbox,
            self.abs_tgt_spinbox,
            self.rel_tgt_spinbox,
            self.div_tgt_spinbox,
            self.speed_spinbox,
            self.cw_button,
            self.ccw_button,
            self.div_setup_button,
        ]
        for f in fields:
            f.setEnabled(inp)


    @pyqtSlot(bool, int)
    def progress_updated(self, enabled, progress):
        self.progress.setEnabled(enabled)
        self.progress.setValue(progress)


    @pyqtSlot(TargetMode)
    def internal_mode_select(self, mode):
        self.setup_current_mode(mode)
        self.target_mode_set.emit(mode)


    @pyqtSlot()
    def show_division_dialog(self):
        if self.division_dialog.exec():
            num = self.div_num_spinbox.value()
            start = self.div_start_spinbox.value()
            extent = self.div_extent_spinbox.value()
            self.div_parameters_set.emit(num, start, extent)


    def setup_current_mode(self, mode):
        setting_map = {
            # (Buddy, target label, dir buttons, setup button)
            TargetMode.ABSOLUTE:
                (self.abs_tgt_spinbox, '&Target angle', True,  False),
            TargetMode.RELATIVE:
                (self.rel_tgt_spinbox, 'Rela&tive angle to move',   True,  False),
            TargetMode.DIVISION:
                (self.div_tgt_spinbox, '&Target div', False, True),
        }

        self.target_widget.setCurrentWidget(self.target_map[mode])
        buddy, tgt_label, dir_btns, setup_btn = setting_map[mode]

        self.target_label.setBuddy(buddy)
        self.target_label.setText(tgt_label)
        self.ccw_button.setVisible(dir_btns)
        self.ccw_button.setEnabled(dir_btns)
        self.cw_button.setVisible(dir_btns)
        self.cw_button.setEnabled(dir_btns)


    def create_widgets(self):
        # Buttons
        self.energize_button = EnergizeButton()
        self.start_stop_button = StartStopButton()
        self.ccw_button = DirectionButton(Direction.CCW)
        self.cw_button = DirectionButton(Direction.CW)
        self.div_setup_button = SetupButton()

        # Progress bar
        self.progress = Progress()

        # Spin Boxes
        self.position_spinbox = QDoubleSpinBox()
        self.position_spinbox.setSuffix('°')
        self.position_spinbox.setDecimals(3)
        self.position_spinbox.setRange(0, 359.999)

        self.speed_spinbox = QDoubleSpinBox()
        self.speed_spinbox.setSuffix('°/s')
        self.speed_spinbox.setDecimals(2)
        self.speed_spinbox.setRange(0.1, 45.0)

        self.abs_tgt_spinbox = QDoubleSpinBox()
        self.abs_tgt_spinbox.setSuffix('°')
        self.abs_tgt_spinbox.setDecimals(3)
        self.abs_tgt_spinbox.setRange(0, 359.999)

        self.rel_tgt_spinbox = QDoubleSpinBox()
        self.rel_tgt_spinbox.setSuffix('°')
        self.rel_tgt_spinbox.setDecimals(3)
        self.rel_tgt_spinbox.setRange(0, 360 * 5000)

        self.div_tgt_spinbox = QSpinBox()
        self.div_tgt_spinbox.setSuffix('/2')
        self.div_tgt_spinbox.setRange(1, 2)
        self.div_tgt_spinbox.setWrapping(True)

        # In division dialog
        self.div_num_spinbox = QSpinBox()
        self.div_num_spinbox.setRange(2, 1000)

        self.div_start_spinbox = QDoubleSpinBox()
        self.div_start_spinbox.setSuffix('°')
        self.div_start_spinbox.setDecimals(3)
        self.div_start_spinbox.setRange(0, 359.999)

        self.div_extent_spinbox = QDoubleSpinBox()
        self.div_extent_spinbox.setSuffix('°')
        self.div_extent_spinbox.setDecimals(3)
        self.div_extent_spinbox.setRange(0.001, 360)

        all_spinboxes = [
            self.position_spinbox,
            self.speed_spinbox,
            self.abs_tgt_spinbox,
            self.rel_tgt_spinbox,
            self.div_tgt_spinbox,
            self.div_num_spinbox,
            self.div_start_spinbox,
            self.div_extent_spinbox,
        ]
        for s in all_spinboxes:
            s.setStyleSheet('''
                QDoubleSpinBox::up-button {
                    width: 24px;
                }
                QDoubleSpinBox::down-button {
                    width: 24px;
                }
                QDoubleSpinBox {
                    font-size: 36px;
                    padding-right: 16px;
                }
                QSpinBox::up-button {
                    width: 24px;
                }
                QSpinBox::down-button {
                    width: 24px;
                }
                QSpinBox {
                    font-size: 36px;
                    padding-right: 16px;
                }
                ''')
            s.setAlignment(Qt.AlignRight)
            s.setFixedHeight(64)
            s.setButtonSymbols(QAbstractSpinBox.NoButtons)

        # Mode switcher
        self.mode_combo = EnumCombo(TargetMode)
        self.mode_combo.setStyleSheet('font-size: 24px')

        # Labels
        self.mode_label = QLabel('&Mode')
        self.mode_label.setBuddy(self.mode_combo)

        self.position_label = QLabel('&Position')
        self.position_label.setBuddy(self.position_spinbox)

        self.target_label = QLabel('&Target')
        self.target_label.setBuddy(self.abs_tgt_spinbox)

        self.speed_label = QLabel('&Speed')
        self.speed_label.setBuddy(self.speed_spinbox)

        # In division dialog
        self.div_num_label = QLabel('&Number of divisions')
        self.div_num_label.setBuddy(self.div_num_spinbox)

        self.div_start_label = QLabel('&Start angle')
        self.div_start_label.setBuddy(self.div_start_spinbox)

        self.div_extent_label = QLabel('E&xtent angle')
        self.div_extent_label.setBuddy(self.div_extent_spinbox)

        all_labels = [
            self.mode_label,
            self.position_label,
            self.target_label,
            self.speed_label,
            self.div_num_label,
            self.div_start_label,
            self.div_extent_label,
        ]
        for l in all_labels:
            l.setStyleSheet('font-size: 16px')
            l.setAlignment(Qt.AlignHCenter)

        # Position rose
        self.position_rose = PositionWidget()


    def create_layout(self):
        # Create the sublayout for the division mode
        div_layout = QGridLayout()
        div_layout.setContentsMargins(0, 0, 0, 0)
        div_layout.addWidget(self.div_setup_button, 0, 0, 1, 1)
        div_layout.addWidget(self.div_tgt_spinbox, 0, 1, 1, 2)
        self.div_widget = QWidget()
        self.div_widget.setLayout(div_layout)

        # Create the target type stack
        self.target_map = {
            TargetMode.ABSOLUTE: self.abs_tgt_spinbox,
            TargetMode.RELATIVE: self.rel_tgt_spinbox,
            TargetMode.DIVISION: self.div_widget,
        }
        self.target_widget = QStackedWidget()
        for t in self.target_map.values():
            self.target_widget.addWidget(t)

        # Top-level layout
        main_layout = QGridLayout()
        row = 0

        # Mode row
        main_layout.addWidget(self.mode_label, row, 0, 1, 3)
        main_layout.addWidget(self.mode_combo, row+1, 0, 1, 3)
        row += 2

        # Position widget
        main_layout.addWidget(self.position_rose, row, 0, 1, 3)
        row += 1

        # Position row
        main_layout.addWidget(self.position_label, row, 0, 1, 3)
        main_layout.addWidget(self.position_spinbox, row+1, 0, 1, 3)
        row += 2

        # Target row
        main_layout.addWidget(self.target_label, row, 0, 1, 3)
        main_layout.addWidget(self.target_widget, row+1, 0, 1, 3)
        row += 2
        
        # Speed/dir row
        main_layout.addWidget(self.speed_label, row, 1)
        main_layout.addWidget(self.ccw_button, row+1, 0)
        main_layout.addWidget(self.speed_spinbox, row+1, 1)
        main_layout.addWidget(self.cw_button, row+1, 2)
        row += 2

        # Bottom row
        main_layout.addWidget(self.energize_button, row, 0)
        main_layout.addWidget(self.progress, row, 1)
        main_layout.addWidget(self.start_stop_button, row, 2)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)


    def create_division_dialog(self):
        dialog = QDialog()
        dialog.setWindowTitle('Division parameters')
        dialog.setModal(Qt.ApplicationModal)

        btn = QDialogButtonBox.Ok

        buttonbox = QDialogButtonBox(btn)
        buttonbox.setStyleSheet('font-size: 16px')
        buttonbox.accepted.connect(dialog.accept)
        buttonbox.rejected.connect(dialog.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.div_num_label)
        layout.addWidget(self.div_num_spinbox)
        layout.addWidget(self.div_start_label)
        layout.addWidget(self.div_start_spinbox)
        layout.addWidget(self.div_extent_label)
        layout.addWidget(self.div_extent_spinbox)
        layout.addWidget(buttonbox)
        dialog.setLayout(layout)

        self.division_dialog = dialog


    def create_internal_connections(self):
        self.mode_combo.itemActivated.connect(self.internal_mode_select)
        self.div_setup_button.pressed.connect(self.show_division_dialog)


    def create_external_signals(self):
        self.position_spinbox.valueChanged.connect(self.position_set)
        self.abs_tgt_spinbox.valueChanged.connect(self.abs_target_set)
        self.rel_tgt_spinbox.valueChanged.connect(self.rel_target_set)
        self.div_tgt_spinbox.valueChanged.connect(self.div_target_set)
        self.speed_spinbox.valueChanged.connect(self.speed_set)
        self.cw_button.clicked.connect(self.cw_pressed)
        self.ccw_button.clicked.connect(self.ccw_pressed)
        self.energize_button.clicked.connect(self.power_pressed)
        self.start_stop_button.clicked.connect(self.start_stop_pressed)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    win = MainWindow()
    win.show()

    sys.exit(app.exec())
