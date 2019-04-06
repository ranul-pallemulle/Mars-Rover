from enum import Enum
# from resources import camera
# from resources.motors_interface import MotorInterface, MotorInterfaceError
import resources.resource as rsc
import coreutils.configure as cfg

# class Motors(Enum):
#     '''Typenames to be used for resource_manager functions.'''
#     WHEELS = 1
#     ARM = 2
# class Camera(Enum):
#     FEED = 1

class Status(Enum):
    FREE = 0
    ACQUIRED = 1

class ResourceError(Exception):
    '''Exception class for ResourceManager class.'''
    pass


class ResourceManager:
    # FREE = 0
    # ACQUIRED = 1
    def __init__(self):
        # self.wheels = None
        # self.arm = None
        # self.camera = None
        # self.resources_status = {
        #     Motors.WHEELS : self.FREE,
        #     Motors.ARM    : self.FREE,
        #     Camera.FEED   : 0} # use count
        self.resources_status = dict()
        
    def initialise(self):
        if not cfg.Configuration.ready():
            raise ResourceError("Settings file not parsed.")
        # try:
        #     MI = MotorInterface()
        #     self.wheels = MI.WheelMotors()
        #     self.arm = MI.ArmMotors()
        #     self.camera = camera.Camera()
        # except MotorInterfaceError as e:
        #     raise ResourceError(str(e))
        try:
            rsc.Resource.resources_initialise()
        except rsc.ResourceRawError as e:
            raise ResourceError(str(e))
        resource_names = rsc.Resource.get_all_names()
        if resource_names:
            print("Found resources: ")
        for name in resource_names:
            print('  '+name)
        # if not resource_names:
        #     raise ResourceError('No resources found.')
        for name in resource_names:
            policy = rsc.Resource.get(name).policy
            if policy == rsc.Policy.UNIQUE:
                self.resources_status[name] = Status.FREE # initially free
            elif policy == rsc.Policy.SHARED:
                self.resources_status[name] = 0 # use count
            

    def get_unique(self, typename):
        '''Provide unique access to a resource.'''
        # if typename == Motors.WHEELS or typename == Motors.ARM:
        #     if self.resources_status[typename] == self.FREE:
        #         self.resources_status[typename] = self.ACQUIRED
        #         print("Resource Manager: {} was acquired".format(typename))
        #         return self._provide_resource(typename)
        #     else:
        #         return None
        # else:
        #     raise ResourceError('No such resource or unable to provide unique access to it.')
        if typename in self.resources_status.keys():
            resource = rsc.Resource.get(typename)
            if resource.policy == rsc.Policy.UNIQUE:
                if self.resources_status[typename] == Status.FREE:
                    self.resources_status[typename] = Status.ACQUIRED
                    return resource
                else:
                    return None
            else:
                raise ResourceError('Resource "{}" does not have a unique access policy.'.format(typename))
        else:
            raise ResourceError('Resource "{}" requested but not found'.format(typename))

    def get_shared(self, typename):
        '''Provide shared access to a resource.'''
        # if typename == Camera.FEED:
        #     count = self.resources_status[typename]
        #     self.resources_status[typename] = count + 1
        #     return self._provide_resource(typename)
        # else:
        #     raise ResourceError('No such resource or unable to provide unique access to it.')
        if typename in self.resources_status.keys():
            resource = rsc.Resource.get(typename)
            if resource.policy == rsc.Policy.SHARED:
                count = self.resources_status[typename]
                self.resources_status[typename] = count + 1
                if self.resources_status[typename] == 1:
                    if resource.shared_init:
                        resource.shared_init()
                return resource
            else:
                raise ResourceError('Resource "{}" does not have a shared access policy.'.format(typename))
        else:
            raise ResourceError('Resource "{}" requested but not found'.format(typename))

    # def _provide_resource(self, typename):
    #     '''Return object corresponding to resource. This is a private method.'''
    #     if typename == Motors.WHEELS:
    #         return self.wheels
    #     elif typename == Motors.ARM:
    #         return self.arm
    #     elif typename == Camera.FEED:
    #         return self.camera

    def release(self, typename):
        '''Deallocate a resource.'''
        # if typename == Motors.WHEELS or typename == Motors.ARM:
        #     if self.resources_status[typename] == self.FREE:
        #         raise ResourceError('Cannot release resource: resource was already free.')
        #     elif self.resources_status[typename] == self.ACQUIRED:
        #         self.resources_status[typename] = self.FREE
        #         print("Resource Manager: {} was released".format(typename))
        # elif typename == Camera.FEED:
        #     count = self.resources_status[typename]
        #     self.resources_status[typename] = count - 1
        # else:
        #     raise ResourceError('release called on unknown resource.')
        if typename in self.resources_status.keys():
            resource = rsc.Resource.get(typename)
            if resource.policy == rsc.Policy.UNIQUE:
                if self.resources_status[typename] == Status.ACQUIRED:
                    self.resources_status[typename] = Status.FREE
                    print("Resource Manager: {} was released".format(typename))
                else:
                    raise ResourceError('Cannot release {}: resource was already free'.format(typename))
            elif resource.policy == rsc.Policy.SHARED:
                count = self.resources_status[typename]
                self.resources_status[typename] = count - 1
                if self.resources_status[typename] < 0:
                    raise ResourceError('Shared resource count for {} is less than 0.'.format(typename))
                if self.resources_status[typename] == 0:
                    if resource.shared_deinit:
                        resource.shared_deinit()
        else:
            raise ResourceError('Resource "{}" not found'.format(typename))
                        

global_resources = ResourceManager()
