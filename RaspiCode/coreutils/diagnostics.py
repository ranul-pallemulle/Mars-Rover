from coreutils.tcpsocket import TcpSocket, TcpSocketError
import coreutils.configure as cfg
from collections import deque
from threading import Thread, RLock
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
    state_lock = RLock()
    state = DiagState.CLOSED

    @classmethod
    def initialise(cls):
        '''Begin diagnostics operation. If diagnostics is enabled in settings,
        wait for a connection from remote. Call only in a DiagState.CLOSED 
        state. If a connection will be attempted, returns True, else returns 
        False.'''
        with cls.state_lock:
            if cls.state != DiagState.CLOSED:
                return False
        enabled = cfg.overall_config.diagnostics_enabled()
        if not enabled: # diagnostics connection won't be attempted
            return False
        cls.port = cfg.overall_config.diagnostics_port()
        with cls.state_lock:
            cls.state = DiagState.PENDING
            thread = Thread(target=cls._make_socket_connection, args=[])
            thread.start()
        return True


    @classmethod
    def _make_socket_connection(cls):
        '''Run in separate thread - cannot raise exceptions. Call only in a
        DiagState.PENDING state - else will result in a warning and return.'''
        with cls.state_lock: # prevent close() from running in this section
            if cls.state != DiagState.PENDING:
                cls.state = DiagStage.CLOSED
                cls.print("Diagnostics: invalid state to start connection. \
Closing...")
                return
            try:
                cls.socket = TcpSocket(cls.port)
                cls.socket.set_max_recv_bytes(1024)
            except TcpSocketError as e:
                cls.state = DiagState.CLOSED
                cls.print("Diagnostics connection error: "+str(e))
                return # no use restarting - cannot create TcpSocket
        cls.print("Waiting for diagnostics connection on port {}...".format(cls.port))
        try:
            cls.socket.wait_for_connection()
        except TcpSocketError as e:
            with cls.state_lock:
                if cls.state == DiagState.CLOSED: # manual close
                    cls.print("Diagnostics closed.")
                    return
                else: # unexpected termination
                    cls.state = DiagState.PENDING                    
                    cls.print("Diagnostics closed (connection error). Restarting...")
                    Thread(target=cls._make_socket_connection, args=[]).start()
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
                data = cls.socket.read() # block
            except TcpSocketError:
                with cls.state_lock:
                    if cls.state == DiagState.CLOSED: # manual close
                        cls.print("Diagnostics closed.")
                        return
                    else: # unexpected termination
                        cls.state = DiagState.PENDING                        
                        cls.print("Diagnostics closed (connection error). Restarting...")
                        Thread(target=cls._make_socket_connection, args=[]).start()
                        return
            if data is None:
                with cls.state_lock:
                    if cls.state == DiagState.CLOSED: # manual close
                        cls.print("Diagnostics closed.")
                        return
                    else: # unexpected termination
                        cls.state = DiagState.PENDING                        
                        cls.print("Diagnostics closed by remote. Restarting...")
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
            pass # _detect_close will handle connection termination


    @classmethod
    def close(cls):
        '''If diagnostics connection is pending, stop waiting for
    connection. Terminate an established connection.'''
        with cls.state_lock:
            prev_state = cls.state
            cls.state = DiagState.CLOSED
            if prev_state == DiagState.PENDING or \
                prev_state == DiagState.ESTABLISHED:
                cls.socket.unblock()
