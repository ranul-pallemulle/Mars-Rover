import board
import busio
import adafruit_pca9685
from adafruit_servokit import ServoKit

i2c = busio.I2C(board.SCL,board.SDA)
kit = ServoKit(channels=16)
servo = adafruit_pca9685.PCA9685(i2c)

kit.servo[13].angle = 50
kit.servo[14].angle = 100
