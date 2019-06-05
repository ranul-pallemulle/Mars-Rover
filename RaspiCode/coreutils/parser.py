from interfaces.opmode import OpMode, OpModeError
from enum import Enum

OP_MODES = None

class CommandPrefixes(Enum):
    START = 1
    STOP = 2

class CommandError(Exception):
    pass
    
def parse_entry(command_string):
    '''Entry point for command parsing. There are three valid command
    forms:
    <[PREFIX]_[MODE] [ARGUMENTS]> 
    <[PREFIX] [MODE] [ARGUMENTS]>
    <[OP_MODE] -> [ARGUMENTS]
    The first two are mostly used to start and stop an operational
    mode. The third is to send a command to an already active
    mode.'''

    # Generate enum from OpMode operational modes list
    global OP_MODES
    OP_MODES = gen_enum()
    
    command_string = command_string.rstrip('\r\n')
    parsed_list = []
    
    arg_list = command_string.split(' ')
    if arg_list.count('') > 0:
        raise CommandError("Command has extra spaces or is empty")
    if is_opmode(arg_list[0]):
        if arg_list[1] == '->':
            parsed_list.append(get_opmode_enum_val(arg_list[0]).name)
            for x in arg_list[2:]:
                parsed_list.append(x)
            return parsed_list
        raise CommandError("Invalid submode command (command needs form <OPMODE> -> <ARGS>)")
    if is_prefix(arg_list[0]):
        if len(arg_list) < 2:
            raise CommandError("Invalid command (specify mode to run command on)")
        if is_opmode(arg_list[1]):
            parsed_list.append(get_prefix_enum_val(arg_list[0]))
            parsed_list.append(get_opmode_enum_val(arg_list[1]).name)
            for x in arg_list[2:]:
                parsed_list.append(x)
            return parsed_list
        raise CommandError("Cannot call {}. Invalid mode '{}'.".format(arg_list[0], arg_list[1]))
    split_first = arg_list[0].split('_')
    split_first_len = len(split_first)
    if split_first_len != 2:
        raise CommandError("Invalid command.")
    if is_prefix(split_first[0]):
        if is_opmode(split_first[1]):
            parsed_list.append(get_prefix_enum_val(split_first[0]))
            parsed_list.append(get_opmode_enum_val(split_first[1]).name)
            for x in arg_list[1:]:
                parsed_list.append(x)
            return parsed_list
        raise CommandError("Cannot call {}. Invalid mode '{}'.".format(split_first[0], split_first[1]))
    raise CommandError("Invalid command")

def is_opmode(word):
    global OP_MODES
    for x in OP_MODES:
        if word == x.name or word == x.name.upper():
            return True
    return False

def get_opmode_enum_val(word):
    global OP_MODES
    for x in OP_MODES:
        if word == x.name or word == x.name.upper():
            return x
    return None

def is_prefix(word):
    for x in CommandPrefixes:
        if word == x.name:
            return True
    return False

def get_prefix_enum_val(word):
    for x in CommandPrefixes:
        if word == x.name:
            return x
    return None


def gen_enum():
    '''Create an enum based on available operational modes.'''
    mode_names = OpMode.get_all_names().copy()
    enum_names = mode_names.copy()
    for i in range(len(mode_names)):
        enum_names[i] = mode_names[i]
    return Enum('OP_MODES', enum_names)
