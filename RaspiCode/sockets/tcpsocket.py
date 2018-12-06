import socket

class TcpSocketError(Exception):
    pass

class TcpSocket:
    '''Wrapper around socket API'''
    sock = None
    conn = None
    max_recv_bytes = 128
    def __init__(self, port):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.setblocking(1)
            self.sock.bind(('', port))
            self.sock.listen(1)
        except socket.error:
            raise TcpSocketError("Error initialising socket")
    def wait_for_connection(self):
        try:
            self.conn,_ = self.sock.accept()
        except (socket.error, socket.timeout):
            raise TcpSocketError("Error waiting for connection")

    def read(self):
        if self.conn is not None:
            try:
                data = self.conn.recv(self.max_recv_bytes)
            except (socket.error, socket.timeout):
                raise TcpSocketError("Error waiting for data")
            if len(data) == 0:
                raise TcpSocketError("Connection lost")
            data = data.decode()
            return data
        raise TcpSocketError('Connection not initialised')

    def reply(self, data):
        if self.conn is not None:
            try:
               self.conn.sendall(data)
            except socket.error as e:
                print(str(e))
        else:
            raise TcpSocketError('Connection not initialised')

    def close(self):
        if self.conn is not None:
            self.conn.close()
            self.sock.close()

    def set_max_recv_bytes(self, numbytes):
        if numbytes < 0:
            raise TcpSocketError('max_recv_bytes needs to be positive')
        try:
            numbytes = int(numbytes)
        except ValueError:
            raise TcpSocketError('max_recv_bytes must be an integer')
        self.max_recv_bytes = numbytes
