import board
import busio
from adafruit_servokit import ServoKit
import adafruit_pca9685

i2c = busio.I2C(board.SCL,board.SDA)
servo = adafruit_pca9685.PCA9685(i2c)
kit = ServoKit(channels=16)

kit.servo[12].angle = 120

#kit.servo[11].angle = 180
#kit.servo[11].angle = 0

kit.servo[13].angle= 100
