import socket
from threading import Thread, Lock
from decimal import Decimal
from enum import Enum

state_lock = Lock();
value_lock = Lock();

class State(Enum):
        CLOSED = 1
        READY = 2
        CLOSE_REQUESTED = 3
        RUNNING = 4

class Joystick:
        def __init__(self,port):
                self.host = ''
                self.port = port
                self.socket = None
                self.conn = None
                self.value = 0
                self.state = State.READY

        def connect(self):
                with state_lock:
                        if self.state == State.CLOSED:
                                self.state = State.READY
                        if self.state != State.READY:
                                print("Not ready for a new connection")
                self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                try:
                        self.socket.bind((self.host,self.port))
                except Exception as e:
                        print(str(e))
                self.socket.listen(1)
                self.conn,_ = self.socket.accept()


        def update_value(self):     # make state access thread-safe pls
                        
                while True:
                        with state_lock:
                                current_state = self.state

                        if current_state == State.READY: # only start if connection is ready
                                with state_lock:
                                        self.state = State.RUNNING
                                        current_state = self.state
                        elif current_state == State.CLOSED: # can't start while connection not available
                                break
                        elif current_state == State.CLOSE_REQUESTED: # want to stop
                                self.disconnect() # disconnect obtains a lock, make sure we aren't locked during this call
                                break
                        if current_state != State.RUNNING: # other cases handled above
                                print("Invalid state")
                                break
                        try:
                                data  = self.conn.recv(1024)
                        except Exception as e:
                                print("Socket error while waiting for data")
                                break
                        data = data.decode()
                        if data == 'KILL\n':
                                with state_lock:
                                        self.state = State.CLOSE_REQUESTED
                        else:
                                try:
                                        recv_num = Decimal(data)
                                except Exception as e:
                                        print("Unknown command")
                                else:        
                                        if recv_num <= 1 and recv_num >= -1:
                                                with value_lock:
                                                        self.value = recv_num
                                        else:
                                                reply = '|value| must be < 1\n'
                                                self.conn.sendall(str.encode(reply))
                                                continue
                        print(data)        
                        reply = 'ACK\n'
                        try:
                                self.conn.sendall(str.encode(reply))
                        except Exception as e:
                                print("Socket error while sending reply")
                                break
                with state_lock: # when while breaks
                        self.state = State.CLOSED

        def begin(self):
                with state_lock:
                        if self.state == State.READY:
                                thread = Thread(target=self.update_value, args=())
                                thread.start()
                        else:
                                print("Cannot start, state is not State.READY")


        def disconnect(self):
        # only ever call this from within update_value. Use state=State.CLOSE_REQUESTED to initiate close
                with state_lock:
                        self.state = State.CLOSED
                self.conn.close()
                self.socket.close()

        def get_value(self):    # for external use only (avoid deadlock)
                with value_lock:
                        return self.value

        def get_state(self):    # for external use only (avoid deadlock)
                with state_lock:
                        return self.state
    
        def set_state(self, state): # for external use only (avoid deadlock)
                with state_lock:
                        self.state = state
        
                
