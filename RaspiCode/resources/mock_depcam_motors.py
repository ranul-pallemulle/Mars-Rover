### Copy of depcam motors section from mock_motors.py
import time
import coreutils.configure as cfg
from coreutils.diagnostics import Diagnostics as dg
from resources.resource import Resource, Policy

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
