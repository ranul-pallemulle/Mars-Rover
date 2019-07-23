import coreutils.unit as unit
from coreutils.diagnostics import Diagnostics as dg
from coreutils.client_socket import ClientSocket, ClientSocketError
from interfaces.receiver import Receiver, ReceiverError
from interfaces.opmode import OpMode, OpModeError

class DeployableCameraOffload(Receiver, OpMode):
    
    def __init__(self):
        Receiver.__init__(self)
        OpMode.__init__(self)
        self.register_name("DepCamera_OFFLOAD")
        self.attached_unit = None
        self.attached_unit_ip = None
        self.clisock = None
        
    def store_received(self, recvd_list):
        if len(recvd_list) != 3:
            return None
        try:
            thet_1 = int(recvd_list[0])
            thet_2 = int(recvd_list[1])
            thet_3 = int(recvd_list[2])
        except (ValueError, IndexError) as e:
            dg.print(str(e))
            return None
        else:
            self.clisock.write("{},{},{}".format(thet_1,thet_2,thet_3))
            return 'ACK'
        
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
        self.attached_unit_ip = unit.MainService.unit_list[self.attached_unit][1]
        self.clisock = ClientSocket()
        self.clisock.connect(self.attached_unit_ip, int(port)+1)
        
    def stop(self, args):
        if self.connection_active():
            try:
                self.disconnect()
            except ReceiverError as e:
                raise OpModeError(str(e))
        unit.send_command(self.attached_unit, "STOP DepCamera")
        self.clisock.close()
        
    def submode_command(self, args):
        dg.print('DepCamera_OFFLOAD mode does not take submode commands.')
        
    def run_on_connection_interrupted(self):
        if self.is_running():
            self.stop(None)
