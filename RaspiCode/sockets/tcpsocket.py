import socket

class TcpSocketError(Exception):
    '''Exception class that will be raised by TcpSocket class.'''
    pass

class TcpSocket:
    '''Wrapper around Python socket API. To be used as a server socket.'''
    sock = None
    conn = None
    max_recv_bytes = 128
    
    def __init__(self, port):
        '''Set up a server socket that listens for one connection on port.'''
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.setblocking(1)
            self.sock.bind(('', port))
            self.sock.listen(1)
        except socket.error as e:
            self.close()
            raise TcpSocketError(str(e))
        
    def wait_for_connection(self):
        '''Block until a connection is made from outside.'''
        if self.sock is not None:
            try:
                self.conn,_ = self.sock.accept()
            except (socket.error, socket.timeout) as e:
                self.close()
                raise TcpSocketError(str(e))
        else:
            self.close()
            raise TcpSocketError('Socket is uninitialised')

    def read(self):
        '''Block until self.max_recv_bytes or less is received.'''
        if self.conn is not None:
            try:
                data = self.conn.recv(self.max_recv_bytes)
            except (socket.error, socket.timeout,OSError) as e:
                self.close()
                raise TcpSocketError(str(e))
            if len(data) == 0:
                self.close()
                raise TcpSocketError("Connection lost")
            data = data.decode()
            return data
        else:
            self.close()
            raise TcpSocketError('Socket is uninitialised')

    def reply(self, data):
        '''Write data to self.conn.'''
        if self.conn is not None:
            try:
               self.conn.sendall(data)
            except (socket.error, socket.timeout,OSError) as e:
                self.close()
                raise TcpSocketError(str(e))
        else:
            self.close()
            raise TcpSocketError('Socket is uninitialised')

    def close(self):
        '''Close any open socket descriptors.'''
        if self.conn is not None:
            try:
                self.conn.close()
            except socket.error:
                pass
            finally:
                self.conn = None
        if self.sock is not None:
            try:
                self.sock.close()
            except socket.error:
                pass
            finally:
                self.sock = None                

    def set_max_recv_bytes(self, numbytes):
        '''Set maximum number of bytes to receive.'''
        try:
            numbytes = int(numbytes)
        except ValueError:
            self.close()
            raise TcpSocketError('max_recv_bytes must be an integer')
        if numbytes < 0:
            self.close()
            raise TcpSocketError('max_recv_bytes needs to be positive')
        self.max_recv_bytes = numbytes
