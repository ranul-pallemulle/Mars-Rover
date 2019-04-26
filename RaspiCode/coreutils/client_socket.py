import socket
import select

class ClientSocketError(Exception):
    '''Exception class that will be raised by ClientSocket class.'''
    pass

class ClientSocket:
    '''Wrapper around Python socket API. To be used as a client socket.'''
    max_recv_bytes = 128
    
    def __init__(self):
        '''Set up a server socket that listens for one connection on port. 
        Create a socketpair to enable the user to unblock read() from outside'''
        self.sock = None
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setblocking(1)
            self.disconn_listener, self.disconn_sender = socket.socketpair()            
        except (socket.error) as e:
            self.close()
            raise ClientSocketError(str(e))

    def connect(self, ip_addr, port):
        '''Connect to a server specified by ip address and port number.'''
        try:
            port_int = int(port)
            assert float(port) - port_int > 0, 'Port number needs to be an integer.'
            assert isinstance(ip_addr, str)
        except (ValueError, AssertionError) as e:
            self.close()
            raise ClientSocketError(str(e))
        if self.sock is not None:
            self.sock.connect((ip_addr, port))
        else:
            self.close()
            raise ClientSocketError('Socket is uninitialised.')
            

    def read(self):
        '''Block until self.max_recv_bytes or less is received.'''
        if self.sock is not None:
            # select() checks sock for data, and disconn_listener for
            # a disconnect request (sent through disconn_sender).
            inputs = [self.sock, self.disconn_listener]
            readable,_,_ = select.select(inputs,[],[])
            if self.sock in readable:
                try:
                    data = self.sock.recv(self.max_recv_bytes)
                except (socket.error, socket.timeout,OSError) as e:
                    self.close()
                    raise ClientSocketError(str(e))
            elif self.disconn_listener in readable:
                self.close()
                return None
            if len(data) == 0:
                self.close()
                return None
            data = data.decode()
            return data
        else:
            self.close()
            raise ClientSocketError('Socket is uninitialised')

    def write(self, data):
        '''Write an encoded string to the server.'''
        if type(data) is not str:
            self.close()
            raise ClientSocketError('Can only send string data')
        data = str.encode(data + '\n')
        if self.sock is not None:
            try:
               self.sock.sendall(data)
            except (socket.error, socket.timeout,OSError) as e:
                self.close()
                raise ClientSocketError(str(e))
        else:
            self.close()
            raise ClientSocketError('Socket is uninitialised')

    def close(self):
        '''Close any open socket descriptors. Does not raise exceptions.'''
        if self.sock is not None:
            try:
                self.sock.close()
            except socket.error:
                pass
            finally:
                self.sock = None
        try:
            self.disconn_listener.close()
            self.disconn_sender.close()
        except socket.error:
            pass

    def unblock(self):
        '''Force read() to return with None to indicate broken connection. Should not raise exceptions.'''
        self.disconn_sender.sendall(str.encode('d'))

    def set_max_recv_bytes(self, numbytes):
        '''Set maximum number of bytes to receive.'''
        try:
            numbytes_int = int(numbytes)
            rem = numbytes-numbytes_int
            if rem > 0:
                raise ValueError
        except ValueError:
            self.close()
            raise ClientSocketError('max_recv_bytes must be an integer')
        if numbytes < 0:
            self.close()
            raise ClientSocketError('max_recv_bytes needs to be positive')
        self.max_recv_bytes = numbytes
