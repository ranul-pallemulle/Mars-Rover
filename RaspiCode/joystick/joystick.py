from threading import Thread, Lock
from sockets.tcpsocket import TcpSocket, TcpSocketError
from enum import Enum

'''Global locks to prevent race conditions.'''
state_lock = Lock()
value_lock = Lock()

class ConnState(Enum):
    '''Describe socket connection state.'''
    CLOSED = 1
    PENDING = 2
    READY = 3
    CLOSE_REQUESTED = 4
    RUNNING = 5

class JoystickError(Exception):
    '''Exception class that will be raised by Joystick class'''
    pass
    
class Joystick:
    '''Make a socket connection and receive two numbers in a new thread.'''
    def __init__(self):
        '''Make a Joystick object. Initialise connection state to closed'''
        self.xval = 0
        self.yval = 0
        self.state = ConnState.CLOSED
        self.socket = None

    def connect(self,port):
        '''Create a new TcpSocket if connection state is closed. Wait
        for a connection on specified port.'''
        with state_lock:
            if self.state == ConnState.CLOSED:
                self.state = ConnState.PENDING
            else:
                raise JoystickError('Socket open: cannot make new socket.')
        try:
            port_int = int(port)
            if float(port) - port_int > 0:
                raise ValueError
            assert port_int > 0
        except (ValueError, AssertionError) as e:
            print(str(e))
            self.disconnect_internal()
            raise JoystickError('Invalid value for port')
        self.port = port_int
        
        try:
            self.socket = TcpSocket(self.port)
            self.socket.set_max_recv_bytes(1024)
        except TcpSocketError as e:
            print(str(e))
            self.disconnect_internal()
            raise JoystickError('Error creating TcpSocket object')
        try:
            self.socket.wait_for_connection();
        except TcpSocketError as e:
            print(str(e))
            self.disconnect_internal()
            raise JoystickError('Error waiting for connection.')
        with state_lock:
            self.state = ConnState.READY

    def update_values(self):
        '''Update xval and yval with values received in a loop and
        send reply, while connection state is "running".'''
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
                print('Joystick disconnected')
                break
            data_arr = data.split(',')
            try:
                x = int(data_arr[0])
                y = int(data_arr[1])
            except (ValueError,IndexError) as e:
                print(str(e))
                self.disconnect_internal()
                print('Invalid data: joystick disconnected')
                break
            else:
                if x<=100 and x>=-100 and y<=100 and y>=-100:
                    with value_lock:
                        self.xval = x
                        self.yval = y
                    reply = 'ACK'
                else:
                    reply = 'ERR:RANGE'
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
                raise JoystickError('State not valid for thread start')

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
                raise JoystickError('Joystick already closed')
        self.socket.unblock()

    def get_xval(self):
        '''Get xval for external use.'''
        with value_lock:
            return self.xval

    def get_yval(self):
        '''Get yval for external use.'''
        with value_lock:
            return self.yval

    def get_state(self):
        '''Get current connection state for external use.'''
        with state_lock:
            return self.state
