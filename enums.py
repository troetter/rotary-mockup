from enum import Enum, auto


class TargetMode(Enum):
    ABSOLUTE = 'Absolute Angle'
    RELATIVE = 'Relative Angle'
    DIVISION = 'Division'


class MotionState(Enum):
    UNPOWERED = auto()
    IDLE = auto()
    READY_TO_MOVE = auto()
    MOVING = auto()
    STOPPING = auto()


class Direction(Enum):
    CW = auto()
    CCW = auto()


class DivMode(Enum):
    FULL = auto()
    END = auto()
    EXTENT = auto()