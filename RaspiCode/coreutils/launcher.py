# Responsible for controlling the state of various individual parts.
# Provides an interface for the main execution to control specific features
from interfaces.opmode import OpMode, OpModeError
from coreutils.diagnostics import Diagnostics as dg
from coreutils.parser import CommandPrefixes

class LauncherError(Exception):
    '''Exception class that will be raised by launch functions.'''
    pass

def call_action(arg_list):
    '''Based on command, do something.'''
    try:
        if arg_list[0] == CommandPrefixes.START: # start an operational mode
            launch_opmode(arg_list[1], arg_list[2:])
        elif arg_list[0] == CommandPrefixes.STOP: # stop an operational mode
            kill_opmode(arg_list[1], arg_list[2:])
        else:                   # command is to be passed to a specific mode
            mode_name = arg_list[0]
            mode = OpMode.get(mode_name) # get mode using its registered
                                         # name. Throws OpModeError if mode_name
                                         # is invalid.
            if mode.is_running():
                mode.submode_command(arg_list[1:]) # pass command to the mode
            else:
                dg.print("{} not active. Start {} before passing submode commands.".format(mode_name, mode_name))
    except (LauncherError, OpModeError) as e: # error carrying out action
        dg.print(str(e))
        return                  # terminate thread - stop processing current command

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
    
