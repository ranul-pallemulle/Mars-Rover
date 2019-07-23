import rpyc
import socket
from threading import Thread, Event
from rpyc.utils.server import ThreadedServer
from coreutils.diagnostics import Diagnostics as dg
import coreutils.configure as cfg

main_conn = None # global instance of MainService on main unit
main_server = None # global instance of ThreadedServer using main_conn
client_conn = None # global instance of connection to main unit on attached unit
close_event = Event()

class MainService(rpyc.Service):
    '''Services offered by main unit through remote procedure calls by attached 
units.'''
    ALIASES=['CENTRALSERVER'] # attached unit 
    unit_list = dict()
    
    def on_connect(self, conn):
        self.conn = conn


    def on_disconnect(self, conn):
        key_to_remove = None
        for key in self.__class__.unit_list.keys():
            _conn,_,_ = self.__class__.unit_list[key]
            if _conn == conn:
                dg.print("Unit {} disconnected.".format(key))
                key_to_remove = key
        if key_to_remove is not None:
            self.__class__.unit_list.pop(key_to_remove)
        else:
            dg.print("Warning: unknown unit disconnected.")


    def exposed_register_unit_name(self, unitname):
        client_ip,_ = self.conn._config['endpoints'][1]
        self.__class__.unit_list[unitname] = [self.conn, client_ip, None]
        dg.print("Found unit {} with IP address {}".format(unitname, client_ip))
        

    def exposed_register_command_server(self, unitname, port):
        _,cli_ip,_ = self.__class__.unit_list[unitname]
        comm_conn = rpyc.connect(cli_ip, port)
        self.__class__.unit_list[unitname][2] = comm_conn
        
        
class CommandService(rpyc.Service):
    '''Service on attached unit for accepting commands from the main unit.'''
    def on_disconnect(self, conn):
        print("Main unit disconnected. Shutting down...")
        close_event.set()

    def exposed_accept(self, command):
        dg.print("Command received on command service: {}".format(command))


# general functions to be run on main unit
def activate_main_unit_services():
    global main_server, main_conn
    main_conn = MainService()
    main_server = ThreadedServer(main_conn, port=18868)
    Thread(target=main_server.start, args=[]).start()
    dg.print("Started main unit services.")
    
def deactivate_main_unit_services():
    global main_server
    main_server.close()
    dg.print("Stopped main unit services.")
    
def send_command(unitname, command):
    comm = MainService.unit_list[unitname][2]
    comm.root.accept(command)

# general functions to be run on attached unit
def register_unit(unitname):
    dg.print("Registering unit name {}...".format(unitname))
    cfg.overall_config.set_unitname(unitname)
    try:
        main_hostname = cfg.overall_config.main_hostname()
    except cfg.ConfigurationError as e:
        dg.print(str(e))
        return False
    main_ip = socket.gethostbyname(main_hostname)
    global client_conn, command_server# needed to keep client_conn alive
    try:
        client_conn = rpyc.connect(main_ip, 18868)
    except ConnectionRefusedError as e:
        dg.print(str(e))
        return False
    dg.print("Found main unit '{}'".format(client_conn.root.get_service_name()))
    client_conn.root.register_unit_name(unitname)
    command_server = ThreadedServer(CommandService, port=18869)
    Thread(target=command_server.start, args=[]).start()
    client_conn.root.register_command_server(unitname, 18869)
    dg.print("Registered.")
    Thread(target=wait_for_close, args=[command_server]).start()
    return True

def wait_for_close(command_server):
    close_event.wait()
    command_server.close()
