from enum import Enum
from resources import motors
from resources import camera

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
        self.wheels = motors.WheelMotors()
        self.arm = motors.ArmMotors()
        self.camera = camera.Camera()
        self.resources = {'wheels':self.FREE, 'arm':self.FREE,
                          'camera':0}
        
    def get_unique(self, typename):
        '''Provide unique access to a resource.'''
        if typename == Motors.WHEELS:
            if self.resources['wheels'] == self.FREE:
                self.resources['wheels'] = self.ACQUIRED
                return self.wheels
            else:
                return None
        if typename == Motors.ARM:
            if self.resources['arm'] == self.FREE:
                self.resources['arm'] = self.ACQUIRED
                return self.arm
            else:
                return None
        else:
            raise ResourceError('No such resource or unable to provide unique access to it.')

    def get_shared(self, typename):
        '''Provide shared access to a resource.'''
        if typename == Camera.FEED:
            count = self.resources['camera']
            self.resources['camera'] = count + 1
            return self.camera
        else:
            raise ResourceError('No such resource or unable to provide unique access to it.')
        
