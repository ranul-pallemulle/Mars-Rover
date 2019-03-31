from interfaces.receiver import Receiver, ReceiverError
from interfaces.actuator import Actuator, ActuatorError
from interfaces.opmode import OpMode, OpModeError
import coreutils.resource_manager as mgr

class Joystick(Receiver, Actuator, OpMode):
    '''Operational mode for receving driving instructions from a remote joystick controller. These are used to move the rover.'''

    def __init__(self):
        Receiver.__init__(self)
        Actuator.__init__(self)
        OpMode.__init__(self)

        self.register_name("Joystick") # make this mode available
        # globally
        
        self.xval = 0           # joystick value for direction
        self.yval = 0           # joystick value for average speed.
        
    def store_received(self, recvd_list):
        '''Store values received from remote, after checking that they are of the right format (a joystick x value and a joystick y value representing angular speed and average speed respectively). Once the values are checked, send them to the motors using the Actuator notification system. Return a reply in the form of a string to be sent back. If the values are invalid, return None.'''
        if len(recvd_list) != 2:
            return None
        try:
            x = int(recvd_list[0])
            y = int(recvd_list[1])
        except (ValueError, IndexError) as e:
            print(str(e))
            return None
        else:
            # all values must be in the right range
            if x<=100 and x>=-100 and y<=100 and y>=-100:
                with self.condition: # acquire lock
                    self.xval = x
                    self.yval = y
                    self.condition.notify() # tell actuation thread
                                            # that values are ready
                return 'ACK'
            else:
                return 'ERR:RANGE' # values in wrong range.

    def get_values(self, motor_set):
        '''Overriden from actuator. motor_set specifies the type of motors
(wheel, arm, etc) and is used only if we have multiple types of motors
being controlled simultaneously. In this case, there's only the wheel
motors so we don't need to query motor_set.'''
        with self.condition:    # acquire lock
            return (self.xval, self.yval)

    def start(self, args):
        '''Implementation of OpMode abstract method start(args). Starts the Joystick mode.'''
        try:
            port = args[0]            
            self.connect(port)  # wait for connection
            self.begin_receive() # start receiving values
        except (IndexError, TypeError):
            raise OpModeError("Need a valid port number.")
        except ReceiverError as e:
            raise OpModeError(str(e))
        try:
            self.acquire_motors(mgr.Motors.WHEELS)
        except ActuatorError as e:
            self.stop(None)         # clean up
            raise OpModeError(str(e))
        if self.have_acquired(mgr.Motors.WHEELS):
            self.begin_actuate()    # start sending received values to motors
        else:
            self.stop(None)
            raise OpModeError
        
    def stop(self, args):
        '''Implementation of the OpMode abstract method stop(args). Stops the Joystick mode.'''
        if self.have_acquired(mgr.Motors.WHEELS):
            self.release_motors(mgr.Motors.WHEELS)
        if self.connection_active():
            try:
                self.disconnect()
            except ReceiverError as e:
                raise OpModeError(str(e))

    def submode_command(self, args):
        '''Implementation of OpMode abstract method submode_command(args). Takes mode-specific commands.'''
        print('Joystick mode does not take submode commands.')

    def run_on_connection_interrupted(self):
        '''Overriden from Receiver. Runs if an active connection to remote is interrupted.'''
        if self.is_running():
            self.stop(None)

