from abc import ABC, abstractmethod
from interfaces.opmode import OpMode, OpModeError
from coreutils.diagnostics import Diagnostics as dg
from threading import Thread
import importlib
import os

class Goal(ABC):
    '''Base class for all goals.'''
    goals_list = dict()
    
    def register_name(self, name):
        type(self).goals_list[name] = self
    
    @abstractmethod
    def initialise(self):
        pass

    @abstractmethod
    def deinitialise(self):
        pass

    @classmethod
    def get_list(cls):
        return cls.goals_list


class Autonomous(OpMode):
    '''Main autonomous mode. All autonomous functionality is implemented
as 'goals' and are activated through submode commands when this mode
is active. Each goal may have its own resource requirements, so
resource acquisition is done by a given goal as needed.
    '''

    def __init__(self):
        OpMode.__init__(self)
        self.register_name("Auto")
        self.goals_initialise()

    def goals_initialise(self):
        '''Look for goals in autonomous directory. Initialise them to register
them and add to goals_list.'''
        for filename in os.listdir('.'):
            if str(filename) == "auto_mode.py":
                continue
            if str(filename).startswith('goal_') and \
               str(filename).endswith('.py'):
                importlib.import_module(str(filename).split('.')[0])
        
        for subcls in Goal.__subclasses__():
            try:
                subcls()
            except TypeError as e:
                raise OpModeError(str(e))
            

    def start(self, args):
        dg.print("Available goals:")
        for goal_name in Goal.get_list():
            dg.print("    "+goal_name)

    def stop(self, args):
        pass                    # may need to disable any active goals

    def submode_command(self, args):
        '''All goals activated via submode commands.'''
        dg.print("Command received is: ")
        subcomm = ""
        for x in args:
            subcomm += (x + ' ')
        dg.print("    "+subcomm)
        thread = Thread(target=self.parse_submode_comm, args=[args])
        thread.start()

    def parse_submode_comm(self, args):

        if args[0].upper() == "GOAL":
            if len(args) < 2:
                dg.print("Warning: subcommand needs to have at least 2 \
arguments")
            goal_str = args[1]
            
        else:
            dg.print("Warning: Non-goal Auto mode sub-commands unimplemented.")
