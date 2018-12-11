from abc import ABCMeta, abstractmethod
from threading import Thread, Lock
from sockets.tcpsocket import TcpSocket, TcpSocketError
from enum import Enum

'''Global locks to prevent race conditions.'''
state_lock = Lock()

class ConnState(Enum):
    '''Describe socket connection state.'''
    CLOSED = 1
    PENDING = 2
    READY = 3
    CLOSE_REQUESTED = 4
    RUNNING = 5

class ControllerError(Exception):
    '''Exception class that will be raised by classes implementing Controller'''
    pass

class Controller:
    __metaclass__ = ABCMeta

    def __init__(self):
        self.state = ConnState.CLOSED
        self.socket = None

    def connect(self,port):
        '''Create a new TcpSocket if connection state is closed. Wait
        for a connection on specified port.'''
        with state_lock:
            if self.state == ConnState.CLOSED:
                self.state = ConnState.PENDING
            else:
                raise ControllerError('Socket open: cannot make new socket.')
        try:
            port_int = int(port)
            if float(port) - port_int > 0:
                raise ValueError
            assert port_int > 0
        except (ValueError, AssertionError) as e:
            print(str(e))
            self.disconnect_internal()
            raise ControllerError('Invalid value for port')
        self.port = port_int
        
        try:
            self.socket = TcpSocket(self.port)
            self.socket.set_max_recv_bytes(1024)
        except TcpSocketError as e:
            print(str(e))
            self.disconnect_internal()
            raise ControllerError('Error creating TcpSocket object')
        try:
            self.socket.wait_for_connection();
        except TcpSocketError as e:
            print(str(e))
            self.disconnect_internal()
            raise ControllerError('Error waiting for connection.')
        with state_lock:
            self.state = ConnState.READY

    @abstractmethod
    def store_received(self,recvd_list):
        pass

    def update_values(self):
        '''Update a list of values, received in a loop and send reply, while
        connection state is "running".'''
        while True:
            with state_lock:
                current_state = self.state
            if current_state == ConnState.READY:
                with state_lock:
                    self.state = ConnState.RUNNING
                    current_state = self.state
            elif current_state == ConnState.CLOSED:
                break
            elif current_state == ConnState.CLOSE_REQUESTED or\
                 current_state == ConnState.PENDING:
                self.disconnect_internal()
                break
            if current_state != ConnState.RUNNING:
                print('Invalid value of current_state')
                self.disconnect_internal()
                break
            try:
                data = self.socket.read()
            except TcpSocketError as e:
                print(str(e))
                self.disconnect_internal()
                break
            if data is None:
                self.disconnect_internal()
                print('Controller disconnected') # find a way to specify which controller
                break
            data_arr = data.split(',')
            reply = self.store_received(data_arr)
            if reply is None:
                self.disconnect_internal()
                break
            try:
                self.socket.reply(reply)
            except TcpSocketError as e:
                print(str(e))
                self.disconnect_internal()
                break
                
    def begin(self):
        '''Run update_values in a new thread, if connection state is ready.'''
        with state_lock:
            if self.state == ConnState.READY:
                thread = Thread(target=self.update_values, args=())
                thread.start()
            else:
                raise ControllerError('State not valid for thread start')

    def disconnect_internal(self):
        '''Close the socket and set the connection state to closed'''
        with state_lock:
            if self.state == ConnState.CLOSED:
                return
        with state_lock:
            self.state = ConnState.CLOSED
        if self.socket is not None:
            self.socket.close()
            self.socket = None

    def disconnect(self):
        '''Externally set connection state to a requested close to
        stop the update_value loop.'''
        with state_lock:
            if self.state == ConnState.CLOSED:
                raise ControllerError('Controller already closed') # find a way to specify which controller
        self.socket.unblock()
                
    def get_state(self):
        '''Get current connection state for external use.'''
        with state_lock:
            return self.state
