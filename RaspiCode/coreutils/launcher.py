# Responsible for controlling the state of various individual parts.
# Provides an interface for the main execution to control specific features
from interfaces.opmode import OpMode, OpModeError
import coreutils.resource_manager as mgr

class LauncherError(Exception):
    '''Exception class that will be raised by launch functions.'''
    pass

def release_all():
    '''Close all resources so that shutdown can be done.'''
    mode_names = OpMode.get_all_names()
    for name in mode_names:
        mode = OpMode.get(name)
        if not mode.is_stopped():
            kill_opmode(name)

def launch_opmode(name, arg_list=[]):
    mode = OpMode.get(name)
    if mode is None:
        raise LauncherError('No operational mode named {}'.format(name))
    try:
        mode.start(arg_list)
    except OpModeError as e:
        raise LauncherError('Failed to start {}: '.format(mode.name)+str(e))


def kill_opmode(name, arg_list=[]):
    mode = OpMode.get(name)
    if mode is None:
        raise LauncherError('No operational mode names {}'.format(name))
    try:
        mode.stop(arg_list)
    except OpModeError as e:
        raise LauncherError('Failed to stop {}: '.format(mode.name)+str(e))
