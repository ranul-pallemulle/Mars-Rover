import coreutils.configure as cfg

operation_mode = cfg.global_config.operation_mode()
if operation_mode == "RASPBERRYPI":
    import resources.motors

class MotorInterface:
    def __init__(self):
        self.pwm_hardware = cfg.global_config.pwm_hardware_setting()
        print("PWM hardware setting: "+self.pwm_hardware)


    def WheelMotors(self):
        if operation_mode == "LAPTOP":
            return MockWheelMotors()
        elif operation_mode == "RASPBERRYPI":
            return motors.WheelMotors()

    def ArmMotors(self):
        if operation_mode == "LAPTOP":
            return MockArmMotors()
        elif operation_mode == "RASPBERRYPI":
            return motors.ArmMotors()
            
class MockWheelMotors:
    def __init__(self):
        motor_config = cfg.MotorConfiguration()
        left_pwm_pin = motor_config.get_pwm_pin("Wheels", "Left")
        left_digital_pin = motor_config.get_digital_pin("Wheels", "Left")
        right_pwm_pin = motor_config.get_pwm_pin("Wheels", "Right")
        right_digital_pin = motor_config.get_digital_pin("Wheels", "Right")
        print("Left pwm pin: "+ str(left_pwm_pin))
        print("Left digital pin: "+ str(left_digital_pin))
        print("Right pwm pin: "+ str(right_pwm_pin))
        print("Right digital pin: "+ str(right_digital_pin))

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

        print("Servo1 pwm pin: "+ str(servo1_pwm_pin))
        print("Servo1 digital pin: "+ str(servo1_digital_pin))
        print("Servo2 pwm pin: "+ str(servo2_pwm_pin))
        print("Servo2 digital pin: "+ str(servo2_digital_pin))
        print("Servo3 pwm pin: "+ str(servo3_pwm_pin))
        print("Servo3 digital pin: "+ str(servo3_digital_pin))

    def set_values(self, values):
        print("arm motors got values: {}, {}, {}".format(values[0], values[1], values[2]))        
