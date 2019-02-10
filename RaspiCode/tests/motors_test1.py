import board
import busio
import adafruit_pca9685
from adafruit_servokit import ServoKit
import time as time
i2c = busio.I2C(board.SCL,board.SDA)

servo = adafruit_pca9685.PCA9685(i2c)

kit = ServoKit(channels=16)

#kit.servo[13].actuation_range = 120
#kit.servo[13].minimum_range = 40

kit.servo[14].set_pulse_width_range(750,2250) #750,2250 600,2500; 200,2200 - like there's a limit to rotation

kit.servo[14].angle = 30

value = int(input("value  = "))
kit.servo[14].angle = value
#kit.continuous_servo[14].throttle = -1


#Testing many values
#for i in range(20):
#    a = i +1
#    kit.servo[14].angle = 180/a
#    print(180/a)
#    time.sleep(1)
#
#for i in range (20):
#    kit.servo[14].angle = i* (180 / 20)
#    print( i * 180/20)
#    time.sleep(1)
#

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
