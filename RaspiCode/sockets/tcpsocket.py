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
            self.conn = None
            self.sock = None
            raise
    def wait_for_connection(self):
        try:
            self.conn,_ = self.sock.accept()
        except (socket.error, socket.timeout):
            self.conn = None
            self.sock = None
            raise

    def read(self):
        if self.conn is not None:
            try:
                data = self.conn.recv(self.max_recv_bytes)
            except (socket.error, socket.timeout,OSError):
                self.conn = None
                self.sock = None
                raise
            if len(data) == 0:
                try:
                    self.conn.close()
                    self.sock.close()
                except socket.error:
                    self.conn = None
                    self.sock = None
                raise TcpSocketError("Connection lost")
            data = data.decode()
            return data
        try:
            self.sock.close()
        except socket.error:
            self.sock = None
        raise TcpSocketError('Connection not initialised')

    def reply(self, data):
        if self.conn is not None:
            try:
               self.conn.sendall(data)
            except (socket.error, socket.timeout,OSError):
                self.conn = None
                self.sock = None
                raise
        else:
            raise TcpSocketError('Connection not initialised')

#    def close(self, sockobj):
#        if sockobj is not None:
#            try:
#                sockobj.close()
#            except socket.error:
#                self.conn = None
#                self.sock = None

    def close(self):
        if self.conn is not None:
            try:
                self.conn.close()
                self.sock.close()
            except socket.error:
                self.conn = None
                self.sock = None                

    def set_max_recv_bytes(self, numbytes):
        if numbytes < 0:
            try:
                self.conn.close()
                self.sock.close()
            except socket.error:
                self.sock = None
                self.conn = None
            raise TcpSocketError('max_recv_bytes needs to be positive')
        try:
            numbytes = int(numbytes)
        except ValueError:
            try:
                self.conn.close()
                self.sock.close()
            except socket.error:
                self.sock = None
                self.conn = None
            raise TcpSocketError('max_recv_bytes must be an integer')
        self.max_recv_bytes = numbytes
