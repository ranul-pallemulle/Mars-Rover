import coreutils.configure as cfg
import coreutils.unit as unit
import coreutils.resource_manager as mgr
from coreutils.diagnostics import Diagnostics as dg
from interfaces.receiver import Receiver, ReceiverError
from interfaces.actuator import Actuator, ActuatorError
from interfaces.opmode import OpMode, OpModeError

class DeployableCamera(Receiver, Actuator, OpMode):
    
    def __init__(self):
        Receiver.__init__(self)
        Actuator.__init__(self)
        OpMode.__init__(self)
        
        self.register_name("DepCamera")
        
        self.angle_bottom = 0
        self.angle_middle = 0
        self.angle_top = 0
        
    
    def store_received(self, recvd_list):
        if len(recvd_list) != 3:
            return None
        try:
            thet_1 = int(recvd_list[0])
            thet_2 = int(recvd_list[1])
            thet_3 = int(recvd_list[2])
        except (ValueError, IndexError) as e:
            dg.print(str(e))
            dg.print("Bad values: {},{},{}".format(recvd_list[0],recvd_list[1],recvd_list[2]))
            return None
        else:
            with self.condition:
                self.angle_top = thet_1
                self.angle_middle = thet_2
                self.angle_bottom = thet_3
                self.condition.notify()
            return 'ACK'


    def get_values(self, motor_set):
        with self.condition:
            return (self.angle_top, self.angle_middle, self.angle_bottom)


    def start(self, args):
        try:
            port = args[0]
            self.connect(port)
            self.begin_receive()
        except (IndexError, TypeError):
            raise OpModeError("Need a valid port number.")
        except ReceiverError as e:
            raise OpModeError(str(e))        
        try:
            self.acquire_motors("DeployableCamera")
        except ActuatorError as e:
            self.stop(None)
            raise OpModeError(str(e))
        if self.have_acquired("DeployableCamera"):
            self.begin_actuate()
        else:
            self.stop(None)
            raise OpModeError('Could not get access to deployable camera motors.')
        mgr.global_resources.get_shared("IPCamera")
        if cfg.overall_config.running_as_unit:
            with unit.cli_wait:
                unit.cli_wait.notify()
        

    def stop(self, args):
        mgr.global_resources.release("IPCamera")
        if self.have_acquired("DeployableCamera"):
            self.release_motors("DeployableCamera")
        if self.connection_active():
            try:
                self.disconnect()
            except ReceiverError as e:
                raise OpModeError(str(e))
        if cfg.overall_config.running_as_unit:
            with unit.cli_wait:
                unit.cli_wait.notify()


    def submode_command(self, args):
        dg.print('DeployableCamera mode does not take submode commands.')
        if cfg.overall_config.running_as_unit:
            with unit.cli_wait:
                unit.cli_wait.notify()


    def run_on_connection_interrupted(self):
        if self.is_running():
            self.stop(None)

