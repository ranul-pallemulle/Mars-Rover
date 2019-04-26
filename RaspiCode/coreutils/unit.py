import coreutils.configure as cfg
from coreutils.diagnostics import Diagnostics as dg
import coreutils.resource_manager as mgr
from functools import wraps
import rpyc
from rpyc.utils.server import ThreadedServer, ThreadPoolServer
import resources.resource as rsc
from threading import Thread
from socket import socket

''' Utilities for multiprocessing through attached units. '''
class UnitError(Exception):
    pass

main_conn = None
main_server = None

class MainService(rpyc.Service):
    unit_list = []
            
    def on_connect(self, conn):
        self.conn = conn

    def on_disconnect(self, conn):
        pass

    def register_unit_name(self, unitname):
        dg.print("Found unit {}".format(unitname))
        # self.__class__.unit_list.append(self.conn)

    def register_resource(self, resourcename, port):
        if resourcename in rsc.Resource.resource_list:
            dg.print("WARNING: Resource name {} already registered. Skipping...".format(resourcename))
        else:
            cli_ip, _ = socket.getpeername(self.conn._channel.stream.sock)
            rsc_conn = rpyc.connect(cli_ip, port)
            rsc.Resource.resource_list[resourcename] = rsc_conn.root
            mgr.global_resources.load_remote_resources()
        

class ClientService(rpyc.Service):
    def on_disconnect(self):
        dg.print("Connection lost - cleaning up...")
        rsc.Resource.cleanup_servers()n
        
    def exposed_cleanup_resources(self):
        dg.print("cleaning up...")
        rsc.Resource.cleanup_servers()

def activate_main_unit_services():
    global main_server
    main_server = ThreadedServer(MainService(), port=18861, protocol_config={
        'allow_public_attrs': True,
    })
    thread = Thread(target=main_server.start, args=[])
    thread.start()

def deactivate_main_unit_services():
    global main_server
    # MainService.cleanup_remote_resources()
    main_server.close()    

def register_unit_name(unitname):
    if not cfg.Configuration.ready():
        raise UnitError("Settings file not parsed.")
    dg.print("Registering unit {}...".format(unitname))
    main_ip = cfg.overall_config.main_ip()
    global main_conn
    main_conn = rpyc.connect(main_ip, 18861, service=ClientService)
    dg.print("Found main unit: {}".format(main_conn.root.get_service_name()))
    main_conn.root.register_unit_name(unitname)
    dg.print("Registered.")

    
def maybe_runs_on_unit(func):
    '''Wraps a function and uses remote procedure calls if running on a
unit.'''
    @wraps(func)
    def wrapper(*args, **kwargs):
        if cfg.OverallConfiguration.running_as_unit:
            res = None          # TODO
        else:
            res = func(*args, **kwargs)
        return res
    return wrapper


