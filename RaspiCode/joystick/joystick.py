from interfaces.receiver import Receiver, ReceiverError
from interfaces.actuator import Actuator, ActuatorError
from coreutils.resource_manager import Motors
from threading import Lock

class Joystick(Receiver,Actuator):

    xval = 0
    yval = 0
    value_lock = Lock()

    def __init__(self, resource_manager):
        Receiver.__init__(self)
        Actuator.__init__(self, resource_manager)
        
    def store_received(self, recvd_list):
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
                with self.value_lock:
                    self.xval = x
                    self.yval = y
                return 'ACK'
            else:
                return 'ERR:RANGE'

    def get_values(self, motor_set):
        '''Overriden from actuator. motor_set specifies the type of motors
(wheel, arm, etc) and is used only if we have multiple types of motors
being controlled simultaneously. In this case, there's only the wheel
motors so we don't need to query motor_set.'''
        with self.value_lock:
            return (self.xval, self.yval)

    def start(self):
        self.begin_receive()
        self.acquire_motors(Motors.WHEELS)
        self.begin_actuate()
        
    def stop(self):
        self.release_motors(Motors.WHEELS)
        self.disconnect()

