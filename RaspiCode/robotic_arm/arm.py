from interfaces.receiver import Receiver, ReceiverError
from interfaces.actuator import Actuator, ActuatorError
import coreutils.resource_manager as mgr
from enum import Enum

class State(Enum):
    STOPPED = 0
    RUNNING = 1

class RoboticArm(Receiver, Actuator):

    def __init__(self):
        Receiver.__init__(self)
        Actuator.__init__(self)
        self.controller_state = State.STOPPED
        self.angle_1 = 0
        self.angle_2 = 0
        self.angle_3 = 0

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
        print("Starting RoboticArm mode...")
        self.begin_receive()
        self.acquire_motors(mgr.Motors.ARM)
        if not self.have_acquired(mgr.Motors.ARM):
            self.stop()
            return
        self.begin_actuate()
        self.controller_state = State.RUNNING
        print("RoboticArm mode started.")
    
    def stop(self):
        if self.is_running():
            print("Stopping RoboticArm mode...")
            if self.have_acquired(mgr.Motors.ARM):
                self.release_motors(mgr.Motors.ARM)
            try:
                self.disconnect()
            except ReceiverError as e:
                print(str(e))
            self.controller_state = State.STOPPED
            print("RoboticArm mode stopped.")

    def run_on_connection_interrupted(self):
        self.stop()

    def is_running(self):
        if self.controller_state == State.RUNNING:
            return True
        return False

    def set_state_as_running(self):
        self.controller_state = State.RUNNING
