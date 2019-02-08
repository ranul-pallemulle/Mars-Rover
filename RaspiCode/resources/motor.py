"""
I think the issue is perhaps hardware/ pluggin things into the wrong places/ motor might be a bit old. I AM NOT TOO SURE

UPDATE: It is probably because of insufficient voltage
"""



import sys
import time
import RPi.GPIO as GPIO
from PCA9685 import PWM

class Motor:
    
    def __init__(self):
        self.name = 12
        self.mode = GPIO.getmode()
        GPIO.cleanup()
        GPIO.setmode(GPIO.BOARD)
        self.motor_1 = PWM(PIN_NUMBER)

    def get_values(self,values):
        GPIO.setup(motor_1,GPIO.OUT)

        pass 
        
    def move_forward(self):
        GPIO.output(motor_1,GPIO.HIGH)
        
    def move_backward(self):
        GPIO.output(motor_1,GPIO.HIGH)
        
    def turn_right(self):
        GPIO.output(motor_1,GPIO.HIGH)

    def turn_left(self):
        GPIO.output(motor_1,GPIO.HIGH)

            



#def forward(x):
#    GPIO.output(motor,GPIO.HIGH)
#    time.sleep(x)
#    GPIO.output(forward_PIN, GPIO.LOW)
#
#def backwards(x):
#    GPIO.output(forward_PIN,GPIO.HIGH)
#    time.sleep(x)
#    GPIO.output(forward_PIN, GPIO.LOW)

#
#
#GPIO.cleanup()
#
#forward(5)
        
if __name__ == "__main__":
    motor_1_PIN_1 = 12
    motor_1_PIN_2 = 13
    
    mot = Motor()
    mot.get_values()
    
    
