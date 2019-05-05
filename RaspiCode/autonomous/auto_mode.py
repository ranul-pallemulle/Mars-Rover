from abc import ABC, ABCMeta, abstractmethod
from interfaces.opmode import OpMode, OpModeError
from coreutils.diagnostics import Diagnostics as dg
from threading import Thread
import importlib
import os
from functools import wraps

class MetaGoal(ABCMeta):
    def __new__(meta, name, bases, attr):
        if not 'run' in attr:
            raise AttributeError("abstract method 'run' not implemented in \
class "+name)
        runmeth = attr['run']
        if not '__isabstractmethod__' in runmeth.__dict__:
            @wraps(runmeth)
            def runwrapper(self, *args, **kwargs):
                if not self.running:
                    dg.print("Starting goal {}...".format(self.name))
                    try:
                        res = runmeth(self, *args, **kwargs)
                    except GoalError as e:
                        dg.print(str(e))
                        return
                    self.running = True
                    dg.print("Goal {} started.".format(self.name))
                    return res                    
                else:
                    dg.print("Warning: goal already running - cannot call\
 run()")
            attr['run'] = runwrapper

        if not 'cleanup' in attr:
            raise AttributeError("abstract method 'cleanup' not implemented in\
class "+name)
        cleanmeth = attr['cleanup']
        if not '__isabstractmethod__' in cleanmeth.__dict__:
            @wraps(cleanmeth)
            def cleanwrapper(self, *args, **kwargs):
                if self.running:
                    dg.print("Stopping goal {}...".format(self.name))     
                    try:
                        res = cleanmeth(self, *args, **kwargs)
                    except GoalError as e:
                        dg.print(str(e))
                        return
                    self.running = False
                    dg.print("Goal {} stopped.".format(self.name))
                    return res
                else:
                    dg.print("Warning: goal not running - cannot call stop()")
            attr['cleanup'] = cleanwrapper
        return super(MetaGoal, meta).__new__(meta, name, bases, attr)

class GoalError(Exception):
    '''Exception class raised by Goal'''
    pass


class Goal(ABC,metaclass=MetaGoal):
    '''Base class for all goals.'''
    goals_list = dict()

    def __init__(self):
        self.running = False
        self.name = None
    
    def register_name(self, name):
        if name in type(self).goals_list:
            dg.print("Warning: goal name '{}' already taken. Skipping..."
                     .format(name))
            return
        type(self).goals_list[name] = self
        self.name = name

    @abstractmethod
    def run(self):
        '''Start goal operation.'''
        pass

    @abstractmethod
    def cleanup(self):
        '''Do any optional cleanup (e.g. resource release.)'''
        pass

    @classmethod
    def get_list(cls):
        return cls.goals_list

    def is_running(self):
        return self.running


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
        for goal_name in Goal.get_list():
            goal = Goal.get_list()[goal_name]
            if goal.is_running():
                goal.cleanup()

    def submode_command(self, args):
        '''All goals activated via submode commands.'''
        # dg.print("Command received is: ")
        # subcomm = ""
        # for x in args:
        #     subcomm += (x + ' ')
        # dg.print("    "+subcomm)
        thread = Thread(target=self.parse_submode_comm, args=[args])
        thread.start()

    def parse_submode_comm(self, args):

        if args[0].upper() == "GOAL":
            if len(args) < 3:
                dg.print("Warning: subcommand needs to have at least 3 \
arguments")
                return
            goal_str = args[1]
            if goal_str in Goal.get_list():
                goal = Goal.get_list()[goal_str]
            else:
                dg.print("Warning: goal '{}' not found".format(goal_str))
                return
            comm_str = args[2].upper()
            if comm_str == "START":
                goal.run()
            elif comm_str == "STOP":
                goal.cleanup()
            else:
                dg.print("Warning: goal commands other than 'start' and 'stop'\
 unimplemented")
            
        else:
            dg.print("Warning: Non-goal Auto mode sub-commands unimplemented.")
            
