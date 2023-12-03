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
        # Read mechanical properties
        mech = self.config_obj['Mechanical']
        gearing = mech.getfloat('motor_revs_per_spindle_rev')
        fullsteps = mech.getint('motor_fullsteps_per_rev')
        microsteps = mech.getint('motor_microsteps_per_fullstep')
        self.steps_per_rev = int(gearing * fullsteps * microsteps)

        # Driver connection
        motor = self.config_obj['Motor']
        self.start_speed = motor.getfloat('start_speed')
        self.min_speed = motor.getfloat('min_speed')
        self.max_speed = motor.getfloat('max_speed')
        self.default_speed = motor.getfloat('default_speed')
        self.acceleration = motor.getfloat('acceleration')
