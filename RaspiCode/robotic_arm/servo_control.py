import board
import busio
from adafruit_servokit import ServoKit
import adafruit_pca9685
import time as time

class Robotic_Arm:
    """
    Robotic Arm Control, in order to control the 3 servo motors
    """
    def __init__(self,grab_PIN = 12,middle_PIN = 13,bottom_PIN = 14):
        self.i2c = busio.I2C(board.SCL,board.SDA)
        self.servo = adafruit_pca9685.PCA9685(self.i2c)
        self.kit = ServoKit(channels=16)
        
        #3 Servos, defines PIN numbers
        self.servo_grab = self.kit.servo[grab_PIN]
        self.servo_middle = self.kit.servo[middle_PIN]
        self.servo_bottom = self.kit.servo[bottom_PIN]
        
        #Max Rotation Range
        self.servo_grab.actuation_range = 10
        self.servo_middle.actuation_range = 90
        self.servo_bottom.actuation_range = 90
        
    def get_values(self,fname):
        """
        Obtains values from joystick output
        """
        file = open(fname,"r")
        lines= file.readlines()
        self.angle_grab=[]
        self.angle_middle=[]
        self.angle_bottom=[]
        for line in range(len(lines)):
            self.angle_grab.append(int(lines[line].split()[0]))
            self.angle_middle.append(int(lines[line].split()[1]))
            self.angle_bottom.append(int(lines[line].split()[2]))
            print(self.angle_middle)
        
    def set_angle(self):
        self.servo_grab.angle = self.angle_grab[0]
        self.servo_middle.angle = self.angle_middle[0]
        self.servo_bottom.angle = self.angle_bottom[0]
        print(self.angle_bottom[0])
        
if __name__ == "__main__":
    
    fname = "test_data.txt"
    
    grab_PIN = 12
    middle_PIN = 13 
    bottom_PIN = 14

    arm = Robotic_Arm(grab_PIN,middle_PIN,bottom_PIN)
    
    while 1:
        arm.get_values(fname)
        print("Getting Values")
        time.sleep(1)
            
        arm.set_angle()    

