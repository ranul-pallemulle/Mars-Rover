import rpyc
import socket
from threading import Thread
from rpyc.utils.server import ThreadedServer
from coreutils.diagnostics import Diagnostics as dg
import coreutils.configure as cfg


class MainService(rpyc.Service):
    '''Services offered by main unit through remote procedure calls by attached 
units.'''
    ALIASES=['CENTRALSERVER'] # attached unit 
    unit_list = dict()
    
    def on_connect(self, conn):
        self.conn = conn


    def on_disconnect(self, conn):
        for key in self.__class__.unit_list.keys():
            if self.__class__.unit_list[key] == conn:
                dg.print("Unit {} disconnected.".format(key))
                return
        dg.print("Warning: unknown unit disconnected.")


    def register_unit_name(self, unitname):
        self.__class__.unit_list[unitname] = self.conn
        dg.print("Found unit {}".format(unitname))


# general functions for main unit
def activate_main_unit_services():
    global main_server
    main_server = ThreadedServer(MainService(), port=18861, protocol_config={
        'allow_public_attrs': True,
    })
    Thread(target=main_server.start, args=[]).start()
    dg.print("Started main unit services.")
    
def deactivate_main_unit_services():
    global main_server
    main_server.close()
    dg.print("Stopped main unit services.")
    
# general functions for attached unit
def register_unit(unitname):
    dg.print("Registering unit name {}...".format(unitname))
    cfg.overall_config.set_unitname(unitname)
    try:
        main_hostname = cfg.overall_config.main_hostname()
    except cfg.ConfigurationError as e:
        dg.print(str(e))
        return False
    main_ip = socket.gethostbyname(main_hostname)
    try:
        main_conn = rpyc.connect(main_ip, 18861)
    except ConnectionRefusedError as e:
        dg.print(str(e))
        return False
    dg.print("Found main unit '{}'".format(main_conn.root.get_service_name()))
    main_conn.root.register_unit_name(unitname)
    dg.print("Registered.")
    return True
