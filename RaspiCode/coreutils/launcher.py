# Responsible for controlling the state of various individual parts.
# Provides an interface for the main execution to control specific features
from joystick import joystick
from enum import Enum
class State(Enum):
    RUNNING = 1
    STOPPED = 2

joystick_state = State.STOPPED
camera_state = State.STOPPED
auto_state = State.STOPPED

jstick_obj = None

def launch_joystick(arg_list):
    global jstick_obj
    global joystick_state
    if joystick_state == State.RUNNING:
        return
    
    if len(arg_list) != 2:
        raise Exception
    try:
        jstick_obj = joystick.Joystick(arg_list[1])
    except Exception as e:
        print(str(e))
        raise
    jstick_obj.connect()
    jstick_obj.begin()
    joystick_state = State.RUNNING
    

def kill_joystick(arg_list):
    global jstick_obj
    global joystick_state
    if joystick_state == State.STOPPED:
        return
    if len(arg_list) != 1:
        raise Exception
    jstick_obj.disconnect()
    joystick_state = State.STOPPED

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
