from abc import ABCMeta, abstractmethod
from threading import Thread, Lock
from coreutils.tcpsocket import TcpSocket, TcpSocketError
from enum import Enum

class ConnState(Enum):
    '''Describe socket connection state.'''
    CLOSED = 1
    PENDING = 2
    READY = 3
    CLOSE_REQUESTED = 4
    RUNNING = 5

class ReceiverError(Exception):
    '''Exception class that will be raised by classes implementing Receiver'''
    pass

class Receiver:
    '''Receive values via a TcpSocket on a separate thread. Valid format
of received values is determined by store_received.'''
    __metaclass__ = ABCMeta

    def __init__(self):
        self.state = ConnState.CLOSED
        self.socket = None
        self.state_lock = Lock()

    def connect(self,port):
        '''Create a new TcpSocket if connection state is closed. Wait
        for a connection on specified port.'''
        print("{}: waiting for connection...".format(self.__class__.__name__))
        with self.state_lock:
            if self.state == ConnState.CLOSED:
                self.state = ConnState.PENDING
                self.set_state_as_running() # inform subclass that things are starting
            else:
                raise ReceiverError('Socket open: cannot make new socket.')
        try:
            port_int = int(port)
            if float(port) - port_int > 0:
                raise ValueError
            assert port_int > 0
        except (ValueError, AssertionError) as e:
            print(str(e))
            self.disconnect_internal()
            raise ReceiverError('Invalid value for port')
        self.port = port_int
        
        try:
            self.socket = TcpSocket(self.port)
            self.socket.set_max_recv_bytes(1024)
        except TcpSocketError as e:
            print(str(e))
            self.disconnect_internal()
            raise ReceiverError('Error creating TcpSocket object')
        try:
            self.socket.wait_for_connection();
        except TcpSocketError as e:
            print(str(e))
            self.disconnect_internal()
            raise ReceiverError('Error waiting for connection.')
        with self.state_lock:
            self.state = ConnState.READY
        print("{}: connected.".format(self.__class__.__name__))

    @abstractmethod
    def store_received(self,recvd_list):
        pass

    @abstractmethod
    def run_on_connection_interrupted(self):
        pass

    @abstractmethod
    def set_state_as_running(self):
        pass

    def update_values(self):
        '''Update a list of values, received in a loop and send reply, while
        connection state is "running".'''
        while True:
            with self.state_lock:
                current_state = self.state
            if current_state == ConnState.READY:
                with self.state_lock:
                    self.state = ConnState.RUNNING
                    current_state = self.state
            elif current_state == ConnState.CLOSED:
                break
            elif current_state == ConnState.CLOSE_REQUESTED or\
                 current_state == ConnState.PENDING:
                self.disconnect_internal()
                self.run_on_connection_interrupted()
                break
            if current_state != ConnState.RUNNING:
                print('Invalid value of current_state')
                self.disconnect_internal()
                self.run_on_connection_interrupted()
                break
            try:
                data = self.socket.read()
            except TcpSocketError as e:
                print(str(e))
                self.disconnect_internal()
                self.run_on_connection_interrupted()
                break
            if data is None:
                self.disconnect_internal()
                self.run_on_connection_interrupted()
                break
            data_arr = data.split(',')
            reply = self.store_received(data_arr)
            if reply is None:
                print("{}: invalid values received".format(self.__class__.__name__))
                self.disconnect_internal()
                self.run_on_connection_interrupted()
                break
            try:
                self.socket.reply(reply)
            except TcpSocketError as e:
                print(str(e))
                self.disconnect_internal()
                self.run_on_connection_interrupted()
                break
                
    def begin_receive(self):
        '''Run update_values in a new thread, if connection state is ready.'''
        with self.state_lock:
            if self.state == ConnState.READY:
                thread = Thread(target=self.update_values, args=())
                thread.start()
            else:
                raise ReceiverError('State not valid for thread start')

    def disconnect_internal(self):
        '''Close the socket and set the connection state to closed'''
        with self.state_lock:
            if self.state == ConnState.CLOSED:
                return
        print("{}: disconnecting...".format(self.__class__.__name__))
        with self.state_lock:
            self.state = ConnState.CLOSED
        if self.socket is not None:
            self.socket.close()
            self.socket = None
        print("{}: disconnected.".format(self.__class__.__name__))

    def disconnect(self):
        '''Externally set connection state to a requested close to
        stop the update_value loop.'''
        with self.state_lock:
            if self.state == ConnState.CLOSED:
                raise ReceiverError('{} controller already closed'.format(self.__class__.__name__))
        self.socket.unblock()
                
    def get_state(self):
        '''Get current connection state for external use.'''
        with self.state_lock:
            return self.state
