from interfaces.receiver import Receiver, ReceiverError
from threading import Lock

class RoboticArm(Receiver):

    angle_1 = 0
    angle_2 = 0
    angle_3 = 0
    value_lock = Lock()

    def store_received(self, recvd_list):
        if len(recvd_list) != 3:
            return None
        try:
            thet_1 = int(recvd_list[0])
            thet_2 = int(recvd_list[1])
            thet_3 = int(recvd_list[2])
        except (ValueError, IndexError) as e:
            print(str(e))
            return None
        else:
            if thet_1 <= 180 and thet_1 >= -180\
               and thet_2 <= 180 and thet_2 >= -180\
               and thet_3 <= 180 and thet_3 >= -180:
                with self.value_lock:
                    self.angle_1 = thet_1
                    self.angle_2 = thet_2
                    self.angle_3 = thet_3
                return 'ACK'
            else:
                return 'ERR:RANGE'

    def get_angle_1(self):
        with self.value_lock:
            return self.angle_1

    def get_angle_2(self):
        with self.value_lock:
            return self.angle_2

    def get_angle_3(self):
        with self.value_lock:
            return self.angle_3
