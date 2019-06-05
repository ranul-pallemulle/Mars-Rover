from coreutils.tcpsocket import TcpSocket, TcpSocketError
import coreutils.configure as cfg
from collections import deque
from threading import Thread, Lock
from enum import Enum

class DiagState(Enum):
    CLOSED = 1
    PENDING = 2
    ESTABLISHED = 3

class DiagnosticsError(Exception):
    '''Exception class that will be raised by Diagnostics.'''
    pass

class Diagnostics:
    '''Sending diagnostic messages back to a remote controller.'''
    buf = deque(maxlen = 20)    # buffer of unsent messages
    state_lock = Lock()
    state = DiagState.CLOSED

    @classmethod
    def initialise(cls):
        enabled = cfg.overall_config.diagnostics_enabled()
        if not enabled:
            return
        port = cfg.overall_config.diagnostics_port()
        thread = Thread(target=cls._make_socket_connection, args=[port])
        thread.start()

    @classmethod
    def _make_socket_connection(cls,port):
        try:
            cls.socket = TcpSocket(port)
            cls.socket.set_max_recv_bytes(1024)
        except TcpSocketError as e:
            raise DiagnosticsError(str(e))
        cls.print("Waiting for diagnostics connection on port {}...".format(port))
        with cls.state_lock:
            cls.state = DiagState.PENDING
        try:
            cls.socket.wait_for_connection()
        except TcpSocketError as e:
            with cls.state_lock:
                cls.state = DiagState.CLOSED
            cls.print("Diagnostics closed.")
            return
        with cls.state_lock:
            cls.state = DiagState.ESTABLISHED
        cls.print("Diagnostics connection established.")  
        thread = Thread(target=cls._detect_close, args=[])
        thread.start()

    @classmethod
    def _detect_close(cls):
        while True:
            try:
                data = cls.socket.read()
            except TcpSocketError:
                with cls.state_lock:
                    cls.state = DiagState.CLOSED
                cls.print("Diagnostics closed (connection error).")
                return
            if data is None:
                with cls.state_lock:
                    cls.state = DiagState.CLOSED
                cls.print("Diagnostics closed by remote.")
                return

    @classmethod
    def print(cls, msg):
        '''Send a message on an established diagnostics connection. Does not raise exceptions - prints to console if exception occurs.'''
        print(msg)
        with cls.state_lock:
            if cls.state != DiagState.ESTABLISHED:
                cls.buf.append(msg)
                return
        try:
            while cls.buf:
                cls.socket.reply(cls.buf.popleft()) # send unsent messages first
            cls.socket.reply(msg)
        except TcpSocketError:
            with cls.state_lock:
                cls.state = DiagState.CLOSED
            cls.print("Diagnostics connection lost.")

    @classmethod
    def close(cls):
        '''If diagnostics connection is pending, stop waiting for connection.'''
        with cls.state_lock:
            if cls.state == DiagState.PENDING or \
                cls.state == DiagState.ESTABLISHED:
                cls.socket.unblock()
