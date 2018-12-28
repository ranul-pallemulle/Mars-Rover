from interfaces.receiver import Receiver, ReceiverError
from interfaces.actuator import Actuator, ActuatorError
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
        return (self.xval, self.yval)

    def get_xval(self):
        with self.value_lock:
            return self.xval

    def get_yval(self):
        with self.value_lock:
            return self.yval

    def stop(self):
        self.disconnect()
        self.release_motors()
