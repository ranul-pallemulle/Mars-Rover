from interfaces.receiver import Receiver, ReceiverError
from interfaces.actuator import Actuator, ActuatorError
import coreutils.resource_manager as mgr
from enum import Enum

class State(Enum):
    STOPPED = 0
    RUNNING = 1

class Joystick(Receiver,Actuator):

    def __init__(self):
        Receiver.__init__(self)
        Actuator.__init__(self)
        self.controller_state = State.STOPPED
        self.xval = 0
        self.yval = 0        
        
    def store_received(self, recvd_list):
        '''Store values received from remote, after checking that they are of the right format. Return a reply in the form of a string to be sent back.'''
        if len(recvd_list) != 2:
            return None
        try:
            x = int(recvd_list[0])
            y = int(recvd_list[1])
        except (ValueError, IndexError) as e:
            print(str(e))
            return None
        else:
            if x<=100 and x>=-100 and y<=100 and y>=-100:
                with self.condition:
                    self.xval = x
                    self.yval = y
                    self.condition.notify() # tell actuation thread
                                            # that values are ready
                return 'ACK'
            else:
                return 'ERR:RANGE'

    def get_values(self, motor_set):
        '''Overriden from actuator. motor_set specifies the type of motors
(wheel, arm, etc) and is used only if we have multiple types of motors
being controlled simultaneously. In this case, there's only the wheel
motors so we don't need to query motor_set.'''
        with self.condition:    # simply lock
            return (self.xval, self.yval)

    def start(self):
        print("Starting Joystick mode...")
        self.controller_state = State.RUNNING
        self.begin_receive()
        self.acquire_motors(mgr.Motors.WHEELS)
        if not self.have_acquired(mgr.Motors.WHEELS):
            self.stop()
            return
        self.begin_actuate()
        print("Joystick mode started.")
        
    def stop(self):
        if self.is_running():
            print("Stopping Joystick mode...")
            if self.have_acquired(mgr.Motors.WHEELS):
                self.release_motors(mgr.Motors.WHEELS)
            try:
                self.disconnect()
            except ReceiverError as e:
                print(str(e))
            self.controller_state = State.STOPPED
            print("Joystick mode stopped.")

    def run_on_connection_interrupted(self):
        '''Runs if connection to remote is interrupted.'''
        self.stop()

    def is_running(self):
        if self.controller_state == State.RUNNING:
            return True
        return False

    def set_state_as_running(self):
        self.controller_state = State.RUNNING

