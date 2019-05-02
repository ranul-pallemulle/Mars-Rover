from abc import ABC, abstractmethod
from threading import Thread, RLock, Condition
from coreutils.diagnostics import Diagnostics as dg
import coreutils.resource_manager as mgr

class ActuatorError(Exception):
    '''Exception class that will be raised by classes implementing Actuator.'''
    pass

class Actuator(ABC):
    '''Actuates motors on a separate thread.'''

    def __init__(self):
        ''' Make empty list of motor objects.'''
        self.motor_list = dict()
        self.condition = Condition()
        self.release_was_called = False
        self.list_lock = RLock()
    
    def begin_actuate(self):
        '''Run update_motors in a new thread, if the motor_list is not empty.'''
        if self.release_was_called:
            self.release_was_called = False
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
            with self.list_lock:
                motor_set = mgr.global_resources.get_unique(self,motor_type)
                if motor_set is not None:
                    self.motor_list[motor_type] = motor_set
                else:
                    dg.print("{}: warning (acquire_motors): could not get unique access to {}".format(self.__class__.__name__,motor_type))
        except mgr.ResourceError as e:
            dg.print(str(e))
            raise ActuatorError('{}: Could not get access to motors.'.format(self.__class__.__name__))

        
    def update_motors(self):
        '''Send values received to motors. Assumes that all acquisitions
        (calls to acquire_motors()) have been done. Checking of each
        list member for modification is not done due to speed
        considerations. Therefore make sure to acquire all motors
        needed before calling begin_actuate and do not acquire or
        reacquire anything after the call.'''
        with self.list_lock:
            if len(self.motor_list) == 0:
                return

        while True:
            with self.condition:
                self.condition.wait() # block until values
                                      # available or
                                      # release_motors is called
                if self.release_was_called:
                    self.release_was_called = False
                    return
            with self.list_lock: # prevent release_motors from
                            # modifying the list until values
                            # (already received) are updated.
                for motor_set in self.motor_list.keys():
                    values = self.get_values(motor_set)
                    if values is not None:
                        self.motor_list[motor_set].set_values(values)


    def release_motors(self, motor_set):
        '''Remove unique access to a set of motors so that they may be used
elsewhere.'''
        with self.list_lock:
            if motor_set in self.motor_list:
                self.motor_list.pop(motor_set)
                mgr.global_resources.release(self,motor_set)
                with self.condition:
                    self.release_was_called = True
                    self.condition.notify()
            else:
                dg.print("Warning (actuator): release_motors called on resource not acquired.")

                
    def have_acquired(self, motor_set):
        '''Check if actuator has acquired the specified motors. Useful for use
        by classes inheriting from actuator as they don't need to know
        about the motor_list or locking.'''
        with self.list_lock:
            if motor_set in self.motor_list:
                return True
            else:
                return False

    def actuator_manual_set_released(self, motor_set):
        '''Remove a motor set from motor_list without releasing to resource 
        manager. This is used purely for remote resources which may disconnect
        unexpectedly and hence they cannot be released to the resource manager
        as they no longer exist. This exists purely to make have_acquired return
        false.
        '''
        with self.list_lock:
            if motor_set in self.motor_list:
                self.motor_list.pop(motor_set)
    
