from abc import ABCMeta, abstractmethod
from threading import Thread, Lock

list_lock = Lock()

class ActuatorError(Exception):
    '''Exception class that will be raised by classes implementing Actuator.'''
    pass

class Actuator:
    '''Actuates motors on a separate thread.'''
    __metaclass__ = ABCMeta

    def __init__(self, resource_manager):
        ''' Make empty list of motor objects.'''
        self.motor_list = dict()
        self.mgr = resource_manager
    
    def begin_actuate(self):
        '''Run update_motors in a new thread, if the motor_list is not empty.'''
        thread = Thread(target=self.update_motors, args=())
        thread.start()

    @abstractmethod
    def get_values(self, motor_set):
        '''Implementation will define some values to update the motors with.
    The number of values returned is implementation specific.'''
        pass

    def acquire_motors(self, motor_type):
        '''Get unique access to a set of motors such as wheel motors or
        robotic arm motors.'''
        try:
            with list_lock:
                self.motor_list[motor_type] = self.mgr.get_unique(motor_type)
        except ResourceError as e:
            print(str(e))
            raise ActuatorError('Could not get access to motors.')
    def update_motors(self):
        ''' Send values received to motors. '''
        num_motors = 0
        with list_lock:
            num_motors = len(self.motor_list)
        if num_motors == 0:
            return
        elif num_motors == 1: # speed up most common case
            motor_set = None
            with list_lock:
                motor_set = list(self.motor_list.values())[0]
            while num_motors > 0:
                print(num_motors)
                values = self.get_values(motor_set)
                motor_set.set_values(values)
                with list_lock:
                    num_motors = len(self.motor_list)
            return
        else:
            while self.motor_list:
                for motor_set in self.motor_list.values():
                    values = self.get_values(motor_set)
                    motor_set.set_values(values)

    def release_motors(self, motor_set):
        '''Remove unique access to a set of motors so that they may be used
elsewhere.'''
        num_motors = 0
        motors = None
        with list_lock:
            if motor_set in self.motor_list:
                motors = self.motor_list.pop(motor_set)
        if motors is not None:
            self.mgr.release(motor_set)
        else:
            print("Warning (actuator): release_motors called on resource not acquired.")
        return

    def have_acquired(self, motor_set):
        '''Check if actuator has acquired the specified motors. Useful for use
        by classes inheriting from actuator as they don't need to know
        about the motor_list or locking.'''
        with list_lock:
            if motor_set in self.motor_list:
                return True
            else:
                return False
    
