import sys
import time
import coreutils.configure as cfg
import RPi.GPIO as io

import board
import busio
from resources.adafruit_servokit import ServoKit
import resources.PCA9685_servo as PCA9685_servo
import resources.PCA9685_motor as PCA9685_motor

motor_config = cfg.MotorConfiguration()

pwm_hardware = cfg.global_config.pwm_hardware_setting()

if pwm_hardware == "ONBOARD":
    print("All pwm done through RPi.GPIO")
elif pwm_hardware == "EXTERNAL":
    print("All pwm done through external chip communicated with via I2C")


class WheelMotors:
    def __init__(self):
        left_pwm_pin = motor_config.get_pwm_pin("Wheels", "Left")
        left_digital_pin = motor_config.get_digital_pin("Wheels", "Left")

        right_pwm_pin = motor_config.get_pwm_pin("Wheels", "Right")
        right_digital_pin = motor_config.get_digital_pin("Wheels", "Right")

        self._ymax = 100
        self._xmax = 100

        self.leftmotor_in1_pin = left_digital_pin
        self.rightmotor_in1_pin = right_digital_pin
        self.PWM_left = left_pwm_pin
        self.PWM_right = right_pwm_pin

        io.setmode(io.BCM)

        io.setup(self.leftmotor_in1_pin, io.OUT)
        io.setup(self.rightmotor_in1_pin, io.OUT)
        io.output(self.leftmotor_in1_pin, False)
        io.output(self.rightmotor_in1_pin, False)

        io.setwarnings(False)

        self.duty_cycle = 4095
        self.PCA9685_pwm = PCA9685_motor.PCA9685()
        self.PCA9685_pwm.set_pwm_freq(60)

    def set_values(self, values):
        """
        Only calculates fraction used to find PWM values across
        the whole duty cycle. Fraction is then passed through
        _setMotorRight and _setMotorLeft that deals with 
        calculating PWM values and setting direction. 
        """
        x = values[0]
        y = values[1]

        v_left = (y / self._ymax) + (1 / 2 * (x / self._xmax))
        v_right = (y / self._ymax) - (1 / 2 * (x / self._xmax))

        self._setMotorRight(v_right)
        self._setMotorLeft(v_left)

    def _setMotorMode(self, motor, mode):
        """
        Determines how whether to set the motor moving forwards
        or in reverse. Depending on y (v_avg) values. 
        """
        if motor == "leftmotor":
            if mode == "reverse":
                io.output(self.leftmotor_in1_pin, True)
                io.output(self.leftmotor_in2_pin, False)
            elif mode == "forward":
                io.output(self.leftmotor_in1_pin, False)
                io.output(self.leftmotor_in2_pin, True)
            else:
                io.output(self.leftmotor_in1_pin, False)
                io.output(self.leftmotor_in2_pin, False)
        elif motor == "rightmotor":
            if mode == "reverse":
                io.output(self.rightmotor_in1_pin, False)
                io.output(self.rightmotor_in2_pin, True)
            elif mode == "forward":
                io.output(self.rightmotor_in1_pin, True)
                io.output(self.rightmotor_in2_pin, False)
            else:
                io.output(self.rightmotor_in1_pin, False)
                io.output(self.rightmotor_in2_pin, False)
        else:
            io.output(self.leftmotor_in1_pin, False)
            io.output(self.leftmotor_in2_pin, False)
            io.output(self.rightmotor_in1_pin, False)
            io.output(self.rightmotor_in2_pin, False)

    def _setMotorRight(self, power):
        """
        Sets the right motor to a certain pwm value, only 
        determines the speed. Direction of forward and reverse
        determined by _setMotorMode
        """
        int(power)
        if power < 0:
            # Reverse Mode for Right Motor
            # _setMotorMode("rightmotor", "reverse")
            io.output(self.rightmotor_in1_pin, True)
            pwm = int(self.duty_cycle * (1 + power))
            if pwm > self.duty_cycle:
                pwm = self.duty_cycle
        elif power > 0:
            # Forward Motor for Left Motor
            # _setMotorMode("rightmotor", "forward")
            io.output(self.rightmotor_in1_pin, False)
            pwm = int(self.duty_cycle * power)
            if pwm > self.duty_cycle:
                pwm = self.duty_cycle
        else:
            # Stops right motor
            io.output(self.rightmotor_in1_pin, False)
            pwm = 0
        self.PCA9685_pwm.set_pwm(self.PWM_right, 0, pwm)

    def _setMotorLeft(self, power):
        """
        Sets the left motor to a certain pwm value, only 
        determines the speed. Direction of forward and reverse
        determined by _setMotorMode
        """
        int(power)
        if power < 0:
            # Backwards Mode for Left Motor
            io.output(self.leftmotor_in1_pin, True)
            pwm = int(self.duty_cycle * (1 + power))
            if pwm > self.duty_cycle:
                pwm = self.duty_cycle
        elif power > 0:
            # Reverse Mode for Left Motor
            # _setMotorMode("leftmotor", "forward")

            io.output(self.leftmotor_in1_pin, False)
            pwm = int(self.duty_cycle * power)
            if pwm > self.duty_cycle:
                pwm = self.duty_cycle
        else:
            # Stop left motor
            io.output(self.leftmotor_in1_pin, False)
            pwm = 0
        self.PCA9685_pwm.set_pwm(self.PWM_left, 0, pwm)


class ArmMotors:
    def __init__(self):
        
        """
        Call set_values to set angles ofs servos.
        Will need to callibrate for limits
        """

        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.servo = PCA9685_servo.PCA9685(self.i2c)
        self.kit = ServoKit(channels=16)
        
        gripper_pin = motor_config.get_pin("Arm","Gripper")
        servo1_pin = motor_config.get_pin("Arm","Servo1")
        servo2_pin = motor_config.get_pin("Arm","Servo2")
        servo3_pin = motor_config.get_pin("Arm","Servo3")

        #servo1_pwm_pin = motor_config.get_pwm_pin("Arm", "Servo1")
        #servo1_digital_pin = motor_config.get_digital_pin("Arm", "Servo1")
        #servo2_pwm_pin = motor_config.get_pwm_pin("Arm", "Servo2")
        #servo2_digital_pin = motor_config.get_digital_pin("Arm", "Servo2")
        #servo3_pwm_pin = motor_config.get_pwm_pin("Arm", "Servo3")
        #servo3_digital_pin = motor_config.get_digital_pin("Arm", "Servo3")
        #gripper_pwm_pin = motor_config.get_pwm_pin("Arm", "Gripper")
        #gripper_digital_pin = motor_config.get_digital_pin("Arm", "Gripper")

        # 3 Servos, defines PIN numbers
        self.servo_grab = self.kit.servo[gripper_pin]
        self.servo_top = self.kit.servo[servo1_pin]
        self.servo_middle = self.kit.servo[servo2_pin]
        self.servo_bottom = self.kit.servo[servo3_pin]

        self.servo_grab.actuation_range = 360
        self.servo_top.actuation_range = 360
        self.servo_middle.actuation_range = 360
        self.servo_bottom.actuation_range = 360

        self.servo_grab.set_pulse_width_range(100, 4000)
        self.servo_top.set_pulse_width_range(100, 4000)
        self.servo_middle.set_pulse_width_range(100, 4000)
        self.servo_bottom.set_pulse_width_range(100, 4000)


    def set_values(self, values):


        offset_1 = 160
        offset_2 = 180
        offset_3 = 105
        self.angle_grab = values[0]
        self.angle_top = values[1] - offs
        self.angle_middle = values[2]
        self.angle_bottom = values[3]
        
        print("arm motors got values: {}, {}, {},{}".format(values[0], values[1], values[2],
              values[3]))
        
        self._set_angle()
         

    def _set_angle(self):
        """
        Sets angles of servos, limits defined in the top of the function
        all angles are in degrees. 
        """
        

        #Limit of servo angles 
        grab_lim = 90
        top_lim = 90
        middle_lim = 90
        bottom_lim = 90
                                    
        # Good angle range is 30 - 80 degrees
        if self.angle_grab > grab_lim:
            self.angle_grab = grab_lim
            print('Grabbing servo angle out of range, limit = {}'.format(grab_lim))
                            
        if self.angle_top > top_lim:
            self.angle_top = top_lim
            print('Top servo angle out of range, limit = {}'.format(top_lim))
            
        if self.angle_middle > middle_lim:
            self.angle_middle = middle_lim
            print('Middle servo angle out of range, limit = {}'.format(middle_lim))

        if self.angle_bottom > bottom_lim:
            self.angle_bottom = bottom_lim
            print('Bottom servo angle out of range, limit = {}'.format(bottom_lim))

        self.servo_grab.angle = self.angle_grab
        self.servo_middle.angle = self.angle_middle
        self.servo_bottom.angle = self.angle_bottom

        time.sleep(1)
