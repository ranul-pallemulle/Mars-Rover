import coreutils.configure as cfg

class MotorInterfaceError(Exception):
    pass

class MotorInterface:
    def __init__(self):
        try:
            self.pwm_hardware = cfg.global_config.pwm_hardware_setting()
            self.operation_mode = cfg.global_config.operation_mode()
        except cfg.ConfigurationError as e:
            raise MotorInterfaceError("Error in configuration: "+str(e))

        if self.operation_mode == "RASPBERRYPI":
            print("Operation mode: Raspberry Pi")
            import resources.motors
        elif self.operation_mode == "LAPTOP":
            print("Operation mode: Laptop (debug) - no actual motors in use.")
        print("Found PWM hardware setting: "+self.pwm_hardware)


    def WheelMotors(self):
        try:
            if self.operation_mode == "LAPTOP":
                return MockWheelMotors()
            elif self.operation_mode == "RASPBERRYPI":
                import resources.motors as motors
                return motors.WheelMotors()
        except cfg.ConfigurationError as e:
            raise MotorInterfaceError('Error in configuration: \n'+str(e))

    def ArmMotors(self):
        try:
            if self.operation_mode == "LAPTOP":
                return MockArmMotors()
            elif self.operation_mode == "RASPBERRYPI":
                import resources.motors as motors
                return motors.ArmMotors()
        except cfg.ConfigurationError as e:
            raise MotorInterfaceError('Error in configuration: \n'+str(e))
            
class MockWheelMotors:
    def __init__(self):
        motor_config = cfg.MotorConfiguration()
        left_pwm_pin = motor_config.get_pwm_pin("Wheels", "Left")
        left_digital_pin = motor_config.get_digital_pin("Wheels", "Left")
        right_pwm_pin = motor_config.get_pwm_pin("Wheels", "Right")
        right_digital_pin = motor_config.get_digital_pin("Wheels", "Right")
        print("Found settings for wheel motors.")

    def set_values(self, values):
        print("wheel motors got values: {}, {}".format(values[0], values[1]))        
        
    
class MockArmMotors:
    def __init__(self):
        motor_config = cfg.MotorConfiguration()
        servo1_pwm_pin = motor_config.get_pwm_pin("Arm", "Servo1")
        servo1_digital_pin = motor_config.get_digital_pin("Arm", "Servo1")
        servo2_pwm_pin = motor_config.get_pwm_pin("Arm", "Servo2")
        servo2_digital_pin = motor_config.get_digital_pin("Arm", "Servo2")
        servo3_pwm_pin = motor_config.get_pwm_pin("Arm", "Servo3")
        servo3_digital_pin = motor_config.get_digital_pin("Arm", "Servo3")
        gripper_pwm_pin = motor_config.get_pwm_pin("Arm", "Gripper")
        gripper_digital_pin = motor_config.get_digital_pin("Arm", "Gripper")
        print("Found settings for arm motors.")
        
    def set_values(self, values):
        print("arm motors got values: {}, {}, {}, {}".format(values[0], values[1], values[2], values[3]))
