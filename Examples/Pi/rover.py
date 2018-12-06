from joystick import Joystick, State
from gpiozero import Motor

class Rover:
    def __init__(self):
        self.joystick = Joystick(5560)
        self.led = Motor(17,18)

    def connect_joystick(self):
        self.joystick.connect()
        self.joystick.begin()

    def disconnect_joystick(self):
        self.joystick.set_state(State.CLOSE_REQUESTED) # only works if joystick.begin() has been called

    def move(self):
        while True:
            joystick_state = self.joystick.get_state()
            if self.joystick.state == State.CLOSED:
                break
            elif joystick_state == State.RUNNING:
                value = self.joystick.get_value()
                if value >= 0:
                    self.led.forward(value)
                else:
                    self.led.backward(-value)
        
