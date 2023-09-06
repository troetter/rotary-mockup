from PyQt5.QtCore import *
from enum import Enum


class MovementMode(Enum):
    MANUAL_MOVE = 'MANUAL'
    DIVISION = 'DIVISION'


class MotorMode(Enum):
    UNPOWERED_IDLE = 1
    POWERED_IDLE = 2
    MOVING = 3


class InterfaceMode(Enum):
    READY = 1
    DATA_ENTRY = 2


class AngleField(object):
    def __init__(self, value=0.0, minimum=0.0, maximum=359.999, num_decimal=3, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = value
        self.minimum = minimum
        self.maximum = maximum
        self.num_decimal = num_decimal
        self.num_integer = max(len(str(int(minimum))), len(str(int(maximum))))
        self.entry = False
        self.int_part = None
        self.decimal_separator_pressed = False
        self.frac_part = None


    def start_entering(self):
        self.old_value = self.value
        self.entry = True
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
            if self.int_part is None:
                self.int_part = '0'
        elif self.decimal_separator_pressed:
            if self.frac_part is None:
                self.frac_part = character
            elif len(self.frac_part) < self.num_decimal:
                i = self.int_part
                f = self.frac_part + character
                if float(f'{i}.{f}') <= self.maximum:
                    self.frac_part += character
        else:
            if self.int_part is None or self.int_part == '0':
                self.int_part = character
            elif int(self.int_part + character) <= self.maximum:
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

        self.entry = not done
        return done


    def set_value(self, value):
        rounded = round(value, self.num_decimal)
        if rounded < self.minimum or rounded > self.maximum:
            raise ValueError('Value out of range')
        self.value = rounded


    def get_value(self):
        return self.value


    def get_value_field(self):
        if self.entry:
            nothing_entered = (
                self.int_part is None and 
                self.frac_part is None and
                not self.decimal_separator_pressed)

            if nothing_entered:
                v = round(self.old_value, self.num_decimal)
                f = self.num_decimal
                w = self.num_integer + self.num_decimal + 1
                string = f'{v:{w}.{f}f}'
                shaded = True
            else:
                if self.int_part is not None:
                    i = self.int_part
                else:
                    i = ''
                if self.decimal_separator_pressed:
                    d = '.'
                else:
                    d = ' '
                if self.frac_part is not None:
                    f = self.frac_part
                else:
                    f = ''
                ni = self.num_integer
                nf = self.num_decimal
                string = f'{i : >{ni}}{d}{f : <{nf}}'
                shaded = False
        else:
            v = round(self.value, self.num_decimal)
            f = self.num_decimal
            w = self.num_integer + self.num_decimal + 1
            string = f'{v:{w}.{f}f}'
            shaded = False

        return string, shaded, self.entry


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

        self.position_field = AngleField(value=0.0)

        self.current_target_field = AngleField(value=0.0)
        self.divisions = []

        self.powered = False
        self.direction_cw = True

        self.movement_mode = MovementMode.MANUAL_MOVE
        self.motor_mode = MotorMode.UNPOWERED_IDLE
        self.interface_mode = InterfaceMode.READY
        
        self.timer = QTimer(self)
        self.timer.setInterval(25)

        self.left_stack.show_position()
        self.right_stack.show_movement()

        self.setup_connections()
        self.update_position_widget()
        self.update_movement_widget()


    def setup_connections(self):
        self.position_widget.position_pressed.connect(
            self.position_pressed)

        self.position_widget.target_pressed.connect(
            self.target_pressed)

        self.position_widget.power_pressed.connect(
            self.power_pressed)

        self.position_widget.direction_pressed.connect(
            self.direction_pressed)

        self.main_menu_widget.item_pressed.connect(
            self.menu_item_pressed)

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
        self.main_menu_widget.set_modes([x.value for x in MovementMode])
        self.right_stack.show_main_menu()
        self.left_stack.clear()


    def switch_to_mode_manual(self):
        self.movement_mode = MovementMode.MANUAL_MOVE
        self.right_stack.show_movement()
        self.left_stack.show_position()
        self.update_movement_widget()
        self.update_position_widget()


    def switch_to_mode_division(self):
        self.movement_mode = MovementMode.DIVISION
        if self.divisions:
            self.right_stack.show_movement()
            self.left_stack.show_position()
            self.update_movement_widget()
            self.update_position_widget()
        else:
            self.right_stack.clear()
            self.left_stack.show_division()


    def update_position_widget(self):
        powered = self.motor_mode != MotorMode.UNPOWERED_IDLE
        pos_val = self.position_field.get_value()
        pos_str, pos_shd, pos_ent = self.position_field.get_value_field()
        tgt_val = self.current_target_field.get_value()
        tgt_str, tgt_shd, tgt_ent = self.current_target_field.get_value_field()
        if self.movement_mode == MovementMode.DIVISION:
            divs = self.divisions
        else:
            divs = []

        self.position_widget.set_position_value(pos_val)
        self.position_widget.set_position_field(pos_str, pos_shd, pos_ent)
        self.position_widget.set_target_value(tgt_val)
        self.position_widget.set_target_field(tgt_str, tgt_shd, tgt_ent)
        self.position_widget.set_divisions(divs)
        self.position_widget.set_power_state(powered)
        self.position_widget.set_direction(self.direction_cw)

        self.position_widget.update()


    def update_movement_widget(self):
        mode_text = self.movement_mode.value
        speed = self.motor_controller.get_speed()
        target_visible = self.movement_mode == MovementMode.DIVISION
        idle = self.idle()
        startable = self.startable()
        stoppable = self.motor_mode == MotorMode.MOVING

        self.move_widget.set_mode(mode_text)
        self.move_widget.set_speed(speed)
        self.move_widget.set_speed_active(idle)
        self.move_widget.set_target_visible(target_visible)
        self.move_widget.set_target_active(idle)
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
        pos = self.position_field.get_value()
        tgt = self.current_target_field.get_value()
        return all([
            self.motor_mode == MotorMode.POWERED_IDLE,
            self.interface_mode == InterfaceMode.READY,
            pos != tgt])


    @pyqtSlot()
    def position_pressed(self):
        if self.idle():
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
            self.motor_controller.set_power_on()
        else:
            self.motor_mode = MotorMode.UNPOWERED_IDLE
            self.motor_controller.set_power_off()
        self.update_position_widget()
        self.update_movement_widget()



    @pyqtSlot()
    def direction_pressed(self):
        if self.idle():
            self.direction_cw = not self.direction_cw
            self.update_position_widget()


    @pyqtSlot(str)
    def menu_item_pressed(self, item):
        if item == MovementMode.MANUAL_MOVE.value:
            self.switch_to_mode_manual()
        elif item == MovementMode.DIVISION.value:
            self.switch_to_mode_division()
        else:
            msg = f'Invalid main menu item selected ({item})'
            raise RuntimeError(msg)


    @pyqtSlot()
    def main_menu_pressed(self):
        if self.idle():
            self.switch_to_main_menu()


    @pyqtSlot()
    def start_pressed(self):
        if self.startable():
            pos = self.position_field.get_value()
            tgt = self.current_target_field.get_value()
            self.motor_controller.set_position(pos)
            self.motor_controller.set_target(tgt)
            self.motor_controller.move(self.direction_cw)
            self.motor_mode = MotorMode.MOVING
            self.timer.start()
            self.update_position_widget()
            self.update_movement_widget()


    @pyqtSlot()
    def stop_pressed(self):
        if self.motor_mode == MotorMode.MOVING:
            self.motor_controller.stop()
            pos = self.motor_controller.get_position()
            self.position_field.set_value(pos)
            self.motor_mode = MotorMode.POWERED_IDLE
            self.timer.stop()
            self.update_position_widget()
            self.update_movement_widget()


    @pyqtSlot()
    def speed_increase_pressed(self):
        if self.idle():
            self.motor_controller.increase_speed()
            self.update_movement_widget()


    @pyqtSlot()
    def speed_decrease_pressed(self):
        if self.idle():
            self.motor_controller.decrease_speed()
            self.update_movement_widget()


    @pyqtSlot()
    def timeout(self):
        if self.motor_mode == MotorMode.MOVING:
            if not self.motor_controller.moving():
                self.timer.stop()
                self.motor_mode = MotorMode.POWERED_IDLE
                self.update_movement_widget()

            pos = self.motor_controller.get_position()
            self.position_field.set_value(pos)
            self.update_position_widget()
        else:
            self.timer.stop()


    @pyqtSlot(str)
    def handle_position_keypad(self, str):
        done = self.position_field.key_pressed(str)
        self.update_position_widget()
        if done:
            self.interface_mode = InterfaceMode.READY
            self.right_stack.show_movement()
            self.update_movement_widget()


    @pyqtSlot(str)
    def handle_target_keypad(self, str):
        done = self.current_target_field.key_pressed(str)
        self.update_position_widget()
        if done:
            self.interface_mode = InterfaceMode.READY
            self.right_stack.show_movement()
            self.update_movement_widget()
