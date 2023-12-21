import configparser
import os

class Configuration:
    def __init__(self, filename):
        if not os.path.isfile(filename):
            raise RuntimeError('config file cannot be found')

        self.config_obj = configparser.ConfigParser()
        self.config_obj.read(filename)

        self.populate_config()

    def populate_config(self):
        # Read config
        mech = self.config_obj['Mechanical']
        motor = self.config_obj['Motor']
        gearing = mech.getfloat('motor_revs_per_spindle_rev')
        fullsteps = motor.getint('fullsteps_per_rev')
        microsteps = motor.getint('microsteps_per_fullstep')
        self.steps_per_rev = int(gearing * fullsteps * microsteps)
        self.microsteps = microsteps
        self.max_current = motor.getint('max_current')
        self.start_speed = motor.getfloat('start_speed')
        self.min_speed = motor.getfloat('min_speed')
        self.max_speed = motor.getfloat('max_speed')
        self.default_speed = motor.getfloat('default_speed')
        self.acceleration = motor.getfloat('acceleration')
