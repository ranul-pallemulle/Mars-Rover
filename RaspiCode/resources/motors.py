import sys
import time
import RPi.GPIO as GPIO

import board
import busio
from adafruit_servokit import ServoKit
import adafruit_pca9685


class WheelMotors:
    def __init__(self,values):
        self.mode = GPIO.getmode()
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        
        self.motor_1 = [motor_1_pin_1,motor_1_pin_2]
        self.motor_2 = [motor_2_pin_1,motor_2_pin_2]
        GPIO.setup(self.motor_1,GPIO.OUT)
        
        #Only needs one pin, as only turn in forward direction
        self.motor_1_pwm = GPIO.PWM(motor_1_pin_1,100)
        self.motor_2_pwm = GPIO.PWM(motor_2_pin_2,100)
        
        self.motor_1_pwm.start(0)
        self.motor_2_pwm.start(0)
        pass
    
    def set_values(self, values):
        print("wheel motors got values: {}, {}".format(values[0], values[1]))

    def move_forward(self):
        GPIO.output(self.motor_1[0],GPIO.HIGH)
        
    def move_backward(self):
        GPIO.output(self.motor_1[1],GPIO.HIGH)
        
    def turn_left(self):
        """
        Makes one side moves faster than the other,
        in order to make it turn. 
        """
        self.motor_1_pwm.ChangeDutyCycle(100)
        self.motor_2_pwm.ChangeDutyCycle(25)
        
    def turn_right(self):
        self.motor_1_pwm.ChangeDutyCycle(25)
        self.motor_2_pwm.ChangeDutyCycle(100)
        
    def end(self):
        self.motor_1_pwm.stop()
        GPIO.cleanup()
        

    

class ArmMotors:
    def __init__(self,values):
        self.i2c = busio.I2C(board.SCL,board.SDA)
        self.servo = adafruit_pca9685.PCA9685(self.i2c)
        self.kit = ServoKit(channels=16)
        
        #3 Servos, defines PIN numbers
        self.servo_grab = self.kit.servo[grab_PIN]
        self.servo_middle = self.kit.servo[middle_PIN]
        self.servo_bottom = self.kit.servo[bottom_PIN]

        self.servo_grab.set_pulse_width_range(750,2250)
        self.servo_middle.set_pulse_width_range(750,2250)
        self.servo_bottom.set_pulse_width_range(750,2250)
        pass

    def set_values(self, values):
        print("arm motors got values: {}, {}, {}".format(values[0], values[1], values[2]))

    def set_angle(self):
        for i in  range (len(self.angle_grab)):
            if self.angle_middle[i] < 0 or self.angle_middle[i] > 90:
                raise Exception( 'Middle servo angle out of range, the  value  was: {}'.format(self.angle_middle[i]))

            if self.angle_bottom[i] < 0 or self.angle_bottom[i] > 180:
                raise Exception( 'Bottom servo angle out of range, the  value  was: {}'.format(self.angle_bottom[i]))
            
            #Good angle range is 30 - 80 degrees
            if self.angle_grab[i] < 0 or self.angle_grab[i] > 90
                raise Exception ( 'Grabbing servo angle out of range, the  value  was: {}'.format(self.angle_grab[i]))

            self.servo_grab.angle = self.angle_grab[i]
            self.servo_middle.angle = self.angle_middle[i]
            self.servo_bottom.angle = self.angle_bottom[i]
            
            
            
            time.sleep(1)