import sys
import gc
from enum import Enum
import resources.resource as rsc
import coreutils.configure as cfg
from coreutils.diagnostics import Diagnostics as dg
from interfaces.opmode import OpMode
from autonomous.auto_mode import Goal
# from autonomous.cv_engine import CVEngine

class Status(Enum):
    FREE = 0
    ACQUIRED = 1

class ResourceError(Exception):
    '''Exception class for ResourceManager class.'''
    pass

class ResourceManager:
    def __init__(self):
        self.resources_status = dict() # acquisition statuses of resources
        self.acquisition_list = dict() # key: resource name, value: name of 
                                       # opmode using it
        
    def initialise(self):
        '''Load all available local resources.'''
        if not cfg.Configuration.ready():
            raise ResourceError("Settings file not parsed.")
        try:
            rsc.Resource.resources_initialise()
        except rsc.ResourceRawError as e:
            raise ResourceError(str(e))
        resource_names = rsc.Resource.get_local_names()
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

                
    def load_remote_resource(self, name):
        '''Load resource located on an attached unit.'''
        resource_names = rsc.Resource.get_remote_names()
        if name in resource_names:
            dg.print("Found remote resource "+name)
            resource = rsc.Resource.get(name)
            if str(resource.policy) == str(rsc.Policy.UNIQUE):
                # resource.policy = rsc.Policy.UNIQUE # makes this a netref :/
                self.resources_status[name] = Status.FREE
            elif str(resource.policy) == str(rsc.Policy.SHARED):
                #resource.policy = rsc.Policy.SHARED
                self.resources_status[name] = 0
            return True
        return False

    def remove_resource(self, name):
        '''Remote unit disconnected - remove any of its resources from the main
         unit.'''
        if name in self.resources_status.keys():
            self.resources_status.pop(name)
            if name in self.acquisition_list.keys():
                obj = self.acquisition_list.pop(name)
                dg.print("Stopping opmodes using lost resource '"+name+"'...")
                if isinstance(obj, list):
                    for name in obj:
                        acq_opmode = OpMode.opmodes_list[name]
                        acq_opmode.on_resources_unexp_lost()
                else:
                    acq_opmode = OpMode.opmodes_list[obj]
                    acq_opmode.on_resources_unexp_lost()
            

    def get_unique(self, acq_obj, typename):
        '''Provide unique access to a resource. Return None if already
acquired. acq_obj == acquiring object - i.e the object acquiring the resource.
Pass self as this argument.'''
        acq_name = next((key for key, value in OpMode.opmodes_list.items() if value == acq_obj), "_NOTFOUND")
        if acq_name == '_NOTFOUND':
            acq_name = next((key for key, value in Goal.goals_list.items() if value == acq_obj), "_NOTFOUND")
        if acq_name == '_NOTFOUND':
            # if acq_obj.__class__ in CVEngine.__subclasses__():
            #     acq_name = 'CVEngine'
            acq_name = acq_obj.__class__.__name__
        if acq_name == '_NOTFOUND':
            raise ResourceError('Could not locate acquirer for resource {}'.format(typename))
        if typename in self.resources_status.keys():
            # dg.print("Refcount for {}:
            # {}".format(typename,sys.getrefcount(rsc.Resource.get(typename))))
            resource = rsc.Resource.get(typename)
            if str(resource.policy) == str(rsc.Policy.UNIQUE):
                if self.resources_status[typename] == Status.FREE:
                    self.resources_status[typename] = Status.ACQUIRED
                    self.acquisition_list[typename] = acq_name
                    dg.print("Resource Manager: {} was acquired by {}".
                             format(typename, acq_name))
                    return resource
                else:
                    return None
            else:
                raise ResourceError('Resource "{}" does not have a unique\
 access policy.'.format(typename))
        else:
            raise ResourceError('Resource "{}" requested but not found'.
                                format(typename))

    def get_shared(self, acq_obj, typename):
        '''Provide shared access to a resource.'''
        # print("TRYING TO GET {} FROM {}".format(typename, acq_obj))
        acq_name = next((key for key, value in OpMode.opmodes_list.items() if value == acq_obj), "_NOTFOUND")
        if acq_name == '_NOTFOUND':
            acq_name = next((key for key, value in Goal.goals_list.items() if value == acq_obj), "_NOTFOUND")
        if acq_name == '_NOTFOUND':
            # if acq_obj.__class__ in CVEngine.__subclasses__():
            #     acq_name = 'CVEngine'
            acq_name = acq_obj.__class__.__name__
        if acq_name == '_NOTFOUND':
            raise ResourceError('Could not locate acquirer "{}" for resource {}'.format(acq_obj,typename))
        if typename in self.resources_status.keys():
            # dg.print("Refcount for {}:
            # {}".format(typename,sys.getrefcount(resource)))
            resource = rsc.Resource.get(typename)
            if str(resource.policy) == str(rsc.Policy.SHARED):
                count = self.resources_status[typename]
                self.resources_status[typename] = count + 1
                # print("Got here")
                # print("HELLO: {}".format(self.acquisition_list[typename]))
                # if not self.acquisition_list[typename]:
                if not typename in self.acquisition_list.keys():
                    self.acquisition_list[typename] = []

                self.acquisition_list[typename].append(acq_name)
                if self.resources_status[typename] == 1:
                    if resource.shared_init:
                        dg.print("Shared resource {} initialising...".format(typename))
                        try:
                            resource.shared_init()
                        except Exception as e:
                            self.resources_status[typename] = 0
                            raise ResourceError("Error initialising shared resource: "+str(e))
                        dg.print("Shared resource {} initialised".format(typename))
                dg.print("Resource Manager: {} was acquired".format(typename))
                return resource
            else:
                raise ResourceError('Resource "{}" does not have a shared\
 access policy.'.format(typename))
        else:
            raise ResourceError('Resource "{}" requested but not found'.
                                format(typename))

    def release(self, acq_obj, typename):
        '''Release ownership of a resource.'''
        acq_name = next((key for key, value in OpMode.opmodes_list.items() if value == acq_obj), "_NOTFOUND")
        if acq_name == '_NOTFOUND':
            acq_name = next((key for key, value in Goal.goals_list.items() if value == acq_obj), "_NOTFOUND")
        if acq_name == '_NOTFOUND':
            # if acq_obj.__class__ in CVEngine.__subclasses__():
            #     acq_name = 'CVEngine'
            acq_name = acq_obj.__class__.__name__
        if acq_name == '_NOTFOUND':
            raise ResourceError('Could not locate releaser "{}" for resource {}'.format(acq_obj,typename))
        if typename in self.resources_status.keys():
            resource = rsc.Resource.get(typename)
            # dg.print("Refcount for {}:
            # {}".format(typename,sys.getrefcount(rsc.Resource.get(typename))))
            # dg.print("refererrers:
            # {}".format(gc.get_referrers(rsc.Resource.get(typename))))
            if str(resource.policy) == str(rsc.Policy.UNIQUE):
                if self.resources_status[typename] == Status.ACQUIRED:
                    self.resources_status[typename] = Status.FREE
                    self.acquisition_list.pop(typename)
                    dg.print("Resource Manager: {} was released by {}.".
                             format(typename, acq_name))
                else:
                    raise ResourceError('Cannot release {}: resource was\
 already free'.format(typename))
            elif str(resource.policy) == str(rsc.Policy.SHARED):
                count = self.resources_status[typename]
                self.resources_status[typename] = count - 1
                self.acquisition_list[typename].remove(acq_name)
                dg.print("Resource Manager: {} was released by {}.".
                        format(typename, acq_name))
                if self.resources_status[typename] < 0:
                    raise ResourceError('Shared resource count for {} is less than 0.'.format(typename))
                if self.resources_status[typename] == 0:
                    if resource.shared_deinit:
                        dg.print("Shared resource {} deinitialising...".format(typename))
                        try:                        
                            resource.shared_deinit()
                        except Exception as e:
                            raise ResourceError('Error deinitialising shared resource: '+str(e))
                        dg.print("Shared resource {} deinitialised".format(typename))
        else:
            raise ResourceError('Resource "{}" not found'.format(typename))
                        

global_resources = ResourceManager()
