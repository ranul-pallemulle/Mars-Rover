from interfaces.receiver import Receiver, ReceiverError
from interfaces.actuator import Actuator, ActuatorError
import coreutils.resource_manager as mgr

class Joystick(Receiver,Actuator):

    xval = 0
    yval = 0

    def __init__(self):
        Receiver.__init__(self)
        Actuator.__init__(self)
        
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
        self.begin_receive()
        self.acquire_motors(mgr.Motors.WHEELS)
        if not self.have_acquired(mgr.Motors.WHEELS):
            self.stop()
        self.begin_actuate()
        
    def stop(self):
        if self.have_acquired(mgr.Motors.WHEELS):
            self.release_motors(mgr.Motors.WHEELS)
        self.disconnect()

    def run_on_connection_interrupted(self):
        '''Runs if connection to remote is interrupted.'''
        if self.have_acquired(mgr.Motors.WHEELS):
            self.release_motors(mgr.Motors.WHEELS)

