from abc import ABC, abstractmethod
from threading import RLock, Lock
from enum import Enum
import importlib
import os
from coreutils.diagnostics import Diagnostics as dg
import coreutils.configure as cfg

class State(Enum):
    ''' Operational mode states.'''
    STOPPED = 0
    RUNNING = 1
    STARTING = 2
    STOPPING = 3

class OpModeError(Exception):
    '''Exception class raised by OpMode.'''
    pass

class MethodCapture:
    '''Make a function into a wrapper around itself, such that a call to
it causes optional initialisation and finalisation functions to run before and
after it. Also allow the option of acquiring some lock for the duration of its call.'''
    def __init__(self, method, lock=None, run_before=None, run_after=None, exception_cleanup=None):
        self.lock = lock
        self.method = method
        self.run_before = run_before
        self.run_after = run_after
        self.cleanup = exception_cleanup

    def __call__(self, args):
        '''Function call wrapper around the target method. Runs run_before and
run_after accordingly and acquires and releases the lock before and after the target method call.'''
        if self.run_before is not None:
            self.run_before()
            
        if self.lock is not None:
            self.lock.acquire()      

        try:
            self.method(args)
        except OpModeError as e:
            if self.cleanup is not None:
                self.cleanup()
            if self.lock is not None:
                self.lock.release()
            raise e
        
        if self.run_after is not None:
            self.run_after()
            
        if self.lock is not None:
            self.lock.release()
            

class OpMode(ABC):
    '''Base class for all operational modes. This interfaces provides the
abstract methods start() and stop() and wraps them so that they are
called properly in the program context. All derived classes of this
class must register themselves using register_name() to be accessible
to the program as an operational mode.
    '''
    opmodes_list = dict()       # operational mode instances stored
                                # under their registered names.

    @classmethod
    def opmodes_initialise(cls):
        '''Look for derived classes in directories specified in the settings
file. Initialise them to register them and add to opmodes_list.'''
        try:
            dir_list = cfg.overall_config.opmodes_directories()
        except cfg.ConfigurationError as e:
            raise OpModeError(str(e))
        if not dir_list:
            dg.print("WARNING: no operational mode directories specified.")
        for folder in dir_list:
            if not folder:
                dg.print("WARNING: no operational modes found.")
                return
            if folder.endswith('.py'):
                folder = folder.split('.py')[0]
                path = folder.replace('/','.')
                try:
                    importlib.import_module(path)
                except FileNotFoundError as e:
                    raise OpModeError('Error in opmodes files list. Check settings file. : \n'+str(e))
            else:
                try:
                    for filename in os.listdir(folder):
                        if str(filename).endswith('.py'):
                            importlib.import_module(folder+'.'+str(filename).split('.')[0])
                except FileNotFoundError as e:
                    raise OpModeError('Error in opmode directories list. Check settings file. : \n'+str(e))
        for subcls in cls.__subclasses__():
            try:
                subcls()
            except TypeError as e:
                raise OpModeError(str(e))

    def __init__(self):
        ''' Wrap the start and stop functions. Initialise locks.'''
        self.opmode_state = State.STOPPED
        self.opmode_lock = RLock()
        self.start_lock = Lock()
        self.stop_lock = Lock()
        self.start = MethodCapture(method=self.start,
                                   lock=self.start_lock,
                                   run_before=self.before_start_call,
                                   run_after=self.after_start_call,
                                   exception_cleanup=self._manual_set_stopped)
        self.stop = MethodCapture(method=self.stop,
                                  lock=self.stop_lock,
                                  run_before=self.before_stop_call,
                                  run_after=self.after_stop_call,
                                  exception_cleanup=None)

    def register_name(self, name):
        '''Store opmode instance in opmode_list.'''
        if name in type(self).opmodes_list:
            dg.print('WARNING: Operational mode name {} already registered. Skipping...'.format(name))
            return
        type(self).opmodes_list[name] = self
        self.name = name

    def before_start_call(self):
        '''Call before the opmode's start() is executed.'''
        with self.opmode_lock:
            if not self.is_stopped():
                raise OpModeError('Cannot start {}: mode already active'.format(self.name))
            self.opmode_state = State.STARTING
        dg.print("Starting {} mode...".format(self.name))

    def after_start_call(self):
        '''Call after the opmode's start() is executed.'''
        with self.opmode_lock:
            self.opmode_state = State.RUNNING
        dg.print("{} mode started.".format(self.name))

    def before_stop_call(self):
        '''Call before the opmode's stop() is executed.'''
        with self.opmode_lock:
            if self.is_stopped():
                raise OpModeError('Cannot stop {}: already stopped'.format(self.name))
            elif self.is_stopping():
                raise OpModeError('Cannot stop {}: busy processing previous stop request.'.format(self.name))
            self.opmode_state = State.STOPPING
        dg.print("Stopping {} mode...".format(self.name))

    def after_stop_call(self):
        '''Call after the opmode's stop() is executed.'''
        with self.opmode_lock:
            self.opmode_state = State.STOPPED
        dg.print("{} mode stopped.".format(self.name))

    @classmethod
    def get(cls, name):
        '''Return the operational mode instance registered under 'name'.'''
        try:
            if cls.opmodes_list[name]:
                return cls.opmodes_list[name]
            return None
        except Exception as e:
            raise OpModeError(str(e))

    @classmethod
    def get_all(cls):
        '''Return all available operational mode instances.'''
        return cls.opmodes_list

    @classmethod
    def get_all_names(cls):
        '''Return a list of names of all registered operational modes.'''
        names_list = []
        for item in cls.opmodes_list.keys():
            names_list.append(item)
        return names_list

    @abstractmethod
    def start(self, args):
        '''Instance specific start method to begin mode operation.'''
        pass

    @abstractmethod
    def stop(self, args):
        '''Instance specific stop method to end mode operation.'''
        pass

    @abstractmethod
    def submode_command(self, args):
        '''Instance specific method for handling commands.'''
        pass

    def is_running(self):
        with self.opmode_lock:
            if self.opmode_state == State.RUNNING:
                return True
            return False

    def is_starting(self):
        with self.opmode_lock:
            if self.opmode_state == State.STARTING:
                return True
            return False

    def is_stopping(self):
        with self.opmode_lock:
            if self.opmode_state == State.STOPPING:
                return True
            return False

    def is_stopped(self):
        with self.opmode_lock:
            if self.opmode_state == State.STOPPED:
                return True
            return False

    def _manual_set_stopped(self):
        with self.opmode_lock:
            self.opmode_state = State.STOPPED

    def _manual_set_running(self):
        with self.opmode_lock:
            self.opmode_state = State.STOPPED

