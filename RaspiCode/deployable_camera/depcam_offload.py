import coreutils.unit as unit
from coreutils.diagnostics import Diagnostics as dg
from interfaces.receiver import Receiver, ReceiverError
from interfaces.opmode import OpMode, OpModeError

class DeployableCameraOffload(Receiver, OpMode):
    
    def __init__(self):
        Receiver.__init__(self)
        OpMode.__init__(self)
        self.register_name("DepCamera_OFFLOAD")
        self.attached_unit = None
        
    def store_received(self, recvd_list):
        pass
        
    def start(self, args):
        '''port=args[1] will be used as local port. Attached unit will use
        port+1 so that main and attached units can run on the same computer.'''
        try:
            self.attached_unit = args[0]
            port = args[1]
            self.connect(port)
        except (IndexError, TypeError):
            raise OpModeError("Invalid arguments to start depcam_offload or need a valid port number")
        unit.send_command(self.attached_unit, "START DepCamera {}".format(int(port)+1))
        try:
            self.begin_receive()
        except ReceiverError as e:
            raise OpModeError(str(e))
        
    def stop(self, args):
        if self.connection_active():
            try:
                self.disconnect()
            except ReceiverError as e:
                raise OpModeError(str(e))
            
        unit.send_command(self.attached_unit, "STOP DepCamera")
        
    def submode_command(self, args):
        dg.print('DepCamera_OFFLOAD mode does not take submode commands.')
        
    def run_on_connection_interrupted(self):
        if self.is_running():
            self.stop(None)
