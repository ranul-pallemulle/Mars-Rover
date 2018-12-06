# Responsible for controlling the state of various individual parts.
# Provides an interface for the main execution to control specific features
import socket
from joystick import joystick
from sockets.tcpsocket import TcpSocketError
from enum import Enum
class State(Enum):
    RUNNING = 1
    STOPPED = 2

class LauncherError(Exception):
    pass

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
        raise LauncherError('Incorrect number of args for launch_joystick')
    try:
        jstick_obj = joystick.Joystick(arg_list[1])
    except (socket.error,ValueError,TcpSocketError) as e:
        print(str(e))
        raise LauncherError('Joystick failed to create socket')
    try:
        jstick_obj.connect()
    except (socket.error,ValueError,joystick.JoystickError) as e:
        print(str(e))
        raise LauncherError('Joystick failed to connect to remote')
    try:
        jstick_obj.begin()
    except joystick.JoystickError as e:
        print(str(e))    
        raise LauncherError('Joystick in invalid state for starting')
    joystick_state = State.RUNNING
    

def kill_joystick(arg_list):
    global jstick_obj
    global joystick_state
    if joystick_state == State.STOPPED:
        return
    if len(arg_list) != 1:
        raise LauncherError('Incorrect number of args for kill_joystick')
    try:
        jstick_obj.disconnect()
    except socket.error as e:
        print(str(e))
        raise LauncherError('Error running joystick disconnect()')
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
