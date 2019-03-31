from interfaces.receiver import Receiver, ReceiverError
from interfaces.actuator import Actuator, ActuatorError
from interfaces.opmode import OpMode, OpModeError
import coreutils.resource_manager as mgr

class Dummy(Receiver, Actuator, OpMode):
    def __init__(self):
        Receiver.__init__(self)
        Actuator.__init__(self)
        OpMode.__init__(self)

        self.register_name("Dummy")

        self.val1 = 0
        self.val2 = 0

    def store_received(self, recvd_list):
        if len(recvd_list) != 2:
            return None
        self.val1 = recvd_list[0]
        self.val2 = recvd_list[1]
        return 'Got em'

    def get_values(self, motor_set):
        with self.condition:
            return (self.val1, self.val2)

    def start(self, args):
        try:
            port = args[0]
            self.connect(port)
            self.begin_receive()
        except(IndexError, TypeError):
            raise OpModeError("Need a valid port number.")
        except ReceiverError as e:
            raise OpModeError(str(e))
        try:
            self.acquire_motors(mgr.Motors.WHEELS)
        except ActuatorError as e:
            self.stop()
            raise OpModeError(str(e))
        if self.have_acquired(mgr.Motors.WHEELS):
            self.begin_actuate()
        else:
            self.stop()

    def stop(self, args):
        if self.have_acquired(mgr.Motors.WHEELS):
            self.release_motors(mgr.Motors.WHEELS)
        if self.connection_active():
            try:
                self.disconnect()
            except ReceiverError as e:
                raise OpModeError(str(e))

    def submode_command(self, args):
        pass

    def run_on_connection_interrupted(self):
        if self.is_running():
            self.stop(None)
