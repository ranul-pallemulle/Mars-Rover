import sys
import gc
from enum import Enum
import resources.resource as rsc
import coreutils.configure as cfg
from coreutils.diagnostics import Diagnostics as dg

class Status(Enum):
    FREE = 0
    ACQUIRED = 1

class ResourceError(Exception):
    '''Exception class for ResourceManager class.'''
    pass

class ResourceManager:
    def __init__(self):
        self.resources_status = dict()
        
    def initialise(self):
        '''Load all available resources.'''
        if not cfg.Configuration.ready():
            raise ResourceError("Settings file not parsed.")
        try:
            rsc.Resource.resources_initialise()
        except rsc.ResourceRawError as e:
            raise ResourceError(str(e))
        resource_names = rsc.Resource.get_all_names()
        if resource_names:
            dg.print("Found resources: ")
        for name in resource_names:
            dg.print('  '+name)
        for name in resource_names:
            policy = rsc.Resource.get(name).policy
            if policy == rsc.Policy.UNIQUE:
                self.resources_status[name] = Status.FREE # initially free
            elif policy == rsc.Policy.SHARED:
                self.resources_status[name] = 0 # use count
            

    def get_unique(self, typename):
        '''Provide unique access to a resource. Return None if already acquired.'''
        if typename in self.resources_status.keys():
            # print("Refcount for {}: {}".format(typename,sys.getrefcount(rsc.Resource.get(typename))))            
            resource = rsc.Resource.get(typename)
            if resource.policy == rsc.Policy.UNIQUE:
                if self.resources_status[typename] == Status.FREE:
                    self.resources_status[typename] = Status.ACQUIRED
                    dg.print("Resource Manager: {} was acquired".format(typename))
                    return resource
                else:
                    return None
            else:
                raise ResourceError('Resource "{}" does not have a unique access policy.'.format(typename))
        else:
            raise ResourceError('Resource "{}" requested but not found'.format(typename))

    def get_shared(self, typename):
        '''Provide shared access to a resource.'''
        if typename in self.resources_status.keys():
            # print("Refcount for {}: {}".format(typename,sys.getrefcount(resource)))            
            resource = rsc.Resource.get(typename)
            if resource.policy == rsc.Policy.SHARED:
                count = self.resources_status[typename]
                self.resources_status[typename] = count + 1
                if self.resources_status[typename] == 1:
                    if resource.shared_init:
                        dg.print("Shared resource {} initialising...".format(typename))
                        resource.shared_init()
                        dg.print("Shared resource {} initialised".format(typename))
                dg.print("Resource Manager: {} was acquired".format(typename))
                return resource
            else:
                raise ResourceError('Resource "{}" does not have a shared access policy.'.format(typename))
        else:
            raise ResourceError('Resource "{}" requested but not found'.format(typename))

    def get_camera_use_count(self):
        return self.resources[Camera.FEED]

    def release(self, typename):
        '''Release ownership of a resource.'''
        if typename in self.resources_status.keys():
            resource = rsc.Resource.get(typename)
            # print("Refcount for {}: {}".format(typename,sys.getrefcount(rsc.Resource.get(typename))))
            # print("refererrers: {}".format(gc.get_referrers(rsc.Resource.get(typename))))            
            if resource.policy == rsc.Policy.UNIQUE:
                if self.resources_status[typename] == Status.ACQUIRED:
                    self.resources_status[typename] = Status.FREE
                    dg.print("Resource Manager: {} was released.".format(typename))
                else:
                    raise ResourceError('Cannot release {}: resource was already free'.format(typename))
            elif resource.policy == rsc.Policy.SHARED:
                count = self.resources_status[typename]
                self.resources_status[typename] = count - 1
                dg.print("Resource Manager: {} was released.".format(typename))                
                if self.resources_status[typename] < 0:
                    raise ResourceError('Shared resource count for {} is less than 0.'.format(typename))
                if self.resources_status[typename] == 0:
                    if resource.shared_deinit:
                        dg.print("Shared resource {} deinitialising...".format(typename))                        
                        resource.shared_deinit()
                        dg.print("Shared resource {} deinitialised".format(typename))
        else:
            raise ResourceError('Resource "{}" not found'.format(typename))
                        

global_resources = ResourceManager()
