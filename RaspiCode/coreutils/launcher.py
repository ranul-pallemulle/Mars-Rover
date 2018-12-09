# Responsible for controlling the state of various individual parts.
# Provides an interface for the main execution to control specific features
from joystick.joystick import Joystick, JoystickError

class LauncherError(Exception):
    '''Exception class that will be raised by launch functions.'''
    pass

'''Global objects'''
jstick_obj = None

def release_all():
    '''Close all resources so that shutdown can be done.'''
    try:
        kill_joystick([])
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
        except JoystickError as e:
            jstick_obj = None
            raise LauncherError('Failed to create Joystick object: '+str(e))
    port = arg_list[1]      # need to check len(arg_list)
    try:
        jstick_obj.connect(port)
        jstick_obj.begin()
    except JoystickError as e:
        raise LauncherError('Failed to start Joystick: '+str(e))

def kill_joystick(arg_list):
    '''Stop joystick operation if it is running.'''
    global jstick_obj
    if jstick_obj is not None:
        try:
            jstick_obj.disconnect()
        except JoystickError as e:
            raise LauncherError(str(e))
    else:
        raise LauncherError('Joystick object not initialised')
            

def toggle_joystick(arg_list):
    pass

def launch_camera(arg_list):
    pass

def kill_camera(arg_list):
    pass

def launch_auto(arg_list):
    pass

def kill_auto(arg_list):
    pass
