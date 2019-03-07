import RPi.GPIO as io
import PCA9685 as Adafruit_PCA9685
import time


class Wheel_Motors:
    """
    Class to handle moving of motors:

    Takes input values from a joystick, in x-y values.
    If x or y are negative values, sets motor mode in reverse by swapping
    GPIO outputs, then applies PWM to change speeds. 
    """

    def __init__(self, values):  # IN1, IN2, IN3, IN4, ENA, ENB, D

        self._ymax = 100
        self._xmax = 100
        self.leftmotor_in1_pin = IN1
        self.leftmotor_in2_pin = IN2
        self.rightmotor_in1_pin = IN3
        self.rightmotor_in2_pin = IN4
        self.ENA_left = ENA
        self.ENB_right = ENB

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
        PCA9685_pwm = Adafruit_PCA9685.PCA9685()
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

        v_left = (y / self._ymax) + (1 / 2 * x)
        v_right = (y / self._ymax) - (1 / 2 * x)

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
            _setMotorMode("rightmotor", "reverse")
            pwm = -int(duty_cycle * power)
            if pwm > duty_cycle:
                pwm = duty_cycle
        elif power > 0:
            # Forward Motor for Left Motor
            _setMotorMode("rightmotor", "forward")
            pwm = int(duty_cycle * power)
            if pwm > duty_cycle:
                pwm = duty_cycle
        else:
            # Stops right motor
            _setMotorMode("rightmotor", "stop")
            pwm = 0
        PCA9685_pwm.set_pwm(self.ENB_right, 0, pwm)

    def _setMotorLeft(self, power):
        """
        Sets the left motor to a certain pwm value, only 
        determines the speed. Direction of forward and reverse
        determined by _setMotorMode
        """
        int(power)
        if power < 0:
            # Forward Mode for Left Motor
            _setMotorMode("leftmotor", "reverse")
            pwm = -int(duty_cycle * power)
            if pwm > duty_cycle:
                pwm = duty_cycle
        elif power > 0:
            # Reverse Mode for Left Motor
            _setMotorMode("leftmotor", "forward")
            pwm = int(duty_cycle * power)
            if pwm > duty_cycle:
                pwm = duty_cycle
        else:
            # Stop left motor
            _setMotorMode("leftmotor", "stop")
            pwm = 0
        PCA9685_pwm.set_pwm(self.ENA_left, 0, pwm)
