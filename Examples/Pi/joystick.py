import socket
from threading import Thread
from decimal import Decimal

class Joystick:
    def __init__(self,port):
        self.host = ''
        self.port = port
        self.socket = None
        self.conn = None
        self.value = 0
        self.state = 'CLOSED'


    def connect(self):
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.socket.bind((self.host,self.port))
        except Exception as e:
            print(str(e))
        self.socket.listen(1)
        self.conn,_ = self.socket.accept()


    def update_value(self):
        while True:
            if self.state == 'CLOSED':
                self.state = 'RUNNING'
            if self.state == 'CLOSE_REQUESTED':
                self.disconnect()
                break
            else:
                data  = self.conn.recv(1024)
                data = data.decode()
                print(data)

                if data == 'KILL':
                    self.state = 'CLOSE_REQUESTED'
                else:
                    self.value = Decimal(data)
                    reply = 'ACK'
                    self.conn.sendall(str.encode(reply))

    def begin(self):
        thread = Thread(target=update_value)


    def disconnect(self):
        while self.state == 'RUNNING':
            pass
        self.conn.close()
        self.socket.close()

    def get_value(self):
        return self.value
        
                
