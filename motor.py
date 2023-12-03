import math
from datetime import datetime

class Motor(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def update_state(self):
        raise NotImplementedError('implement in subclass')

    def set_power_on(self):
        raise NotImplementedError('implement in subclass')

    def set_power_off(self):
        raise NotImplementedError('implement in subclass')

    def is_energized(self):
        raise NotImplementedError('implement in subclass')

    def is_moving(self):
        raise NotImplementedError('implement in subclass')
    
    def get_position(self):
        raise NotImplementedError('implement in subclass')

    def get_target_position(self):
        raise NotImplementedError('implement in subclass')
    
    def set_acceleration(self, acceleration):
        raise NotImplementedError('implement in subclass')

    def set_start_speed(self, start_speed):
        raise NotImplementedError('implement in subclass')

    def start_move_to_position(self, target_position, top_speed):
        raise NotImplementedError('implement in subclass')

    def stop(self):
        raise NotImplementedError('implement in subclass')


class FakeMotor(Motor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.power_on = False
        self.moving = False
        self.position = 0
        self.speed = 0
        self.start_speed = 0
        self.acceleration = 0
        self.target = 0
        self.stop_signal = False


    def is_moving(self):
        return self.moving


    def is_stopping(self):
        return self.stop_signal


    def get_position(self):
        return self.position


    def get_target_position(self):
        return self.target


    def set_acceleration(self, acceleration):
        self.acceleration = acceleration


    def set_start_speed(self, start_speed):
        self.start_speed = start_speed


    def start_move_to_position(self, target_position, top_speed):
        if not self.power_on:
            raise RuntimeError('cannot move when not energized')
        elif self.moving:
            raise RuntimeError('attempted to interrupt move')
        elif target_position == self.position:
            raise RuntimeError('attempted move to current pos')
        elif top_speed < self.start_speed:
            raise RuntimeError('speed too low')
        
        # Calculate the time to accelerate to full speed
        time_acc = (top_speed - self.start_speed) / self.acceleration
        
        # Same time to decelerate
        time_dec = time_acc

        # Number of steps to go
        dist_to_go = abs(target_position - self.position)

        # The distance covered when accelerating to and decelerating from
        # top speed
        dist_acc = (top_speed + self.start_speed) * time_acc / 2
        dist_dec = dist_acc

        # Select one of two cases, with or without a constant speed phase
        if (dist_acc + dist_dec) < dist_to_go:
            time_full_speed = (dist_to_go - dist_acc - dist_dec) / top_speed
        else:
            # Calculate a new acceleration time, which will be the same as the
            # deceleration time
            # ax² + bx + c = 0 => x = -b/2a (+/-) sqrt((b/2a)² - c/a)
            # x = time_acc
            # a = self.acceleration
            # b = 2 * self.start_speed
            # c = -dist_to_go
            b_over_2a = self.start_speed / self.acceleration
            c_over_a = -dist_to_go / self.acceleration
            time_acc = -b_over_2a + math.sqrt(b_over_2a**2 - c_over_a)
            time_full_speed = 0
            time_dec = time_acc
            dist_acc = dist_to_go / 2
            dist_dec = dist_acc
            top_speed = self.start_speed + time_acc * self.acceleration

        self.target = target_position
        self.top_speed = top_speed
        self.start_position = self.position
        self.stop_signal = False
        self.moving = True
        self.start_time = datetime.now()
        self.t1 = time_acc
        self.t2 = self.t1 + time_full_speed
        self.t3 = self.t2 + time_dec
        self.d1 = dist_acc
        self.d2 = dist_to_go - dist_dec
        self.d3 = dist_to_go


    def set_power_on(self):
        self.power_on = True


    def set_power_off(self):
        self.power_on = False
        self.update_state()


    def is_energized(self):
        return self.power_on


    def stop(self):
        self.stop_signal = True
        self.update_state()


    def update_state(self):
        if not self.moving:
            return

        # Calculate speed and distance moved from start of move
        t = (datetime.now() - self.start_time).total_seconds()
        if t < self.t1:
            t_off = t
            speed = self.start_speed + self.acceleration * t_off
            moved_dist = self.start_speed * t_off + self.acceleration * t_off**2 / 2
        elif t < self.t2:
            t_off = t - self.t1
            speed = self.top_speed
            moved_dist = self.d1
            moved_dist += self.top_speed * t_off
        elif t < self.t3:
            t_off = t - self.t2
            speed = self.top_speed - self.acceleration * t_off
            moved_dist = self.d2
            moved_dist += self.top_speed * t_off - self.acceleration * t_off**2 / 2
        else:
            speed = 0
            moved_dist = self.d3
            self.moving = False

        # If stop signal is set and we haven't stopped yet, calculate a
        # a deceleration from where we are
        if self.moving and self.stop_signal:
            time_dec = (speed - self.start_speed) / self.acceleration
            dist_dec = (speed + self.start_speed) * time_dec / 2
            self.t1 = min(t, self.t1)
            self.t2 = t
            self.t3 = t + time_dec
            self.d2 = moved_dist
            self.d3 = moved_dist + dist_dec
            self.top_speed = speed
            self.stop_signal = False

        # If power was cut, stop immediately
        if not self.power_on:
            speed = 0
            self.moving = False

        # Update speed and position
        self.speed = speed
        if (self.target - self.start_position) > 0:
            self.position = int(self.start_position + moved_dist)
        else:
            self.position = int(self.start_position - moved_dist)
