from abc import ABCMeta, abstractmethod
from threading import Thread, Lock, Condition
import coreutils.resource_manager as mgr

list_lock = Lock()

class ActuatorError(Exception):
    '''Exception class that will be raised by classes implementing Actuator.'''
    pass

class Actuator:
    '''Actuates motors on a separate thread.'''
    __metaclass__ = ABCMeta

    def __init__(self):
        ''' Make empty list of motor objects.'''
        self.motor_list = dict()
        self.condition = Condition()
        self.release_was_called = False
    
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
                motor_set = mgr.global_resources.get_unique(motor_type)
                if motor_set is not None:
                    self.motor_list[motor_type] = motor_set
                else:
                    print("Warning (acquire_motors): could not get unique access to {}".format(motor_type))
        except ResourceError as e:
            print(str(e))
            raise ActuatorError('Could not get access to motors.')

        
    def update_motors(self):
        '''Send values received to motors. Assumes that all acquisitions
        (calls to acquire_motors()) have been done. Checking of each
        list member for modification is not done due to speed
        considerations. Therefore make sure to acquire all motors
        needed before calling begin_actuate and do not acquire or
        reacquire anything after the call. If any motor in the list is
        found to have been released, it is assumed that actuation
        cannot function as normal anymore and all the other motors
        will be released as well.

        '''
        with list_lock:
            if len(self.motor_list) == 0:
                return

        while True:
            with self.condition:
                self.condition.wait() # block until values
                                      # available or
                                      # release_motors is called

                if self.release_was_called: # release everything
                    with list_lock:
                        for motor_set in self.motor_list.keys():
                            self.release_motors(motor_set)
                    self.release_was_called = False
                    return

            with list_lock: # prevent release_motors from
                            # modifying the list until values
                            # (already received) are updated.
                for motor_set in self.motor_list.keys():
                    values = self.get_values(motor_set)
                    self.motor_list[motor_set].set_values(values)


    def release_motors(self, motor_set):
        '''Remove unique access to a set of motors so that they may be used
elsewhere.'''
        with list_lock:
            if motor_set in self.motor_list:
                self.motor_list.pop(motor_set)
                mgr.global_resources.release(motor_set)
                with self.condition:
                    self.release_was_called = True
                    self.condition.notify()
            else:
                print("Warning (actuator): release_motors called on resource not acquired.")

                
    def have_acquired(self, motor_set):
        '''Check if actuator has acquired the specified motors. Useful for use
        by classes inheriting from actuator as they don't need to know
        about the motor_list or locking.'''
        with list_lock:
            if motor_set in self.motor_list:
                return True
            else:
                return False
    
