from interfaces.receiver import Receiver, ReceiverError
from interfaces.actuator import Actuator, ActuatorError
from interfaces.opmode import OpMode, OpModeError
import coreutils.resource_manager as mgr

class RoboticArm(Receiver, Actuator, OpMode):
    '''Operational mode for receiving instructions from a remote robotic arm controller. These are used to control the robotic arm.'''

    def __init__(self):
        Receiver.__init__(self)
        Actuator.__init__(self)
        OpMode.__init__(self)

        self.register_name("RoboticArm") # make this mode available
                                         # globally
        
        self.angle_1 = 0        # base servo
        self.angle_2 = 0        # intermediate servo
        self.angle_3 = 0        # servo closest to gripper
        self.angle_grp = 0      # gripper

    def store_received(self, recvd_list):
        '''Store values received from remote, after checking that they are of the right format (4 angle values; three for the arm servos and 1 for the gripper). Once the values are checked, send them to the motors using the Actuator notification system. Return a reply in the form of a string to be sent back. If the values are invalid, return None.'''
        if len(recvd_list) != 4:
            return None
        try:
            thet_1 = int(recvd_list[0])
            thet_2 = int(recvd_list[1])
            thet_3 = int(recvd_list[2])
            gripval = int(recvd_list[3])
        except (ValueError, IndexError) as e:
            print(str(e))
            return None
        else:
            # all values must be in the right range
            if thet_1 <= 180 and thet_1 >= -180\
               and thet_2 <= 180 and thet_2 >= -180\
               and thet_3 <= 180 and thet_3 >= -180\
               and gripval <= 180 and gripval >= -180:
                with self.condition: # acquire lock
                    self.angle_1 = thet_1
                    self.angle_2 = thet_2
                    self.angle_3 = thet_3
                    self.angle_grp = gripval
                    self.condition.notify() # tell the actuator thread
                                            # that values are ready.
                return 'ACK'
            else:
                return 'ERR:RANGE' # values in wrong range

    def get_values(self, motor_set):
        '''Overridden from actuator. motor_set specifies the type of motors (wheel, arm, etc) and is used only if we have multiple types of motors being controlled simultaneously. In this case, there's only the arm motors so we don't need to query motor_set.'''
        with self.condition:    # acquire lock
            return (self.angle_1, self.angle_2, self.angle_3, self.angle_grp)

    def start(self, args):
        '''Implementation of OpMode abstract method start(args). Starts the RoboticArm mode.'''
        try:
            port = args[0]
            self.connect(port)  # wait for connection
            self.begin_receive() # start receiving values
        except (IndexError, TypeError):
            raise OpModeError("Need a valid port number.")
        except ReceiverError as e:
            raise OpModeError(str(e))
        try:
            self.acquire_motors(mgr.Motors.ARM)
        except ActuatorError as e:
            self.stop()         # clean up
            raise OpModeError(str(e))
        self.begin_actuate()    # start sending received values to motors
    
    def stop(self, args):
        '''Implementation of OpMode abstract method stop(args). Stops the RoboticArm mode.'''
        if self.have_acquired(mgr.Motors.ARM):
            self.release_motors(mgr.Motors.ARM)
        if self.connection_active():
            try:
                self.disconnect()
            except ReceiverError as e:
                raise OpModeError(str(e))

    def submode_command(self, args):
        '''Implementation of OpMode abstract method submode_command(args). Takes mode-specific commands.'''
        print('RoboticArm mode does not take submode commands.')

    def run_on_connection_interrupted(self):
        '''Overridden from Receiver. Runs if an active connection to remote is interrupted.'''
        if self.is_running():
            self.stop(None)

