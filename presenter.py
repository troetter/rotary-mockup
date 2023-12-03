from PyQt5.QtCore import *
from enum import Enum
from enums import TargetMode, MotionState, Direction
from motion import MotionController
from ui import MainWindow
from configuration import Configuration


class Presenter(QObject):
    def __init__(self, controller: MotionController, ui: MainWindow, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.controller = controller
        self.ui = ui
        self.timer = QTimer(self)
        self.timer.setInterval(200)

        self.setup_ui()
        self.setup_connections()
        self.timer.start()


    def setup_connections(self):
        self.timer.timeout.connect(self.timeout)

        self.ui.target_mode_set.connect(self.target_mode_changed)
        self.ui.position_set.connect(self.position_set_in_ui)
        self.ui.abs_target_set.connect(self.abs_target_set)
        self.ui.rel_target_set.connect(self.rel_target_set)
        self.ui.div_target_set.connect(self.div_target_set)
        self.ui.div_parameters_set.connect(self.div_parameters_set)
        self.ui.speed_set.connect(self.speed_set)
        self.ui.cw_pressed.connect(self.cw_pressed)
        self.ui.ccw_pressed.connect(self.ccw_pressed)
        self.ui.power_pressed.connect(self.power_pressed)
        self.ui.start_stop_pressed.connect(self.start_stop_pressed)


    @pyqtSlot(TargetMode)
    def target_mode_changed(self, mode):
        self.controller.event_target_mode_set(mode)
        if mode == TargetMode.ABSOLUTE:
            self.update_abs_target()
        elif mode == TargetMode.RELATIVE:
            self.update_rel_target()
        elif mode == TargetMode.DIVISION:
            self.update_div_target()
        self.update_divs()
        self.update_motion_state()
        print(f'mode changed to {mode}')


    @pyqtSlot(float)
    def position_set_in_ui(self, position):
        self.controller.event_position_set(position)
        self.update_position()
        self.update_motion_state()
        print(f'position changed to {position}')


    @pyqtSlot(float)
    def abs_target_set(self, target):
        self.controller.event_target_set(target)
        self.update_abs_target()
        self.update_motion_state()
        print(f'absolute target set to {target}')


    @pyqtSlot(float)
    def rel_target_set(self, target):
        self.controller.event_target_set(target)
        self.update_rel_target()
        self.update_motion_state()
        print(f'relative target set to {target}')


    @pyqtSlot(int)
    def div_target_set(self, target):
        self.controller.event_target_set(target - 1)
        self.update_div_target()
        self.update_motion_state()
        print(f'division target set to {target}')


    @pyqtSlot(int, float, float)
    def div_parameters_set(self, num_divs, start_angle, extent):
        self.controller.event_division_set(num_divs, start_angle, extent)
        self.update_divs()
        self.update_div_target()
        self.update_motion_state()
        print(f'division parameters set; {num_divs}, {start_angle}, {extent}')


    @pyqtSlot(float)
    def speed_set(self, speed):
        self.controller.event_speed_set(speed)
        self.update_speed()
        print(f'speed set to {speed}')


    @pyqtSlot()
    def cw_pressed(self):
        self.controller.event_direction_set(Direction.CW)
        self.update_direction()
        if self.controller.get_target_mode() == TargetMode.RELATIVE:
            self.update_rel_target()
        print('direction clockwise')


    @pyqtSlot()
    def ccw_pressed(self):
        self.controller.event_direction_set(Direction.CCW)
        self.update_direction()
        if self.controller.get_target_mode() == TargetMode.RELATIVE:
            self.update_rel_target()
        print('direction counter-clockwise')


    @pyqtSlot()
    def power_pressed(self):
        self.controller.event_power()
        self.update_progress()
        self.update_motion_state()
        print('power pressed')


    @pyqtSlot()
    def start_stop_pressed(self):
        self.controller.event_start_stop()
        self.update_progress()
        self.update_motion_state()
        print('start/stop pressed')


    @pyqtSlot()
    def timeout(self):
        self.controller.event_periodic()
        self.update_position()
        self.update_progress()
        self.update_motion_state()
        if self.controller.get_target_mode() == TargetMode.RELATIVE:
            self.update_rel_target()
        state = self.controller.get_motion_state()
        moving_states = [MotionState.MOVING, MotionState.STOPPING]
        if state in moving_states:
            self.timer.setInterval(20)
        else:
            self.timer.setInterval(200)


    def setup_ui(self):
        self.old_target_mode = None
        self.update_target_mode()

        self.old_position = None
        self.update_position()

        self.old_abs_target = None
        self.update_abs_target()

        self.old_rel_target = None
        self.update_rel_target()

        self.old_div_target = None
        self.update_div_target()

        self.old_divs = None
        self.update_divs()

        self.old_div_parameters = None
        self.update_div_parameters()

        self.old_speed = None
        self.update_speed()

        self.old_direction = None
        self.update_direction()

        self.old_motion_state = None
        self.update_motion_state()

        self.old_progress = None
        self.update_progress()


    def update_target_mode(self):
        target_mode = self.controller.get_target_mode()
        if target_mode != self.old_target_mode:
            self.ui.target_mode_updated(target_mode)
        self.old_target_mode = target_mode


    def update_position(self):
        position = self.controller.get_position_angle()
        if position != self.old_position:
            self.ui.position_updated(position)
        self.old_position = position


    def update_abs_target(self):
        target = self.controller.get_abs_target()
        if target != self.old_abs_target:
            self.ui.abs_target_updated(target)
        self.old_abs_target = target


    def update_rel_target(self):
        target = self.controller.get_rel_target()
        if target != self.old_rel_target:
            abs_angle, rel_angle = target
            self.ui.rel_target_updated(abs_angle, rel_angle)
        self.old_rel_target = target


    def update_div_target(self):
        target = self.controller.get_div_target()
        if target != self.old_div_target:
            angle, index = target
            self.ui.div_target_updated(angle, index + 1)
        self.old_div_target = target


    def update_divs(self):
        divs = self.controller.get_divs()
        if divs != self.old_divs:
            self.ui.divs_updated(divs)
        self.old_divs = divs


    def update_div_parameters(self):
        params = self.controller.get_div_parameters()
        if params != self.old_div_parameters:
            num_divs, start_angle, extent = params
            self.ui.div_parameters_updated(num_divs, start_angle, extent)
        self.old_div_params = params


    def update_speed(self):
        speed = self.controller.get_speed()
        if speed != self.old_speed:
            self.ui.speed_updated(speed)
        self.old_speed = speed


    def update_direction(self):
        direction = self.controller.get_direction()
        if direction != self.old_direction:
            self.ui.direction_updated(direction)
        self.old_direction = direction


    def update_motion_state(self):
        motion_state = self.controller.get_motion_state()
        if motion_state != self.old_motion_state:
            self.ui.motion_state_updated(motion_state)
        self.old_motion_state = motion_state


    def update_progress(self):
        progress = self.controller.get_progress()
        if progress != self.old_progress:
            enabled, value = progress
            self.ui.progress_updated(enabled, value)
        self.old_progress = progress
