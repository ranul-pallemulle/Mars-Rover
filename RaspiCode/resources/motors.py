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
        left_digital1_pin = motor_config.get_digital1_pin("Wheels", "Left")
        left_digital2_pin = motor_config.get_digital2_pin("Wheels", "Left")

        right_pwm_pin = motor_config.get_pwm_pin("Wheels", "Right")
        right_digital1_pin = motor_config.get_digital1_pin("Wheels", "Right")
        right_digital2_pin = motor_config.get_digital2_pin("Wheels", "Right")

        self._ymax = 100
        self._xmax = 100

        self.leftmotor_in1_pin = left_digital1_pin
        self.rightmotor_in1_pin = right_digital1_pin
        self.PWM_left = left_pwm_pin
        self.PWM_right = right_pwm_pin

        io.setmode(io.BCM)

        io.setup(self.leftmotor_in1_pin, io.OUT)
        io.setup(self.leftmotor_in2_pin, io.OUT)
        io.setup(self.rightmotor_in1_pin, io.OUT)
        io.setup(self.rightmotor_in2_pin, io.OUT)

        io.output(self.leftmotor_in1_pin, False)
        io.output(self.leftmotor_in2_pin, False)
        io.output(self.rightmotor_in1_pin, False)
        io.output(self.rightmotor_in2_pin, False)

        io.setwarnings(False)

        self.duty_cycle = 4095
        PCA9685_pwm = PCA9685_motor.PCA9685()
        PCA9685_pwm.set_pwm_freq(60)

    def set_values(self, values):
        """
                Only calculates fraction used to find PWM values across
                the whole duty cycle. Fraction is then passed through
                _setMotorRight and _setMotorLeft that deals with 
                calculating PWM values and setting direction. 
        """
        x = []
        y = []

        v_left = (y / self._ymax) + (1 / 2 * (x / self._xmax))
        v_right = (y / self._ymax) - (1 / 2 * (x / self._xmax))

        # Sets average v as the fraction of y compared to its max
        # v_avg = y / self._ymax
        # v_left = v_avg
        # v_right = v_avg

        # #Sets a R
        # if x > 0:
        #     v_left += x / self._xmax
        #     v_right += v_left - self.D
        # elif x < 0:
        #     v_right += x / self._xmax
        #     v_left += v_right - self.D
        # elif x == 0:
        #   pass

        _setMotorRight(v_right)
        _setMotorLeft(v_left)

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
            pwm = -int(duty_cycle * (1 - power))
            if pwm > duty_cycle:
                pwm = duty_cycle
        elif power > 0:
            # Forward Motor for Left Motor
            # _setMotorMode("rightmotor", "forward")
            io.output(self.rightmotor_in1_pin, False)
            pwm = int(duty_cycle * power)
            if pwm > duty_cycle:
                pwm = duty_cycle
        else:
            # Stops right motor
            io.output(self.rightmotor_in1_pin, False)
            pwm = 0
        PCA9685_pwm.set_pwm(self.PWM_right, 0, pwm)

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
            pwm = int(duty_cycle * (1 - power))
            if pwm > duty_cycle:
                pwm = duty_cycle
        elif power > 0:
            # Reverse Mode for Left Motor
            # _setMotorMode("leftmotor", "forward")

            io.output(self.leftmotor_in1_pin, False)
            pwm = int(duty_cycle * power)
            if pwm > duty_cycle:
                pwm = duty_cycle
        else:
            # Stop left motor
            io.output(self.leftmotor_in1_pin, False)
            pwm = 0
        PCA9685_pwm.set_pwm(self.PWM_left, 0, pwm)


class ArmMotors:
    def __init__(self):
        servo1_pwm_pin = motor_config.get_pwm_pin("Arm", "Servo1")
        servo1_digital_pin = motor_config.get_digital_pin("Arm", "Servo1")
        servo2_pwm_pin = motor_config.get_pwm_pin("Arm", "Servo2")
        servo2_digital_pin = motor_config.get_digital_pin("Arm", "Servo2")
        servo3_pwm_pin = motor_config.get_pwm_pin("Arm", "Servo3")
        servo3_digital_pin = motor_config.get_digital_pin("Arm", "Servo3")
        gripper_pwm_pin = motor_config.get_pwm_pin("Arm", "Gripper")
        gripper_digital_pin = motor_config.get_digital_pin("Arm", "Gripper")

        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.servo = PCA9685_servo.PCA9685(self.i2c)
        self.kit = ServoKit(channels=16)

        # 3 Servos, defines PIN numbers
        self.servo_grab = self.kit.servo[grab_PIN]
        self.servo_middle = self.kit.servo[middle_PIN]
        self.servo_bottom = self.kit.servo[bottom_PIN]

        self.servo_grab.set_pulse_width_range(750, 2250)
        self.servo_middle.set_pulse_width_range(750, 2250)
        self.servo_bottom.set_pulse_width_range(750, 2250)
        pass

    def set_values(self, values):
        print("arm motors got values: {}, {}, {}".format(values[0], values[1], values[2]))

    def set_angle(self):
        for i in range(len(self.angle_grab)):
            if self.angle_middle[i] < 0 or self.angle_middle[i] > 90:
                raise Exception('Middle servo angle out of range, the  value  was: {}'.format(self.angle_middle[i]))

            if self.angle_bottom[i] < 0 or self.angle_bottom[i] > 180:
                raise Exception('Bottom servo angle out of range, the  value  was: {}'.format(self.angle_bottom[i]))

            # Good angle range is 30 - 80 degrees
            if self.angle_grab[i] < 0 or self.angle_grab[i] > 90:
                raise Exception('Grabbing servo angle out of range, the  value  was: {}'.format(self.angle_grab[i]))

            self.servo_grab.angle = self.angle_grab[i]
            self.servo_middle.angle = self.angle_middle[i]
            self.servo_bottom.angle = self.angle_bottom[i]

            time.sleep(1)
