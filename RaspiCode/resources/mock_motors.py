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
        dg.print("Mock wheel motors settings:")     

        left_pwm_pin = cfg.motor_config.get_pwm_pin("Wheels", "Left")
        left_digital_pin = cfg.motor_config.get_digital_pin("Wheels", "Left")
        right_pwm_pin = cfg.motor_config.get_pwm_pin("Wheels", "Right")
        right_digital_pin = cfg.motor_config.get_digital_pin("Wheels", "Right")

        dg.print("    Left PWM pin: {}".format(left_pwm_pin))
        dg.print("    Left digital pin: {}".format(left_digital_pin))
        dg.print("    Right PWM pin: {}".format(right_pwm_pin))
        dg.print("    Right digital pin: {}".format(right_digital_pin))

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
        dg.print("Mock arm motors settings:")
        
        servo1_pin = cfg.motor_config.get_pin("Arm", "Servo1")
        servo2_pin = cfg.motor_config.get_pin("Arm", "Servo2")
        servo3_pin = cfg.motor_config.get_pin("Arm", "Servo3")
        gripper_pin = cfg.motor_config.get_pin("Arm", "Gripper")

        dg.print("    Servo 1 pin: {}".format(servo1_pin))
        dg.print("    Servo 2 pin: {}".format(servo2_pin))
        dg.print("    Servo 3 pin: {}".format(servo3_pin))
        dg.print("    Gripper pin: {}".format(gripper_pin))

    def set_values(self, values):
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

        dg.print("PWM value for grab servo: {}".format(self.angle_grab))
        dg.print("PWM value for top servo: {}".format(self.angle_top))
        dg.print("PWM value for middle servo: {}".format(self.angle_middle))
        dg.print("PWM value for bottom servo: {}".format(self.angle_bottom))

        time.sleep(0.03)


class MockDeployableCameraMotors(Resource):
    def __init__(self):
        Resource.__init__(self)
        self.policy = Policy.UNIQUE
        self.register_name("DeployableCamera")
        dg.print("Deployable camera motors settings:")
        
        servo1_pin = cfg.motor_config.get_pin("DeployableCamera", "Servo1")
        self.servo1_lim_upper = cfg.motor_config.get_limit("DeployableCamera",
                                                           "Servo1", "Upper")
        self.servo1_lim_lower = cfg.motor_config.get_limit("DeployableCamera",
                                                           "Servo1", "Lower")
        servo2_pin = cfg.motor_config.get_pin("DeployableCamera", "Servo2")
        self.servo2_lim_upper = cfg.motor_config.get_limit("DeployableCamera",
                                                      "Servo2", "Upper")
        self.servo2_lim_lower = cfg.motor_config.get_limit("DeployableCamera",
                                                      "Servo2", "Lower")
        servo3_pin = cfg.motor_config.get_pin("DeployableCamera", "Servo3")
        self.servo3_lim_upper = cfg.motor_config.get_limit("DeployableCamera",
                                                      "Servo3", "Upper")
        self.servo3_lim_lower = cfg.motor_config.get_limit("DeployableCamera",
                                                      "Servo3", "Lower")
        
        dg.print("   Servo 1 pin: {}".format(servo1_pin))
        dg.print("   Servo 1 upper limit: {}".format(self.servo1_lim_upper))
        dg.print("   Servo 1 lower limit: {}".format(self.servo1_lim_lower))
        dg.print("   Servo 2 pin: {}".format(servo2_pin))
        dg.print("   Servo 2 upper limit: {}".format(self.servo2_lim_upper))
        dg.print("   Servo 2 lower limit: {}".format(self.servo2_lim_lower))
        dg.print("   Servo 3 pin: {}".format(servo3_pin))
        dg.print("   Servo 3 upper limit: {}".format(self.servo3_lim_upper))
        dg.print("   Servo 3 lower limit: {}".format(self.servo3_lim_lower))
        
    def set_values(self, values):
        if (values[0] > self.servo1_lim_upper or values[0] <
        self.servo1_lim_lower):
            return
        if (values[1] > self.servo2_lim_upper or values[1] <
        self.servo2_lim_lower):
            return
        if (values[2] > self.servo3_lim_upper or values[2] <
        self.servo3_lim_lower):
            return
        offset = 135
        top_angle = values[0] + offset
        middle_angle = values[1] + offset
        bottom_angle = values[2] + offset
        dg.print("Mock deployable camera motors: values received: {}, {}, {}"
                 .format(values[0], values[1], values[2]))
        time.sleep(0.02)
