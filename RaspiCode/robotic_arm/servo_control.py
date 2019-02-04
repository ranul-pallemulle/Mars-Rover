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
        self.servo_grab.set_pulse_width_range(700,2600)
        self.servo_middle.set_pulse_width_range(700,2600)
        self.servo_bottom.set_pulse_width_range(700,2600)
#        
        #Max Rotation Range
        self.servo_grab.actuation_range = 180
        self.servo_middle.actuation_range = 180
        self.servo_bottom.actuation_range = 180
        
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
        
    def set_angle(self,grab = 0,middle = 0, bottom = 0):
        for i in  range len(self.angle_grab):
            if self.angle_middle < 0 or self.angle_middle > 180:
                raise Exception( 'Middle servo angle out of range, the  value  was: {}'.format(self.angle_middle[i])

            if self.angle_bottom < 0 or self.angle_middle > 180:
                raise Exception( 'Bottom servo angle out of range, the  value  was: {}'.format(self.angle_bottom[i])

        self.servo_middle.angle = middle #self.angle_middle[0]
        self.servo_bottom.angle = bottom 
	

        self.servo_grab.angle = grab 
        


if __name__ == "__main__":
    
#    fname = "test_data.txt"
#    
#    grab_PIN = 12
#    middle_PIN = 1 
#    bottom_PIN = 13
#
    arm = Robotic_Arm(bottom_PIN=13)
#    
    
     
    while 1:
#        arm.get_values(fname)
        print("Getting Values")
        arm.set_angle(bottom = 0)
        time.sleep(1)
        arm.set_angle(bottom = 45)    
        time.sleep(1)
        arm.set_angle(bottom = 90)    
        time.sleep(1)
        arm.set_angle(bottom = 135)    
        time.sleep(1)
        arm.set_angle(bottom = 180)    
        time.sleep(1)

