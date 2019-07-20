import coreutils.configure as cfg
from resources.resource import Resource, Policy
import board
import busio
from resources.adafruit_servokit import ServoKit
import adafruit_pca9685

class DeployableCameraMotors(Resource):
    def __init__(self):
        Resource.__init__(self)
        self.policy = Policy.UNIQUE
        self.register_name("DeployableCamera")
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.servo = adafruit_pca9685.PCA9685(self.i2c)
        self.kit = ServoKit(channels=16)
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
                
        self.servo_top = self.kit.servo[servo1_pin]
        self.servo_middle = self.kit.servo[servo2_pin]
        self.servo_bottom = self.kit.servo[servo3_pin]
        self.servo_top.actuation_range = 360
        self.servo_middle.actuation_range = 360
        self.servo_bottom.actuation_range = 360
        self.servo_top.set_pulse_width_range(500, 3250)
        self.servo_middle.set_pulse_width_range(500, 3250)
        self.servo_bottom.set_pulse_width_range(500, 3250)
        
    
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
        self.servo_top.angle = values[0] + offset
        self.servo_middle.angle = values[1] + offset
        self.servo_bottom.angle = values[2] + offset
        time.sleep(0.02)
