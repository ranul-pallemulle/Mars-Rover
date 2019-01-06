from interfaces.receiver import Receiver, ReceiverError
from interfaces.actuator import Actuator, ActuatorError
import coreutils.resource_manager as mgr

class RoboticArm(Receiver, Actuator):

    angle_1 = 0
    angle_2 = 0
    angle_3 = 0

    def __init__(self):
        Receiver.__init__(self)
        Actuator.__init__(self)

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
                with self.condition:
                    self.angle_1 = thet_1
                    self.angle_2 = thet_2
                    self.angle_3 = thet_3
                    self.condition.notify()
                return 'ACK'
            else:
                return 'ERR:RANGE'

    def get_values(self, motor_set):
        with self.condition:
            return (self.angle_1, self.angle_2, self. angle_3)

    def start(self):
        self.begin_receive()
        self.acquire_motors(mgr.Motors.ARM)
        if not self.have_acquired(mgr.Motors.ARM):
            self.stop()
        self.begin_actuate()
    
    def stop(self):
        if self.have_acquired(mgr.Motors.ARM):
            self.release_motors(mgr.Motors.ARM)
        self.disconnect()

    def run_on_connection_interrupted(self):
        if self.have_acquired(mgr.Motors.ARM):
            self.release_motors(mgr.Motors.ARM)
