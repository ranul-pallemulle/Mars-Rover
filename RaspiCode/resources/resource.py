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

    # port number that a resource proxy object uses to communicate
    # with the main unit. As a resource is instantiated, it increments
    # the port offset so that each resource uses a different port.
    port_offs = 0
    
    # resource instances stored under their registered names. These
    # are the actual objects (not proxies). If this is not the main
    # unit, the resource instance is still stored here, while the main
    # unit's resource class contains the proxy object in
    # remote_resources_list.
    resource_list = dict()
    
    # dict of dict: resource instance proxy objects stored under their
    # registered names, all stored under the unit name. This exists so
    # that the main unit knows which unit each resource is local
    # to. This makes it possible to use the actual resource instance
    # instead of the proxy when the opmode using the resource is
    # running on the unit to which the resource is local.
    remote_resource_list = dict()

    # server instances, each associated with a proxy instance. These
    # need to be closed when unit disconnects from the main unit.
    servers = dict()

    # def on_connect(self, conn):
    #     # dg.print("Got connection on {}".format(self.__class__.__name__))
    #     pass

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
                    raise ResourceRawError('Error in resource files list. Check \
settings file. : \n'+str(e))
            else:               # is a folder; check inside
                try:
                    for filename in os.listdir(folder):
                        if str(filename).endswith('.py'):
                            importlib.import_module(folder+'.'+str(filename).
                                                    split('.')[0])
                except FileNotFoundError as e:
                    raise ResourceRawError('Error in resource directories list. \
Check settings file. : \n'+str(e))
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
            server = cls.servers.pop()
            server.close()

    def register_name(self, name):
        '''Store resource instance in the resource_list. The key is the
provided name. The policy refers to whether access to it should be
unique or shared. See resource manager for more information on
policy. If this unit is not the main unit (i.e an attached unit on the
network) then register this resource with the main unit.
        '''
        # Register locally
        if name in self.__class__.__bases__[0].resource_list:
            dg.print('WARNING: Resource name {} already registered. Skipping...'
                     .format(name))
            return
        if self.policy is not None:
            self.__class__.__bases__[0].resource_list[name] = self
            dg.print('ADDED RESOURCE {} to list'.format(name))
        else:
            dg.print('WARNING: Resource access policy for resource {} not \
specified. Skipping...'.format(name))
            return
        self.name = name

        # If this is a unit, register with main unit
        if cfg.overall_config.running_as_unit:
            start_port = 19200  # port numbers for use with resources.
            port_offs = self.__class__.__bases__[0].port_offs
            
            # every resource, when program is in unit mode, runs as a
            # server so that the main unit may use remote procedure
            # calls to emulate local function calls.
            thisserver = rpyc.utils.server.ThreadedServer(
                self, port=start_port+port_offs, protocol_config={
                'allow_public_attrs': True,
                'allow_pickle': True,
            })
            thread = Thread(target=thisserver.start, args=[])
            thread.start()
            # store this server in the Resource class (__bases__[0])
            self.__class__.__bases__[0].servers[name] = thisserver
            # Register with the main unit
            try:
                success = unit.main_conn.root.register_resource(name,start_port
                                                              +port_offs)
            except Exception as e: # exception is remote, currently no
                                   # way to catch custom exception
                dg.print(str(e))
                import sys
                sys.exit(1)
            if not success:     # resource name already taken on the main unit
                self.__class__.__bases__[0].resource_list.pop(name)
                self.__class__.__bases__[0].servers.pop(name)
                thisserver.close()
                dg.print("Unregistering resource "+name+" - name already taken \
globally.")
                return
                
            # next resource to register on this unit uses ++start_port
            self.__class__.__bases__[0].port_offs += 1


    @classmethod
    def register_remote_resource(cls, unitname, rscname, proxy_obj):
        '''Executed on the main unit, to register resources located on remote
units.'''
        if rscname in cls.resource_list:
            dg.print("WARNING: Resource name {} already registered. Skipping..."
                     .format(rscname))
            return False
        for registered_unit in cls.remote_resource_list:
            if rscname in cls.remote_resource_list[registered_unit]:
                dg.print("WARNING: Resource name {} already registered. Skipping..."
                         .format(rscname))
                return False
        if proxy_obj.policy is not None:
            if not unitname in cls.remote_resource_list.keys():
                cls.remote_resource_list[unitname] = dict()
            cls.remote_resource_list[unitname][rscname] = proxy_obj
            return True
        else:
            dg.print('WARNING: Resource access policy for resource {} not \
specified. Skipping...'.format(rscname))
            return False


    @classmethod
    def get(cls, name):
        '''Return the resource instance registered under 'name'.'''
        dg.print("GET CALLED ON UNIT {}".format(cfg.overall_config.get_unitname()))
        dg.print("cls name is {}".format(cls.__name__))
        dg.print("cls list is {}".format(cls.resource_list))
        dg.print("name to search for is {}".format(name))
        try:
            if name in cls.resource_list.keys():
                return cls.resource_list[name]
            dg.print("NAME '{}' NOT IN LOCAL LIST".format(name))
            for unit in cls.remote_resource_list:
                dg.print("SEARCH REMOTE LIST...")
                if name in cls.remote_resource_list[unit]:
                    return cls.remote_resource_list[unit][name]
            dg.print("NAME '{}' NOT IN REMOTE LIST".format(name))
            return None
        except Exception as e:
            raise ResourceRawError(str(e))

    @classmethod
    def get_local_names(cls):
        '''Return a list of names of all registered local resources.'''
        dg.print("GET_LOCAL_NAMES CALLED ON UNIT {}".format(cfg.overall_config.get_unitname()))
        names_list = []
        for name in cls.resource_list.keys():
            names_list.append(name)
        return names_list

    @classmethod
    def get_remote_names(cls):
        '''Return a list of names of all registered remote resources.'''
        names_list = []
        for unit in cls.remote_resource_list.keys():
            for name in cls.remote_resource_list[unit].keys():
                names_list.append(name)
        return names_list
