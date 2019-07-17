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
        '''Begin diagnostics operation. If diagnostics is enabled in settings,
        wait for a connection from remote.'''
        enabled = cfg.overall_config.diagnostics_enabled()
        if not enabled: # diagnostics connection won't be attempted
            return
        cls.port = cfg.overall_config.diagnostics_port()
        thread = Thread(target=cls._make_socket_connection, args=[])
        thread.start()


    @classmethod
    def _make_socket_connection(cls):
        '''Run in separate thread - cannot raise exceptions. Call only in a
        DiagState.CLOSED state - else will result in a warning and return.'''
        with cls.state_lock: # prevent close() from running in this section
            try:
                cls.socket = TcpSocket(cls.port)
                cls.socket.set_max_recv_bytes(1024)
            except TcpSocketError as e:
                cls.print("Diagnostics connection error: "+str(e))
                return
        cls.print("Waiting for diagnostics connection on port {}...".format(cls.port))
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
        thread.start() # release lock after thread started


    @classmethod
    def _detect_close(cls):
        '''Run in separate thread - cannot raise exceptions. Call when in a 
        DiagState.ESTABLISHED state. If the connection is closed during the 
        time between going into the ESTABLISHED state and calling this 
        function, this function will detect it and amend the state accordingly.
        '''
        while True:
            try:
                data = cls.socket.read()
            except TcpSocketError:
                with cls.state_lock:
                    cls.state = DiagState.CLOSED
                cls.print("Diagnostics closed (connection error).")
                cls.socket.close()
                cls.socket = None
                # return
                Thread(target=cls._make_socket_connection, args=[]).start()
                return
            if data is None:
                with cls.state_lock:
                    cls.state = DiagState.CLOSED
                cls.print("Diagnostics closed by remote.")
                cls.socket.close()
                cls.socket = None
                # return
                Thread(target=cls._make_socket_connection, args=[]).start()
                return


    @classmethod
    def print(cls, msg):
        '''Send a message on an established diagnostics connection. Does not 
        raise exceptions - prints only to console if exception occurs.'''
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
        with cls.state_lock: # ensure that this block is not run concurrently 
                             # with _make_socket_connection or with itself
            if cls.state == DiagState.PENDING or \
                cls.state == DiagState.ESTABLISHED:
                cls.socket.unblock()
        while True: # wait till closed
            with cls.state_lock:
                if cls.state == DiagState.CLOSED:
                    break
