from enum import Enum
class CommandTypes(Enum):
    START_JOYSTICK = 1
    STOP_JOYSTICK = 2
    START_ARM = 3
    STOP_ARM = 4

class CommandError(Exception):
    pass
    
def parse(command_string):
    '''Parse commands received from remote computer. 
    Commands have the form "command_type <optional_arg1> <optional_arg2"'''
    parsed_list = []
    arg_list = command_string.split(' ')
    if arg_list.count('') > 0:
        raise CommandError("Command has extra spaces or is empty")
    for x in CommandTypes:
        if arg_list[0] == x.name:
            parsed_list.append(x)
    if len(parsed_list) != 1:
        raise CommandError("Invalid command")
    arglen = len(arg_list)
    if arglen > 1:
        parsed_list.append(arg_list[1])
        if arglen == 3:
            parsed_list.append(arg_list[2])
        elif arglen > 3:
            raise CommandError('Too many arguments to command string')
    return parsed_list
        
