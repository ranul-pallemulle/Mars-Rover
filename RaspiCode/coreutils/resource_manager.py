from enum import Enum
from resources import camera
from resources.motors_interface import MotorInterface, MotorInterfaceError

class Motors(Enum):
    '''Typenames to be used for resource_manager functions.'''
    WHEELS = 1
    ARM = 2
class Camera(Enum):
    FEED = 1

class ResourceError(Exception):
    '''Exception class for ResourceManager class.'''
    pass

class ResourceManager:
    FREE = 0
    ACQUIRED = 1
    def __init__(self):
        self.wheels = None
        self.arm = None
        self.camera = None
        self.resources = {
            Motors.WHEELS : self.FREE,
            Motors.ARM    : self.FREE,
            Camera.FEED   : 0} # use count
        
    def initialise(self):
        try:
            MI = MotorInterface()
            self.wheels = MI.WheelMotors()
            self.arm = MI.ArmMotors()
            self.camera = camera.Camera()
        except MotorInterfaceError as e:
            raise ResourceError(str(e))

    def get_unique(self, typename):
        '''Provide unique access to a resource.'''
        if typename == Motors.WHEELS or typename == Motors.ARM:
            if self.resources[typename] == self.FREE:
                self.resources[typename] = self.ACQUIRED
                print("Resource Manager: {} was acquired".format(typename))
                return self._provide_resource(typename)
            else:
                return None
        else:
            raise ResourceError('No such resource or unable to provide unique access to it.')

    def get_shared(self, typename):
        '''Provide shared access to a resource.'''
        if typename == Camera.FEED:
            count = self.resources[typename]
            self.resources[typename] = count + 1
            return self._provide_resource(typename)
        else:
            raise ResourceError('No such resource or unable to provide unique access to it.')

    def _provide_resource(self, typename):
        '''Return object corresponding to resource. This is a private method.'''
        if typename == Motors.WHEELS:
            return self.wheels
        elif typename == Motors.ARM:
            return self.arm
        elif typename == Camera.FEED:
            return self.camera

    def release(self, typename):
        '''Deallocate a resource.'''
        if typename == Motors.WHEELS or typename == Motors.ARM:
            if self.resources[typename] == self.FREE:
                raise ResourceError('Cannot release resource: resource was already free.')
            elif self.resources[typename] == self.ACQUIRED:
                self.resources[typename] = self.FREE
                print("Resource Manager: {} was released".format(typename))
        elif typename == Camera.FEED:
            count = self.resources[typename]
            self.resources[typename] = count - 1
        else:
            raise ResourceError('release called on unknown resource.')

global_resources = ResourceManager()
