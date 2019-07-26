import streamredirect as redirect
import coreutils.unit as unit
import coreutils.configure as cfg
from coreutils.diagnostics import Diagnostics as dg
from coreutils.client_socket import ClientSocket, ClientSocketError
from interfaces.receiver import Receiver, ReceiverError
from interfaces.opmode import OpMode, OpModeError
from threading import Thread
import time

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
        try:
            self.attached_unit_ip = unit.MainService.unit_list[self.attached_unit][1]
        except KeyError as e:
            raise OpModeError("Could not start depcam_offload: unit probably detached.")        
        self.clisock = ClientSocket()
        # start attempting connection (poll) to attached unit's Receiver for values
        Thread(target=self.clisock.connect_polled, args=[self.attached_unit_ip, int(port)+1]).start()
        try: # blocking call to start unit's depcamera mode
            unit.send_command(self.attached_unit, "START DepCamera {}".format(int(port)+1))
        except unit.UnitError as e:
            raise OpModeError(str(e))
        # If this point is reached depcamera mode on unit has started successfully
        while self.clisock.is_open() and (self.clisock.check_poll_succes() == False):
            pass # wait for connection to unit's Receiver or for clisock to fail
        if not self.clisock.is_open():
            raise OpModeError('Poll socket was closed.')
        Thread(target=self.check_alive, args=[]).start() # periodically check for close
        try:
            self.begin_receive()
        except ReceiverError as e:
            raise OpModeError(str(e))
        self.ip = cfg.overall_config.get_connected_ip()
        # time.sleep(5)
        redirect.start(self.attached_unit_ip, 5520, self.ip, 5520)
        
    def stop(self, args):
        if self.connection_active():
            try:
                self.disconnect()
            except ReceiverError as e:
                raise OpModeError(str(e))
        redirect.stop()
        try:
            unit.send_command(self.attached_unit, "STOP DepCamera")
        except unit.UnitError as e:
            dg.print("Warning: sending command 'STOP DepCamera' to unit {} failed.".format(self.attached_unit))
        self.clisock.close()
        
    def submode_command(self, args):
        dg.print('DepCamera_OFFLOAD mode does not take submode commands.')
        
    def run_on_connection_interrupted(self):
        if self.is_running():
            self.stop(None)
            
    def check_alive(self):
        while True:
            if not self.clisock.is_open():
                dg.print("Poll socket closed by unit")
                self.stop(None)
            time.sleep(2)
