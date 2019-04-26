from enum import Enum
import importlib
import os
import coreutils.configure as cfg
from coreutils.diagnostics import Diagnostics as dg
import coreutils.unit as unit
import rpyc
from threading import Thread

class Policy(Enum):
    UNIQUE = 0
    SHARED = 1

class ResourceRawError(Exception):
    '''Exception class raised by Resource.'''
    pass

class Resource(rpyc.Service):
    '''Base class for all resources. All resources (like motors, camera,
etc) should inherit from this class and register themselves to be
available to the resource manager and (hence) to the rest of the program.
    '''

    port_offs = 0
    resource_list = dict()      # resource instances stored under their registered names.
    servers = []

    def on_connect(self, conn):
        dg.print("Got connection on {}".format(self.__class__.__name__))

    def on_disconnect(self, conn):
        dg.print("Got disconnect on {}".format(self.__class__.__name__))

    @classmethod
    def resources_initialise(cls):
        '''Look for derived clases in directories specified in the settings
file. Initialise them to register them and add to resource_list.'''
        try:
            dir_list = cfg.overall_config.resources_directories()
        except cfg.ConfigurationError as e:
            raise ResourceRawError(str(e))
        if not dir_list:
            dg.print("WARNING: no resource directories specified.")
        for folder in dir_list:
            if not folder:
                dg.print("WARNING: no resource modules found.")
                return
            if folder.endswith('.py'): # not a folder but a file
                folder = folder.split('.py')[0]
                path = folder.replace('/','.')                
                try:
                    importlib.import_module(path)
                except FileNotFoundError as e:
                    raise ResourceRawError('Error in resource files list. Check settings file. : \n'+str(e))
            else:               # is a folder; check inside
                try:
                    for filename in os.listdir(folder):
                        if str(filename).endswith('.py'):
                            importlib.import_module(folder+'.'+str(filename).split('.')[0])
                except FileNotFoundError as e:
                    raise ResourceRawError('Error in resource directories list. Check settings file. : \n'+str(e))
        for subcls in cls.__subclasses__():
            try:
                subcls()
            except TypeError as e:
                raise ResourceRawError(str(e))

    def __init__(self):
        self.policy = None

    def _rpyc_setattr(self, name, value):
        return setattr(self, name, value)
    
    @classmethod
    def cleanup_servers(cls):
        dg.print("server list length: {}".format(len(cls.servers)))
        while cls.servers:
            thread = cls.servers.pop()
            thread.close()

    def register_name(self, name):
        '''Store resource instance in the resource_list. The key is the
provided name. The policy refers to whether access to it should be
unique or shared. See resource manager for more information on
policy. 
        '''
        if cfg.overall_config.running_as_unit:
            start_port = 19200  # port numbers for use with resources.
            port_offs = self.__class__.__bases__[0].port_offs
            thisserver = rpyc.utils.server.ThreadedServer(self, port=start_port+port_offs, protocol_config={
                'allow_public_attrs': True,
                'allow_pickle': True,
            })
            thread = Thread(target=thisserver.start, args=[])
            thread.start()
            self.__class__.__bases__[0].servers.append(thisserver)
            unit.main_conn.root.register_resource(name, start_port+port_offs)
            self.__class__.__bases__[0].port_offs += 1
            return
        
        if name in type(self).resource_list:
            dg.print('WARNING: Resource name {} already registered. Skipping...'.format(name))
            return
        if self.policy is not None:
            type(self).resource_list[name] = self
        else:
            dg.print('WARNING: Resource access policy for resource {} not specified. Skipping...'.format(name))
            return
        self.name = name

    @classmethod
    def get(cls, name):
        '''Return the resource instance registered under 'name'.'''
        try:
            if cls.resource_list[name]:
                return cls.resource_list[name]
            return None
        except Exception as e:
            raise ResourceRawError(str(e))

    @classmethod
    def get_all(cls):
        '''Return all available operational mode instances.'''
        return cls.resource_list

    @classmethod
    def get_all_names(cls):
        '''Return a list of names of all registered resources.'''
        names_list = []
        for item in cls.resource_list.keys():
            names_list.append(item)
        return names_list
