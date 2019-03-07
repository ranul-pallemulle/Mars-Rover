# Responsible for controlling the state of various individual parts.
# Provides an interface for the main execution to control specific features
from interfaces.receiver import ReceiverError
from joystick.joystick import Joystick
from robotic_arm.arm import RoboticArm
from coreutils.parser import CommandTypes
import coreutils.resource_manager as mgr

class LauncherError(Exception):
    '''Exception class that will be raised by launch functions.'''
    pass

'''Global objects'''
jstick_obj = None
arm_obj = None

def release_all():
    '''Close all resources so that shutdown can be done.'''
    if (jstick_obj is not None) and jstick_obj.is_running():
        try:
            kill_joystick([CommandTypes.STOP_JOYSTICK])
        except LauncherError as e:
            pass
    if (arm_obj is not None) and arm_obj.is_running():
        try:
            kill_arm([CommandTypes.STOP_ARM])
        except LauncherError as e:
            pass
    # try:
    #     kill_camera([])
    # except LauncherError as e:
    #     pass
    # try:
    #     kill_auto([])
    # except LauncherError as e:
    #     pass

def launch_joystick(arg_list):
    '''Start joystick operation if it is not running.'''
    if len(arg_list) < 2:
        raise LauncherError('Wrong number of arguments to start Joystick:\
        need "START_JOYSTICK <port>"')
    if arg_list[0] != CommandTypes.START_JOYSTICK:
        raise LauncherError('Incorrect command received for starting joystick:\
        need "START_JOYSTICK <port>"')
    port = arg_list[1]
    try:
        port = int(port)
    except ValueError:
        raise LauncherError('Failed to start Joystick: specified port value\
        must be an integer')
    global jstick_obj
    if jstick_obj is None:
        try:
            jstick_obj = Joystick()
        except ReceiverError as e:
            jstick_obj = None
            raise LauncherError('Failed to create Joystick object: '+str(e))

    try:
        jstick_obj.connect(port)
        jstick_obj.start()
    except ReceiverError as e:
        raise LauncherError('Failed to start Joystick: '+str(e))

def kill_joystick(arg_list):
    '''Stop joystick operation if it is running.'''
    if len(arg_list) == 0:
        raise LauncherError('Empty command received, cannot process.')
    if arg_list[0] != CommandTypes.STOP_JOYSTICK:
        raise LauncherError('Incorrect command received for stopping Joystick')
    global jstick_obj
    if jstick_obj is not None:
        if not jstick_obj.is_running():
            raise LauncherError('Joystick mode already stopped.')
        try:
            jstick_obj.stop()
        except ReceiverError as e:
            raise LauncherError(str(e))
    else:
        raise LauncherError('Joystick object not initialised')

def launch_arm(arg_list):
    '''Start robotic arm operation if it is not running.'''
    if len(arg_list) < 2:
        raise LauncherError('Wrong number of arguments to start RoboticArm:\
        try "START_ARM <port>"')
    if arg_list[0] != CommandTypes.START_ARM:
        raise LauncherError('Incorrect command received for starting RoboticArm:\
        need "START_ARM <port>"')
    port = arg_list[1]
    try:
        port = int(port)
    except ValueError:
        raise LauncherError('Failed to start RoboticArm: specified port value\
        must be an integer')    
    global arm_obj
    if arm_obj is None:
        try:
            arm_obj = RoboticArm()
        except ReceiverError as e:
            arm_obj = None
            raise LauncherError('Failed to create RoboticArm object: '+str(e))

    try:
        arm_obj.connect(port)
        arm_obj.start()
    except ReceiverError as e:
        raise LauncherError('Failed to start Robotic Arm '+str(e))

def kill_arm(arg_list):
    if len(arg_list) == 0:
        raise LauncherError('Empty command received, cannot process.')
    if arg_list[0] != CommandTypes.STOP_ARM:
        raise LauncherError('Incorrect command received for stopping RoboticArm')
    global arm_obj
    if arm_obj is not None:
        if not arm_obj.is_running():
            raise LauncherError('RoboticArm mode already stopped.')
        try:
            arm_obj.stop()
        except ReceiverError as e:
            raise LauncherError(str(e))
    else:
        raise LauncherError('RoboticArm object not initialised')

def launch_camera(arg_list):
    pass

def kill_camera(arg_list):
    pass

def launch_auto(arg_list):
    pass

def kill_auto(arg_list):
    pass
