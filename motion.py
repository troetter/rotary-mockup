import tmc5160

import math
from datetime import datetime

class Tmc5160Controller(object):
    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.read_config(config)
        self.tmc = tmc5160.TMC5160(
            spibus=self.spi_bus,
            spics=self.spi_cs,
            spibps=self.spi_bitrate,
            enapin=self.enable_pin)

        self.tmc.set_register_values(self.init_regs)
        self.set_position(0)

        self.position = 0
        self.target = 0
        self.reg_target = 0


    def read_config(self, config):
        # Read mechanical properties
        mech = config['Mechanical']
        gearing = mech.getfloat('motor_revs_per_spindle_rev')
        fullsteps = mech.getint('motor_fullsteps_per_rev')
        microsteps = mech.getint('motor_microsteps_per_fullstep')
        self.steps_per_rev = int(gearing * fullsteps * microsteps)

        # Driver connection
        elec = config['Electrical']
        self.spi_bus = elec.getint('spi_bus')
        self.spi_cs = elec.getint('spi_cs')
        self.spi_bitrate = elec.getint('spi_bitrate')
        self.enable_pin = elec['enable_pin']

        # Read speed settings
        speed = config['Speed']
        num_speeds = speed.getint('num_speeds')
        self.default_speed = speed.getint('default')
        self.current_speed = self.default_speed
        self.speeds = {}
        for i in range(num_speeds):
            section = config[f'Speed.{i}']
            keys = ['A1', 'V1', 'AMAX', 'VMAX', 'DMAX', 'D1', 'VSTOP']
            data = {k.upper(): {k.upper(): section.getint(k)} for k in keys}
            self.speeds[i] = data

        # Read register settings
        self.init_regs = {}
        self.enable_regs = {}
        self.disable_regs = {}
        for s in config.sections():
            if s.startswith('reg'):
                _, phase, reg = s.split('.')
                section = config[s]
                data = {k.upper(): section.getint(k) for k in section}
                if phase == 'init':
                    self.init_regs[reg] = data
                elif phase == 'enable':
                    self.enable_regs[reg] = data
                elif phase == 'disable':
                    self.disable_regs[reg] = data


    def moving(self):
        mov = []
        for i in range(10):
            reg_value = self.tmc.read_register_value('DRV_STATUS')
            mov.append((reg_value & 0x8000_0000) == 0)

        if all(mov):
            print('all moving')
        elif any(mov):
            reg_xactual = self.tmc.read_register_value('XACTUAL')
            at_tgt = self.reg_target == reg_xactual
            print(f'====== {sum(mov)} moving, at target: {at_tgt}')
        else:
            print('all stationary')
        return any(mov)


    def get_position(self):
        reg_value = self.tmc.read_register_value('XACTUAL')
        reg_offset = reg_value - self.setpoint_reg
        step_in_rev = reg_offset % self.steps_per_rev
        angle_offset = step_in_rev * 360.0 / self.steps_per_rev
        pos = math.fmod(self.setpoint_angle + angle_offset, 360.0)
        print(f'Pos  XACTUAL: {reg_value:08x}')
        print(f'reg: {reg_value}, offs: {reg_offset}, step: {step_in_rev}, ang: {angle_offset}, pos: {pos}')
        return pos


    def get_target(self):
        return self.target


    def get_speed(self):
        return (self.current_speed + 1) / len(self.speeds)


    def increase_speed(self):
        if self.current_speed < len(self.speeds) - 1:
            self.current_speed += 1


    def decrease_speed(self):
        if self.current_speed > 0:
            self.current_speed -= 1


    def set_position(self, position):
        print(f'Setting position to {position}')
        if not self.moving():
            self.setpoint_reg = self.tmc.read_register_value('XACTUAL')
            while position < 0.0:
                position += 360.0
            self.setpoint_angle = math.fmod(position, 360)
        else:
            raise RuntimeError('unable to set position while moving')


    def set_target(self, target):
        if not self.moving():
            while target < 0.0:
                target += 360.0
            self.target = math.fmod(target, 360)
        else:
            raise RuntimeError('unable to set target while moving')


    def set_power_on(self):
        # TODO: fix
        self.tmc.set_register_values(self.enable_regs)
        self.tmc.enable()
        self.power_on = True


    def set_power_off(self):
        # TODO: fix
        self.tmc.disable()
        self.tmc.set_register_values(self.disable_regs)
        self.power_on = False


    def move(self, direction_cw):
        # TODO: fix
        if self.power_on and not self.moving():
            reg_actual = self.tmc.read_register_value('XACTUAL')
            reg_offset = reg_actual - self.setpoint_reg
            current_step = reg_offset % self.steps_per_rev
            target_step = int(round((self.target - self.setpoint_angle) * self.steps_per_rev / 360.0))

            if direction_cw:
                delta = (target_step - current_step) % self.steps_per_rev
            else:
                delta = -((current_step - target_step) % self.steps_per_rev)

            reg_target = (reg_actual + delta) % 2**32

            reg_values = self.speeds[self.current_speed].copy()
            reg_values['RAMPMODE'] = {'RAMPMODE': 0}
            reg_values['XTARGET'] = {'XTARGET': reg_target}
            self.reg_target = reg_target
            self.tmc.set_register_values(reg_values)
            print(f'Move XACTUAL: {reg_actual:08x} XTARGET: {reg_target:08x}')
            print(f'pos: {reg_actual}, delta: {delta}, tgt: {reg_target}')


    def stop(self):
        # TODO: fix
        pass


class FakeMotorController(object):
    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.power_on = False
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


    def set_power_on(self):
        self.power_on = True


    def set_power_off(self):
        self.power_on = False


    def move(self, direction_cw):
        if self.power_on and self.position != self.target:
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

