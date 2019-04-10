"""
Have a look at the comments. 
"""
# need all these imports
import board
import busio
import adafruit_pca9685

from adafruit_servokit import ServoKit
import time as time

i2c = busio.I2C(board.SCL, board.SDA)
servo = adafruit_pca9685.PCA9685(i2c)

kit = ServoKit(channels=16)

# Set whic servo Yaw,pitch or deploy is allocated to which PIN number.
YAW = kit.servo[12]
PITCH = kit.servo[13]
DEPLOY = kit.servo[14]

# Callibrates begining ANGLES to 0
YAW_angle, PITCH_angle, DEPLOY_angle = 0, 0, 0
#kit.continuous_servo[13].throttle = 1

# Shaun's test that the servo moves, it works
kit.servo[13].angle = 10

# Make sure to put colon after True!
while True:
        # Need an indent here,
        change = input("Move Camera: ")
        if (change == 1):
                DEPLOY_angle = DEPLOY - 90
                time.sleep(1)
                DEPLOY.angle = DEPLOY_angle
                # These don't actually change the angle, you need to also set the angle here.
                # Above is now correct, changing it for the rest will allow you to set the servo.
        elif (change == 2):
                DEPLOY = DEPLOY + 90
                time.sleep(1)
        elif (change == 3):
                PITCH = PITCH + 30
                time.sleep(1)
        elif (change == 4):
                PITCH = PITCH - 30
                time.sleep(1)
        elif (change == 5):
                YAW = YAW - 30
                time.sleep(1)
        elif (change == 6):
                YAW = YAW + 30
                time.sleep(1)
        else:
                print("No command")
