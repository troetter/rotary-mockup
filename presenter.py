from PyQt5.QtCore import *
from enum import Enum


class MovementMode(Enum):
    MANUAL_MOVE = 1
    DIVISION = 2


class MotorMode(Enum):
    UNPOWERED_IDLE = 1
    POWERED_IDLE = 2
    MOVING = 3


class InterfaceMode(Enum):
    READY = 1
    DATA_ENTRY = 2


class AngleField(object):
    def __init__(self, value=None, uncertain=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = value
        self.uncertain = uncertain
        self.num_decimals = 3
        self.int_part = None
        self.decimal_separator_pressed = False
        self.frac_part = None


    def start_entering(self):
        self.old_value = self.value
        self.uncertain = True
        self.int_part = None
        self.decimal_separator_pressed = False
        self.frac_part = None


    def key_pressed(self, character):
        if len(character) != 1 or character not in '0123456789.⌫⏎':
            msg = 'Bad character keypress: ' + character
            raise RuntimeError(msg)

        done = False
        if character == '⏎':
            done = True
        elif character == '⌫':
            if self.decimal_separator_pressed:
                if self.frac_part is None:
                    self.decimal_separator_pressed = False
                elif len(self.frac_part) > 1:
                    self.frac_part = self.frac_part[:-1]
                else:
                    self.frac_part = None
            else:
                if self.int_part is not None and len(self.int_part) > 1:
                    self.int_part = self.int_part[:-1]
                else:
                    self.int_part = None
        elif character == '.':
            self.decimal_separator_pressed = True
        elif self.decimal_separator_pressed:
            if character in '0123456789':
                if self.frac_part is None:
                    self.frac_part = character
                elif len(self.frac_part) < self.num_decimals:
                    self.frac_part += character
        else:
            if self.int_part is None or self.int_part == '0':
                self.int_part = character
            elif int(self.int_part) < 36 and character in '0123456789':
                self.int_part += character

        return self.validate_input(done)


    def validate_input(self, done):
        nothing_entered = (self.int_part is None and 
                           self.frac_part is None and
                           not self.decimal_separator_pressed)

        if nothing_entered:
            self.value = self.old_value
        else:
            i = self.int_part if self.int_part is not None else '0'
            f = self.frac_part if self.frac_part is not None else '0'
            self.value = float(f'{i}.{f}')

        self.uncertain = not done
        return done
    
    def get_position(self):
        return self.value

    def get_uncertainty(self):
        if self.uncertain:
            if self.int_part is None:
                valid_int = 0
            else:
                valid_int = len(self.int_part)
            if self.frac_part is None:
                valid_frac = 0
            else:
                valid_frac = len(self.frac_part)
        else:
            valid_int = 3
            valid_frac = self.num_decimals

        return (self.uncertain,
                self.decimal_separator_pressed,
                valid_int,
                valid_frac)

    def set_position(self, position, uncertain=False):
        self.value = position


class Presenter(QObject):
    def __init__(self, controller, left_stack, right_stack, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.motor_controller = controller
        self.left_stack = left_stack
        self.right_stack = right_stack

        self.position_widget = left_stack.position
        self.main_menu_widget = right_stack.main_menu
        self.move_widget = right_stack.mode_move
        self.position_keypad = right_stack.position_keypad
        self.target_keypad = right_stack.target_keypad

        self.position = 0.0
        self.position_field = AngleField(value=self.position,
                                         uncertain=True)

        self.current_target = None
        self.current_target_field = AngleField(value=self.current_target,
                                               uncertain=True)
        self.targets = []

        self.powered = False
        self.direction_cw = True

        self.movement_mode = MovementMode.MANUAL_MOVE
        self.motor_mode = MotorMode.UNPOWERED_IDLE
        self.interface_mode = InterfaceMode.READY
        
        self.timer = QTimer(self)
        self.timer.setInterval(100)

        self.left_stack.show_position()
        self.right_stack.show_mode_move()

        self.setup_connections()
        self.update_position_widget()
        self.update_move_widget()


    def setup_connections(self):
        self.position_widget.position_pressed.connect(
            self.position_pressed)

        self.position_widget.target_pressed.connect(
            self.target_pressed)

        self.position_widget.power_pressed.connect(
            self.power_pressed)

        self.position_widget.direction_pressed.connect(
            self.direction_pressed)

        self.main_menu_widget.move_pressed.connect(
            self.menu_move_pressed)

        self.move_widget.mode_pressed.connect(
            self.main_menu_pressed)

        self.move_widget.start_pressed.connect(
            self.start_pressed)

        self.move_widget.stop_pressed.connect(
            self.stop_pressed)

        self.move_widget.speed_increase.connect(
            self.speed_increase_pressed)

        self.move_widget.speed_decrease.connect(
            self.speed_decrease_pressed)

        self.position_keypad.keypress.connect(
            self.handle_position_keypad)

        self.target_keypad.keypress.connect(
            self.handle_target_keypad)

        self.timer.timeout.connect(
            self.timeout)


    def switch_to_main_menu(self):
        #self.movement_mode = MovementMode.MANUAL_MOVE
        self.right_stack.show_main_menu()
        self.left_stack.clear()

    def switch_to_mode_move(self):
        self.movement_mode = MovementMode.MANUAL_MOVE
        self.right_stack.show_mode_move()
        self.left_stack.show_position()


    def update_position_widget(self):
        powered = self.motor_mode != MotorMode.UNPOWERED_IDLE

        self.position_widget.set_position(self.position_field)
        self.position_widget.set_target(self.current_target_field)
        self.position_widget.set_power_state(powered)
        self.position_widget.set_direction(self.direction_cw)

        self.position_widget.update()


    def update_move_widget(self):
        speed = self.motor_controller.get_speed()
        idle = self.idle()
        startable = self.startable()
        stoppable = self.motor_mode == MotorMode.MOVING

        self.move_widget.set_speed(speed)
        self.move_widget.set_speed_active(idle)
        self.move_widget.set_start_active(startable)
        self.move_widget.set_stop_active(stoppable)
        self.move_widget.update()


    def idle(self):
        motor_idle = self.motor_mode in [MotorMode.UNPOWERED_IDLE,
                                         MotorMode.POWERED_IDLE]

        interface_ready = self.interface_mode == InterfaceMode.READY
        return motor_idle and interface_ready


    def powered_idle(self):
        powered_idle = self.motor_mode == MotorMode.POWERED_IDLE
        interface_ready = self.interface_mode == InterfaceMode.READY
        return powered_idle and interface_ready


    def startable(self):
        return all([
            self.motor_mode == MotorMode.POWERED_IDLE,
            self.interface_mode == InterfaceMode.READY,
            not self.position_field.uncertain,
            not self.current_target_field.uncertain])


    @pyqtSlot()
    def position_pressed(self):
        if self.powered_idle():
            self.interface_mode = InterfaceMode.DATA_ENTRY

            self.right_stack.show_position_keypad()
            self.position_field.start_entering()

            self.update_position_widget()


    @pyqtSlot()
    def target_pressed(self):
        if self.idle():
            self.interface_mode = InterfaceMode.DATA_ENTRY

            self.right_stack.show_target_keypad()
            self.current_target_field.start_entering()

            self.update_position_widget()


    @pyqtSlot()
    def power_pressed(self):
        if self.motor_mode == MotorMode.UNPOWERED_IDLE:
            self.motor_mode = MotorMode.POWERED_IDLE
        else:
            self.position_field.uncertain = True
            self.motor_mode = MotorMode.UNPOWERED_IDLE
        self.update_position_widget()
        self.update_move_widget()


    @pyqtSlot()
    def direction_pressed(self):
        if self.idle():
            self.direction_cw = not self.direction_cw
            self.update_position_widget()


    @pyqtSlot()
    def menu_move_pressed(self):
        self.switch_to_mode_move()


    @pyqtSlot()
    def main_menu_pressed(self):
        if self.idle():
            self.switch_to_main_menu()


    @pyqtSlot()
    def start_pressed(self):
        if self.startable():
            pos = self.position_field.get_position()
            tgt = self.current_target_field.get_position()
            self.motor_controller.set_position(pos)
            self.motor_controller.set_target(tgt)
            self.motor_controller.move(self.direction_cw)
            self.motor_mode = MotorMode.MOVING
            self.timer.start()
            self.update_position_widget()
            self.update_move_widget()


    @pyqtSlot()
    def stop_pressed(self):
        if self.motor_mode == MotorMode.MOVING:
            self.motor_controller.stop()
            pos = self.motor_controller.get_position()
            self.position_field.set_position(pos)
            self.motor_mode = MotorMode.POWERED_IDLE
            self.timer.stop()
            self.update_position_widget()
            self.update_move_widget()


    @pyqtSlot()
    def speed_increase_pressed(self):
        if self.idle():
            self.motor_controller.increase_speed()
            self.update_move_widget()


    @pyqtSlot()
    def speed_decrease_pressed(self):
        if self.idle():
            self.motor_controller.decrease_speed()
            self.update_move_widget()


    @pyqtSlot()
    def timeout(self):
        if self.motor_mode == MotorMode.MOVING:
            if not self.motor_controller.moving():
                self.timer.stop()
                self.motor_mode = MotorMode.POWERED_IDLE
                self.update_move_widget()

            pos = self.motor_controller.get_position()
            self.position_field.set_position(pos)
            self.update_position_widget()
        else:
            self.timer.stop()


    @pyqtSlot(str)
    def handle_position_keypad(self, str):
        done = self.position_field.key_pressed(str)
        self.update_position_widget()
        if done:
            self.interface_mode = InterfaceMode.READY
            self.right_stack.show_mode_move()
            self.update_move_widget()


    @pyqtSlot(str)
    def handle_target_keypad(self, str):
        done = self.current_target_field.key_pressed(str)
        self.update_position_widget()
        if done:
            self.interface_mode = InterfaceMode.READY
            self.right_stack.show_mode_move()
            self.update_move_widget()
