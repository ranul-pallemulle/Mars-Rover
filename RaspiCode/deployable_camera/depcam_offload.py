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
            dg.print("Wrong length of recvd list: actual is {}".format(len(recvd_list)))
            return None
        try:
            thet_1 = int(recvd_list[0])
            thet_2 = int(recvd_list[1])
            thet_3 = int(recvd_list[2])
        except (ValueError, IndexError) as e:
            dg.print(str(e))
            return None
        else:
            try:
                self.clisock.write("{},{},{}".format(thet_1,thet_2,thet_3))
                self.clisock.read() # perform the read to stay in sync
                time.sleep(0.02) # strange error without this
                return 'ACK'
            except ClientSocketError as e:
                # self.run_on_connection_interrupted()
                dg.print("ERROR: "+str(e))
                dg.print("Bad values: {},{},{}".format(recvd_list[0],recvd_list[1],recvd_list[2]))
                return None

        
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
        # while self.clisock.is_open() and (self.clisock.check_poll_success() == False):
        #     pass
        # if not self.clisock.is_open():
        #     raise OpModeError('Poll socket was closed.')
        # Thread(target=self.check_alive, args=[]).start() # periodically check for close
        try:
            self.begin_receive()
        except ReceiverError as e:
            raise OpModeError(str(e))
        self.ip = cfg.overall_config.get_connected_ip()
        # time.sleep(5)
        dg.print("Starting stream redirection...")
        redirect.start(self.attached_unit_ip, 5520, self.ip, 5520)
        dg.print("Stream redirection started.")
        
    def stop(self, args):
        if self.connection_active():
            try:
                self.disconnect()
            except ReceiverError as e:
                raise OpModeError(str(e))
        redirect.stop()
        try:
            if self.clisock.is_open(): # only way to check if unit is reachable
                unit.send_command(self.attached_unit, "STOP DepCamera")
                self.clisock.close()
        except unit.UnitError as e:
            dg.print("Warning: sending command 'STOP DepCamera' to unit {} failed.".format(self.attached_unit))

        
    def submode_command(self, args):
        dg.print('DepCamera_OFFLOAD mode does not take submode commands.')
        
    def run_on_connection_interrupted(self):
        if self.is_running():
            self.stop(None)
            
    # def check_alive(self):
    #     while self.is_running():
    #         if not self.clisock.is_open():
    #             dg.print("Poll socket closed by unit")
    #             self.run_on_connection_interrupted()
    #             break
    #         time.sleep(2)
