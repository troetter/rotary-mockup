import math
from datetime import datetime

class FakeMotorController(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.position = 0
        self.target = 0

        self.speeds = [
            0.1,
            1.0,
            10.0,
            30.0,
        ]

        self.speed = len(self.speeds) - 2
        self.movement = None


    def moving(self):
        return self.movement is not None


    def get_position(self):
        if self.movement is None:
            return self.position
        else:
            start_time, speed, to_go = self.movement
            elapsed_time = datetime.now() - start_time
            distance_moved = elapsed_time.total_seconds() * speed
            if abs(distance_moved) >= abs(to_go):
                self.position = self.target
                self.movement = None
                return self.position
            else:
                return math.fmod(self.position + distance_moved + 360, 360)


    def get_target(self):
        return self.target


    def get_speed(self):
        return (self.speed + 1) / len(self.speeds)


    def increase_speed(self):
        if self.speed < len(self.speeds) - 1:
            self.speed += 1


    def decrease_speed(self):
        if self.speed > 0:
            self.speed -= 1


    def set_position(self, position):
        self.position = math.fmod(position, 360)


    def set_target(self, target):
        self.target = math.fmod(target, 360)


    def move(self, direction_cw):
        if self.position != self.target:
            start_time = datetime.now()
            if direction_cw:
                speed = self.speeds[self.speed]
                to_go = math.fmod(self.target - self.position + 360, 360)
            else:
                speed = -self.speeds[self.speed]
                to_go = math.fmod(self.target - self.position - 360, 360)

            self.movement = (start_time, speed, to_go)


    def stop(self):
        if self.movement is not None:
            start_time, speed, to_go = self.movement
            elapsed_time = datetime.now() - start_time
            distance_moved = elapsed_time.total_seconds() * speed
            if abs(distance_moved) >= abs(to_go):
                self.position = self.target
            else:
                self.position += distance_moved
                self.position = math.fmod(self.position + 360, 360)
            self.movement = None

