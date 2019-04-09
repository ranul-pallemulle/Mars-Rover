from enum import Enum
import importlib
import os
import coreutils.configure as cfg

class Policy(Enum):
    UNIQUE = 0
    SHARED = 1

class ResourceRawError(Exception):
    '''Exception class raised by Resource.'''
    pass

class Resource:
    '''Base class for all resources. All resources (like motors, camera,
etc) should inherit from this class and register themselves to be
available to the resource manager and (hence) to the rest of the program.
    '''
    resource_list = dict()      # resource instances stored under their registered names.

    @classmethod
    def resources_initialise(cls):
        '''Look for derived clases in directories specified in the settings
file. Initialise them to register them and add to resource_list.'''
        try:
            dir_list = cfg.overall_config.resources_directories()
        except cfg.ConfigurationError as e:
            raise ResourceRawError(str(e))
        if not dir_list:
            print("WARNING: no resource directories specified.")
        for folder in dir_list:
            if not folder:
                print("WARNING: no resource modules found.")
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

    def register_name(self, name):
        '''Store resource instance in the resource_list. The key is the
provided name. The policy refers to whether access to it should be
unique or shared. See resource manager for more information on
policy. 
        '''
        if name in type(self).resource_list:
            print('WARNING: Resource name {} already registered. Skipping...'.format(name))
            return
        if self.policy is not None:
            type(self).resource_list[name] = self
        else:
            print('WARNING: Resource access policy for resource {} not specified. Skipping...'.format(name))
            return

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
