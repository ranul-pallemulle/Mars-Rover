import board
import busio
from adafruit_servokit import ServoKit
import adafruit_pca9685
import time as time

i2c = busio.I2C(board.SCL,board.SDA)
servo = adafruit_pca9685.PCA9685(i2c)
kit = ServoKit(channels=16)

kit.servo[13].actuation_range = 360
kit.servo[13].set_pulse_width_range(100, 4000)

while True:
    angle = input("Angle?")
    kit.servo[13].angle = int(angle)
    time.sleep(1)

#kit.servo[11].angle = 180
#kit.servo[11].angle = 0

    #kit.servo[13].angle= 50
    #time.sleep(1)
    #kit.servo[12].angle = 0
    #kit.servo[13].angle = 0
    #time.sleep(1)
