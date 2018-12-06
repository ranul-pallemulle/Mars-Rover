from threading import Thread, Lock
import socket
from sockets.tcpsocket import TcpSocket, TcpSocketError
from enum import Enum

state_lock = Lock()
value_lock = Lock()
sock_lock = Lock()

class ConnState(Enum):
    CLOSED = 1
    READY = 2
    CLOSE_REQUESTED = 3
    RUNNING = 4

class JoystickError(Exception):
    pass
    
class Joystick:
    def __init__(self, port):
        self.xval = 0
        self.yval = 0
        try:
            with sock_lock:
                port = int(port)
                self.socket = TcpSocket(port)
                self.socket.set_max_recv_bytes(1024)
        except (socket.error,ValueError, TcpSocketError):
            self.socket = None
            raise
        self.state = ConnState.READY

    def connect(self):
        with state_lock:
            if self.state == ConnState.CLOSED:
                self.state = ConnState.READY
            if self.state != ConnState.READY:
                raise JoystickError('Not ready for a new connection')
        try:
            self.socket.wait_for_connection();
        except (socket.error, socket.timeout):
            self.socket = None
            raise

    def update_values(self):
        while True:
            with state_lock:
                current_state = self.state
            if current_state == ConnState.READY:
                with state_lock:
                    self.state = ConnState.RUNNING
                    current_state = self.state
            elif current_state == ConnState.CLOSED:
                break
            elif current_state == ConnState.CLOSE_REQUESTED:
                self.disconnect()
                return
            if current_state != ConnState.RUNNING:
                self.socket = None
                raise JoystickError('Invalid state (ConnState)')

            try:
                with sock_lock:
                    data = self.socket.read()
            except (socket.error, socket.timeout,TcpSocketError):
                self.socket = None
                raise
#            data = data.decode()
            if data == 'KILL':
                with state_lock:
                    self.state = ConnState.CLOSE_REQUESTED
            else:
                data_arr = data.split(',')
                try:
                    x = int(data_arr[0])
                    y = int(data_arr[1])
                except ValueError:
                    self.socket = None
                    raise
                else:
                    if x<=100 and x>=-100 and y<=100 and y>=-100:
                        with value_lock:
                            self.x = x
                            self.y = y
                    else:
                        reply = 'ERR:RANGE'
                        try:
                            with sock_lock:
                                self.socket.reply(str.encode(reply))
                        except socket.error:
                            self.socket = None
                            raise
                        else:
                            continue
                reply = 'ACK'
                try:
                    with sock_lock:
                        self.socket.reply(str.encode(reply))
                except socket.error:
                    self.socket = None
                    raise
        with state_lock:
            self.state = ConnState.CLOSED

    def begin(self):
        with state_lock:
            if self.state == ConnState.READY:
                thread = Thread(target=self.update_values, args=())
                thread.start()
            else:
                raise JoystickError('State not valid for thread start')

    def disconnect(self):
        if self.state == ConnState.CLOSED:
            return
        with state_lock:
            self.state = ConnState.CLOSED
        try:
            self.socket.close()
        except socket.error:
            self.socket = None
            raise

    def get_xval(self):
        with value_lock:
            return self.xval

    def get_yval(self):
        with value_lock:
            return self.yval

    def get_state(self):
        with state_lock:
            return self.state
