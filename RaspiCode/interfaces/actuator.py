from abc import ABCMeta, abstractmethod
from threading import Thread, Lock

class ActuatorError(Exception):
    '''Exception class that will be raised by classes implementing Actuator.'''
    pass

class Actuator:
    '''Actuates motors on a separate thread.'''
    __metaclass__ = ABCMeta

    def __init__(self):
        ''' Make empty list of motor objects.'''
        self.motor_list = []
    
    def start_motors(self):
        '''Run update_motors in a new thread, if the motor_list is not empty.'''
        thread = Thread(target=self.update_motors, args=())
        thread.start()

    @abstractmethod
    def get_values(self, motor_set):
        pass

    def acquire_motors(self, motor_type):
        '''Get unique access to a set of motors such as wheel motors or
robotic arm motors.'''
        try:
            self.motor_list.append(motor_type.get_unique())
        except ResourceError as e:
            print(str(e))
            raise ActuatorError('Could not get access to motors.')
    def update_motors(self):
        ''' Send values received to motors. '''
        while True:
            for motor_set in self.motor_list:
                values = self.get_values(motor_set)
                motor_set.set_values(values)

    def release_motors(self, motor_set):
        '''Remove unique access to a set of motors so that they may be used
elsewhere.'''
        if self.motor_list:
            try:
                idx = self.motor_list.index(motor_set)
            except IndexError as e:
                print(str(e))
                raise ActuatorError("Can't release motors not acquired.")
            motors = self.motor_list.pop(idx)
            motors.release()
            
