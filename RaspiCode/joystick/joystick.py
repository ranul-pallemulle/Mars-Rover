from interfaces.receiver import Receiver, ReceiverError
from threading import Lock

class Joystick(Receiver):

    xval = 0
    yval = 0
    value_lock = Lock()

    def store_received(self, recvd_list):
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

    def get_xval(self):
        with self.value_lock:
            return self.xval

    def get_yval(self):
        with self.value_lock:
            return self.yval
