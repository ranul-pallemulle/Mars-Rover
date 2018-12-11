# Responsible for controlling the state of various individual parts.
# Provides an interface for the main execution to control specific features
from interfaces.receiver import ReceiverError
from joystick.joystick import Joystick
from robotic_arm.arm import RoboticArm

class LauncherError(Exception):
    '''Exception class that will be raised by launch functions.'''
    pass

'''Global objects'''
jstick_obj = None
arm_obj = None

def release_all():
    '''Close all resources so that shutdown can be done.'''
    try:
        kill_joystick([])
        kill_arm([])
        kill_camera([])
        kill_auto([])
    except LauncherError:
        pass

def launch_joystick(arg_list):
    '''Start joystick operation if it is not running.'''
    global jstick_obj
    if jstick_obj is None:
        try:
            jstick_obj = Joystick()
        except ReceiverError as e:
            jstick_obj = None
            raise LauncherError('Failed to create Joystick object: '+str(e))
    port = arg_list[1]      # need to check len(arg_list)
    try:
        jstick_obj.connect(port)
        jstick_obj.begin()
    except ReceiverError as e:
        raise LauncherError('Failed to start Joystick: '+str(e))

def kill_joystick(arg_list):
    '''Stop joystick operation if it is running.'''
    global jstick_obj
    if jstick_obj is not None:
        try:
            jstick_obj.disconnect()
        except ReceiverError as e:
            raise LauncherError(str(e))
    else:
        raise LauncherError('Joystick object not initialised')

def launch_arm(arg_list):
    '''Start robotic arm operation if it is not running.'''
    global arm_obj
    if arm_obj is None:
        try:
            arm_obj = RoboticArm()
        except ReceiverError as e:
            arm_obj = None
            raise LauncherError('Failed to create RoboticArm object: '+str(e))
    port = arg_list[1]
    try:
        arm_obj.connect(port)
        arm_obj.begin()
    except ReceiverError as e:
        raise LauncherError('Failed to start Robotic Arm '+str(e))

def kill_arm(arg_list):
    global arm_obj
    if arm_obj is not None:
        try:
            arm_obj.disconnect()
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
