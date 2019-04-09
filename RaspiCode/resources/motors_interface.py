import coreutils.configure as cfg
from resources.resource import Resource, Policy

class MotorInterfaceError(Exception):
    pass

class MotorInterface:
    def __init__(self):
        try:
            self.hardware_mode = cfg.overall_config.hardware_mode()
        except cfg.ConfigurationError as e:
            raise MotorInterfaceError("Error in configuration: "+str(e))

        if self.hardware_mode == "RASPBERRYPI":
            print("Hardware mode: Raspberry Pi")
            import resources.motors
        elif self.hardware_mode == "LAPTOP":
            print("Hardware mode: Laptop (debug) - no motors.")
        elif self.hardware_mode == "RASPBERRYPI_NO_MOTORS":
            print("Hardware mode: Raspberry Pi (debug) - no motors)")


    def WheelMotors(self):
        try:
            if self.hardware_mode == "LAPTOP" or\
               self.hardware_mode == "RASPBERRYPI_NO_MOTORS":
                return MockWheelMotors()
            elif self.hardware_mode == "RASPBERRYPI":
                import resources.motors as motors
                return motors.WheelMotors()
        except cfg.ConfigurationError as e:
            raise MotorInterfaceError('Error in configuration: \n'+str(e))

    def ArmMotors(self):
        try:
            if self.hardware_mode == "LAPTOP" or\
               self.hardware_mode == "RASPBERRYPI_NO_MOTORS":
                return MockArmMotors()
            elif self.hardware_mode == "RASPBERRYPI":
                import resources.motors as motors
                return motors.ArmMotors()
        except cfg.ConfigurationError as e:
            raise MotorInterfaceError('Error in configuration: \n'+str(e))
            
class MockWheelMotors(Resource):
    def __init__(self):
        Resource.__init__(self)
        self.policy = Policy.UNIQUE
        self.register_name("Wheels")
        left_pwm_pin = cfg.motor_config.get_pwm_pin("Wheels", "Left")
        left_digital_pin = cfg.motor_config.get_digital_pin("Wheels", "Left")
        right_pwm_pin = cfg.motor_config.get_pwm_pin("Wheels", "Right")
        right_digital_pin = cfg.motor_config.get_digital_pin("Wheels", "Right")
        # print("Found settings for wheel motors.")

    def set_values(self, values):
        print("wheel motors got values: {}, {}".format(values[0], values[1]))        
        
    
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
        # print("Found settings for arm motors.")
        
    def set_values(self, values):
        print("arm motors got values: {}, {}, {}, {}".format(values[0], values[1], values[2], values[3]))
