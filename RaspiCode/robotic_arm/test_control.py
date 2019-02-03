import board
import busio
import adafruit_pca9685
from adafruit_servokit import ServoKit
import time as time
i2c = busio.I2C(board.SCL,board.SDA)

servo = adafruit_pca9685.PCA9685(i2c)

kit = ServoKit(channels=16)

kit.servo[13].actuation_range = 120
kit.servo[13].minimum_range = 40

kit.servo[13].angle = 30

#while 1:
#    #kit.servo[13].angle = 120
#    kit.servo[12].angle = 140
#    kit.servo[13].angle = 140
#    kit.servo[14].angle = 0
#    time.sleep(1)
#    kit.servo[12].angle = 90
#    kit.servo[13].angle = 90
#    time.sleep(1)
##kit.continuous_servo[13].throttle = 1
