import time
import coreutils.configure as cfg
from coreutils.diagnostics import Diagnostics as dg
from resources.resource import Resource, Policy

class MockWheelMotors(Resource):
    def __init__(self):
        Resource.__init__(self)
        self.policy = Policy.UNIQUE
        self.register_name("Wheels")
        self._ymax = 100
        self._xmax = 100
        self.duty_cycle = 4095

        left_pwm_pin = cfg.motor_config.get_pwm_pin("Wheels", "Left")
        left_digital_pin = cfg.motor_config.get_digital_pin("Wheels", "Left")
        right_pwm_pin = cfg.motor_config.get_pwm_pin("Wheels", "Right")
        right_digital_pin = cfg.motor_config.get_digital_pin("Wheels", "Right")

    def set_values(self, values):
        x = values[0]
        y = values[1]
        dg.print ("Mock wheel motors: values received: {}, {}".format(x,y))
        v_left = (y / self._ymax) + (1 / 2 * (x / self._xmax))
        v_right =(y / self._ymax) - (1 / 2 * (x / self._xmax))

        self._setMotorRight(v_right)
        self._setMotorLeft(v_left)

    def _setMotorRight(self, power):
        int(power)
        if power < 0:
            pwm = int(self.duty_cycle * (1 + power))
            if pwm > self.duty_cycle:
                pwm = self.duty_cycle
        elif power > 0:
            pwm = int (self.duty_cycle * power)
            if pwm > self.duty_cycle:
                pwm = self.duty_cycle
        else:
            pwm = 0
        dg.print("Pwm value for right wheel motors: {}".format(pwm))

    def _setMotorLeft(self, power):
        int(power)
        if power < 0:
            pwm = int(self.duty_cycle * (1 + power))
            if pwm > self.duty_cycle:
                pwm = self.duty_cycle
        elif power > 0:
            pwm = int(self.duty_cycle * power)
            if pwm > self.duty_cycle:
                pwm = self.duty_cycle
        else:
            pwm = 0
        dg.print("Pwm value for left wheel motors: {}".format(pwm))

class MockArmMotors(Resource):
    def __init__(self):
        Resource.__init__(self)
        self.policy = Policy.UNIQUE
        self.register_name("Arm")
        
        servo1_pwm_pin = cfg.motor_config.get_pwm_pin("Arm", "Servo1")
        servo1_digital_pin = cfg.motor_config.get_digital_pin("Arm", "Servo1")
        servo2_pwm_pin = cfg.motor_config.get_pwm_pin("Arm", "Servo2")
        servo2_digital_pin = cfg.motor_config.get_digital_pin("Arm", "Servo2")
        servo3_pwm_pin = cfg.motor_config.get_pwm_pin("Arm", "Servo3")
        servo3_digital_pin = cfg.motor_config.get_digital_pin("Arm", "Servo3")
        gripper_pwm_pin = cfg.motor_config.get_pwm_pin("Arm", "Gripper")
        gripper_digital_pin = cfg.motor_config.get_digital_pin("Arm", "Gripper")        

    def set_values(self, values):
        offset_1 = 160
        offset_2 = 180
        offset_3 = 105
        self.angle_grab = values[0]
        self.angle_top = values[1]
        self.angle_middle = values[2]
        self.angle_bottom = values[3]
        dg.print ("Mock arm motors: values received: {}, {}, {}, {}".format(values[0], values[1], values[2], values[3]))
        self._set_angle()

    def _set_angle(self):
        grab_lim = 90
        top_lim = 90
        middle_lim = 90
        bottom_lim = 90

        if self.angle_grab > grab_lim:
            self.angle_grab = grab_lim
            dg.print('Grabbing servo angle out of range, limit = {}'.format(grab_lim))

        if self.angle_top > top_lim:
            self.angle_top = top_lim
            dg.print('Top servo angle out of range, limit = {}'.format(top_lim))
            
        if self.angle_middle > middle_lim:
            self.angle_middle = middle_lim
            dg.print('Middle servo angle out of range, limit = {}'.format(middle_lim))

        if self.angle_bottom > bottom_lim:
            self.angle_bottom = bottom_lim
            dg.print('Bottom servo angle out of range, limit = {}'.format(bottom_lim))

        dg.print("Pwm value for grab servo: {}".format(self.angle_grab))
        dg.print("Pwm value for top servo: {}".format(self.angle_top))
        dg.print("Pwm value for middle servo: {}".format(self.angle_middle))
        dg.print("Pwm value for bottom servo: {}".format(self.angle_bottom))

        time.sleep(1)
