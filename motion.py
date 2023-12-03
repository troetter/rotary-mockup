from enums import MotionState, TargetMode, Direction
from configuration import Configuration
from motor import Motor

class MotionController(object):
    def __init__(self, motor: Motor, config: Configuration):
        self.motor = motor
        self.config = config

        self.motion_state = MotionState.UNPOWERED
        self.target_mode = TargetMode.ABSOLUTE

        self.target_reg = 0

        self.abs_target = 0.0
        self.rel_target = 0.0
        self.div_target = 0
        self.div_parameters = 2, 0, 360
        self.divs = [0, 180]

        self.direction = Direction.CW
        self.speed = self.config.default_speed

        self.setup_motor()


    def event_periodic(self):
        self.motor.update_state()
        self.evaluate_state_transition()


    def event_power(self):
        if self.motion_state == MotionState.UNPOWERED:
            self.motor.set_power_on()
        else:
            self.motor.set_power_off()
        self.evaluate_state_transition()


    def event_start_stop(self):
        valid_states = [
            MotionState.READY_TO_MOVE,
            MotionState.MOVING
        ]

        if self.motion_state not in valid_states:
            raise RuntimeError('Invalid event for state')

        if self.motion_state == MotionState.READY_TO_MOVE:
            self.start_reg = self.motor.get_position()
            tgt_reg = self.target_reg
            speed = self.speed * self.steps_per_deg
            self.motor.start_move_to_position(tgt_reg, speed)
        else:
            self.motor.stop()
        self.evaluate_state_transition()


    def event_position_set(self, position):
        valid_states = [
            MotionState.UNPOWERED,
            MotionState.IDLE,
            MotionState.READY_TO_MOVE,
        ]

        if self.motion_state not in valid_states:
            raise RuntimeError('Invalid event for state')

        motor_pos = self.motor.get_position()
        self.position_anchor = position, motor_pos
        self.calculate_target_reg()
        self.evaluate_state_transition()


    def event_target_mode_set(self, mode):
        valid_states = [
            MotionState.UNPOWERED,
            MotionState.IDLE,
            MotionState.READY_TO_MOVE,
        ]

        if self.motion_state not in valid_states:
            raise RuntimeError('Invalid event for state')

        self.target_mode = mode
        self.calculate_target_reg()
        self.evaluate_state_transition()


    def event_target_set(self, parameter):
        valid_states = [
            MotionState.UNPOWERED,
            MotionState.IDLE,
            MotionState.READY_TO_MOVE,
        ]

        if self.motion_state not in valid_states:
            raise RuntimeError('Invalid event for state')

        if self.target_mode == TargetMode.ABSOLUTE:
            self.abs_target = parameter
        elif self.target_mode == TargetMode.RELATIVE:
            self.rel_target = parameter
        elif self.target_mode == TargetMode.DIVISION:
            self.div_target = parameter

        self.calculate_target_reg()
        self.evaluate_state_transition()


    def event_division_set(self, num_divs, start_angle, extent):
        valid_states = [
            MotionState.UNPOWERED,
            MotionState.IDLE,
            MotionState.READY_TO_MOVE,
        ]

        if self.motion_state not in valid_states:
            raise RuntimeError('Invalid event for state')

        if extent == 360.0:
            d = num_divs
        else:
            d = num_divs - 1
        r = range(num_divs)
        s = start_angle
        e = extent
        self.divs = [(i * e / d + s) % 360.0 for i in r]
        self.div_target = 0
        self.div_parameters = num_divs, start_angle, extent
        self.calculate_target_reg()
        self.evaluate_state_transition()


    def event_direction_set(self, direction):
        valid_states = [
            MotionState.UNPOWERED,
            MotionState.IDLE,
            MotionState.READY_TO_MOVE,
        ]

        if self.motion_state not in valid_states:
            raise RuntimeError('Invalid event for state')

        self.direction = direction
        self.calculate_target_reg()


    def event_speed_set(self, speed):
        valid_states = [
            MotionState.UNPOWERED,
            MotionState.IDLE,
            MotionState.READY_TO_MOVE,
        ]

        if self.motion_state not in valid_states:
            raise RuntimeError('Invalid event for state')

        self.speed = speed


    def get_target_mode(self):
        return self.target_mode


    def get_abs_target(self):
        return self.abs_target


    def get_rel_target(self):
        abs_angle = self.reg_to_angle(self.target_reg)
        rel_angle = self.rel_target
        return abs_angle, rel_angle


    def get_div_target(self):
        angle = self.reg_to_angle(self.target_reg)
        index = self.div_target
        return angle, index


    def get_div_parameters(self):
        return self.div_parameters


    def get_divs(self):
        if self.target_mode == TargetMode.DIVISION:
            return self.divs
        else:
            return []


    def get_position_angle(self):
        reg = self.motor.get_position()
        return self.reg_to_angle(reg) % 360


    def get_direction(self):
        return self.direction


    def get_speed(self):
        return self.speed


    def get_motion_state(self):
        return self.motion_state


    def get_progress(self):
        enabled = self.motion_state in [
            MotionState.MOVING,
            MotionState.STOPPING,
        ]
        if enabled:
            start = self.start_reg
            current = self.motor.get_position()
            target = self.target_reg

            total_movement = abs(target - start)
            current_movement = abs(current - start)
            progress = int(100 * current_movement / total_movement)
        else:
            progress = 0

        return enabled, progress


    def setup_motor(self):
        steps_per_deg = self.config.steps_per_rev / 360
        accel = self.config.acceleration * steps_per_deg
        start_speed = self.config.start_speed * steps_per_deg

        self.motor.set_acceleration(accel)
        self.motor.set_start_speed(start_speed)
        motor_pos = self.motor.get_position()
        self.position_anchor = 0, motor_pos
        self.steps_per_deg = steps_per_deg


    def evaluate_state_transition(self):
        motor_energized = self.motor.is_energized()
        motor_stationary = not self.motor.is_moving()
        motor_stopping = self.motor.is_stopping()
        destination_reached = self.motor.get_position() == self.target_reg

        old_state = self.motion_state
        new_state = old_state

        if not motor_energized:
            new_state = MotionState.UNPOWERED
        elif motor_stationary:
            if destination_reached:
                new_state = MotionState.IDLE
            else:
                new_state = MotionState.READY_TO_MOVE
        elif motor_stopping:
            new_state = MotionState.STOPPING
        elif old_state == MotionState.READY_TO_MOVE:
            new_state = MotionState.MOVING

        is_stationary = new_state in [
            MotionState.UNPOWERED,
            MotionState.IDLE,
            MotionState.READY_TO_MOVE,
        ]
        was_moving = old_state in [
            MotionState.MOVING,
            MotionState.STOPPING,
        ]
        rel_tgt_mode = self.target_mode == TargetMode.RELATIVE

        if was_moving and is_stationary and rel_tgt_mode:
            self.rel_target = 0
            self.calculate_target_reg()

        self.motion_state = new_state


    def calculate_target_reg(self):
        if self.target_mode == TargetMode.ABSOLUTE:
            tgt_cw, tgt_ccw = self.find_target_candidates(self.abs_target)
            if self.direction == Direction.CW:
                target_reg = tgt_cw
            else:
                target_reg = tgt_ccw
        elif self.target_mode == TargetMode.RELATIVE:
            diff_reg = self.find_rel_target(self.rel_target)
            if self.direction == Direction.CCW:
                diff_reg = -diff_reg
            position_reg = self.motor.get_position()
            target_reg = position_reg + diff_reg
        elif self.target_mode == TargetMode.DIVISION:
            tgt_angle = self.divs[self.div_target]
            tgt_cw, tgt_ccw = self.find_target_candidates(tgt_angle)
            position_reg = self.motor.get_position()
            diff_cw = abs(position_reg - tgt_cw)
            diff_ccw = abs(position_reg - tgt_ccw)
            if(diff_cw <= diff_ccw):
                target_reg = tgt_cw
            else:
                target_reg = tgt_ccw

        self.target_reg = target_reg


    def find_target_candidates(self, target_angle):
        anchor_angle, anchor_reg = self.position_anchor
        steps_per_rev = self.config.steps_per_rev
        position_reg = self.motor.get_position()
        target_reg = self.angle_to_reg(target_angle)
        revs = int(position_reg / steps_per_rev)

        tgt_cw = (revs - 1) * steps_per_rev + target_reg
        while tgt_cw < position_reg:
            tgt_cw += steps_per_rev

        tgt_ccw = (revs + 1) * steps_per_rev + target_reg
        while tgt_ccw > position_reg:
            tgt_ccw -= steps_per_rev

        return tgt_cw, tgt_ccw


    def find_rel_target(self, rel_target):
        steps_per_rev = self.config.steps_per_rev
        position_reg = self.motor.get_position()
        diff_reg = int(round(rel_target * steps_per_rev / 360))
        return diff_reg


    def angle_to_reg(self, angle):
        anch_angle, anch_reg = self.position_anchor
        steps_per_rev = self.config.steps_per_rev
        return int(round((angle - anch_angle) * steps_per_rev / 360)) + anch_reg


    def reg_to_angle(self, reg):
        anch_angle, anch_reg = self.position_anchor
        steps_per_rev = self.config.steps_per_rev
        return ((reg - anch_reg) * 360 / steps_per_rev) + anch_angle
