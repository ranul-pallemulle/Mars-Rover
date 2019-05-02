import coreutils.configure as cfg
from coreutils.diagnostics import Diagnostics as dg
from functools import wraps
import rpyc
from rpyc.utils.server import ThreadedServer, ThreadPoolServer
from threading import Thread
from socket import socket

''' Utilities for multiprocessing through attached units. '''
class UnitError(Exception):
    pass

main_conn = None
main_server = None

class MainService(rpyc.Service):
    ALIASES = ['CENTRALSERVER']
    unit_list = dict()
            
    def on_connect(self, conn):
        self.conn = conn

    def on_disconnect(self, conn):
        import coreutils.resource_manager as mgr
        import resources.resource as rsc
        dg.print("Unit disconnected.")
        unit = self.__class__.unit_list.pop(conn)
        rsc_list = rsc.Resource.remove_unit_resources(unit)
        for rsc_name in rsc_list.keys():
            mgr.global_resources.remove_resource(rsc_name)
        dg.print("The following resources were removed:")
        for rsc_name in rsc_list.keys():
            dg.print("    "+rsc_name)

    def register_unit_name(self, unitname):
        dg.print("Found unit {}".format(unitname))
        self.__class__.unit_list[self.conn] = unitname

    def register_resource(self, resourcename, port):
        '''Add remote resource to resource list and have resource manager
record its access policy.'''
        import coreutils.resource_manager as mgr
        import resources.resource as rsc
        cli_ip, _ = socket.getpeername(self.conn._channel.stream.sock)
        rsc_conn = rpyc.connect(cli_ip, port)
        result = rsc.Resource.register_remote_resource(
            self.__class__.unit_list[self.conn],resourcename, rsc_conn.root)
        if result:
            result = mgr.global_resources.load_remote_resource(resourcename)
        return result

class ClientService(rpyc.Service):
    pass
    # def on_disconnect(self, conn):
    #     dg.print("Connection lost - cleaning up...")
    #     rsc.Resource.cleanup_servers()
        
    # def exposed_cleanup_resources(self):
    #     dg.print("cleaning up...")
    #     rsc.Resource.cleanup_servers()

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
    cfg.overall_config.set_unitname(unitname)
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
        if cfg.overall_config.running_as_unit:
            res = None          # TODO
        else:
            res = func(*args, **kwargs)
        return res
    return wrapper


