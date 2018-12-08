# Responsible for controlling the state of various individual parts.
# Provides an interface for the main execution to control specific features
from joystick.joystick import Joystick, JoystickError

class LauncherError(Exception):
    '''Exception class that will be raised by launch functions.'''
    pass

'''Global objects'''
jstick_obj = None

def launch_joystick(arg_list):
    '''Start joystick operation if it is not running.'''
    global jstick_obj
    if jstick_obj is None:
        port = arg_list[1]      # need to check len(arg_list)
        try:
            jstick_obj = Joystick(port)
        except JoystickError as e:
            print(str(e))
            jstick_obj = None
            raise LauncherError('Failed to create Joystick object')
    try:
        jstick_obj.connect()
        jstick_obj.begin()
    except JoystickError as e:
        print(str(e))
        raise LauncherError('Failed to start Joystick')

def kill_joystick(arg_list):
    '''Stop joystick operation if it is running.'''
    global jstick_obj
    if jstick_obj is not None:
        try:
            jstick_obj.disconnect()
        except JoystickError as e:
            print(str(e))
            raise LauncherError('Joystick already closed')
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
