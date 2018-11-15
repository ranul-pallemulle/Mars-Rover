import joystick
from gpiozero import Motor

class Rover:
    def __init__(self):
        self.joystick = Joystick(5560)
        self.led = Motor(17,18)

    def connect_joystick(self):
        self.joystick.connect()
        self.joystick.begin()

    def move(self):
        while True:
            value = self.joystick.get_value()
            if value >= 0:
                self.led.forward(value)
            else:
                self.led.backward(-value)
        
