import socket
import select

class TcpSocketError(Exception):
    '''Exception class that will be raised by TcpSocket class.'''
    pass

class TcpSocket:
    '''Wrapper around Python socket API. To be used as a server socket.'''
    max_recv_bytes = 128
    
    def __init__(self, port):
        '''Set up a server socket that listens for one connection on port. 
        Create a socketpair to enable the user to unblock read() from outside'''
        self.sock = None
        self.conn = None
        try:
            port_int = int(port)
            if float(port) - port_int > 0:
                raise ValueError
            assert port_int > 1000,"Port number needs to be an integer larger than 1000."
        except (ValueError, AssertionError) as e:
            raise TcpSocketError(str(e))
        self.disconn_listener, self.disconn_sender = socket.socketpair()
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.setblocking(1)
            self.sock.bind(('', port_int))
            self.sock.listen(1)
        except (socket.error, OverflowError, TypeError) as e:
            self.close()
            raise TcpSocketError(str(e))
        
    def wait_for_connection(self):
        '''Block until a connection is made from outside.'''
        if self.sock is not None:
            inputs = [self.sock, self.disconn_listener]
            try:
                readable,_,_ = select.select(inputs,[],[])
            except OSError as e:
                self.close()
                raise TcpSocketError(str(e))
            if self.sock in readable:
                try:
                    self.conn,_ = self.sock.accept()
                except (socket.error, socket.timeout) as e:
                    self.close()
                    raise TcpSocketError(str(e))
            elif self.disconn_listener in readable:
                self.close()
                raise TcpSocketError('Socket closed before connection was made.')
        else:
            self.close()
            raise TcpSocketError('Socket is uninitialised')

    def read(self):
        '''Block until self.max_recv_bytes or less is received.'''
        if self.conn is not None:
            # select() checks conn for data, and disconn_listener for
            # a disconnect request (sent through disconn_sender).
            inputs = [self.conn, self.disconn_listener]
            try:
                readable,_,_ = select.select(inputs,[],[])
            except OSError as e: # bad file descriptor
                self.close()
                raise TcpSocketError(str(e))
            if self.conn in readable:
                try:
                    data = self.conn.recv(self.max_recv_bytes)
                except (socket.error, socket.timeout,OSError) as e:
                    self.close()
                    raise TcpSocketError(str(e))
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
            raise TcpSocketError('Socket is uninitialised')

    def reply(self, data):
        '''Write an encoded string to self.conn.'''
        if type(data) is not str:
            self.close()
            raise TcpSocketError('Can only send string data')
        data = str.encode(data + '\n')
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
        '''Close any open socket descriptors. Does not raise exceptions.'''
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
        try:
            if self.disconn_listener is not None:
                self.disconn_listener.close()
            if self.disconn_sender is not None:
                self.disconn_sender.close()
        except socket.error:
            pass
        finally:
            self.disconn_listener = None
            self.disconn_sender = None

    def unblock(self):
        '''Force socket select.select() to return readable on disconn_listener 
to prevent blocking on socket.recv() or socket.accept().'''
        try:
            self.disconn_sender.sendall(str.encode('d'))
        except (OSError): # sockets might be closed (bad file descriptor)
            self.close()
        except AttributeError: # disconn_sender might be None
            pass

    def set_max_recv_bytes(self, numbytes):
        '''Set maximum number of bytes to receive.'''
        try:
            numbytes_int = int(numbytes)
            rem = numbytes-numbytes_int
            if rem > 0:
                raise ValueError
        except ValueError:
            self.close()
            raise TcpSocketError('max_recv_bytes must be an integer')
        if numbytes < 0:
            self.close()
            raise TcpSocketError('max_recv_bytes needs to be positive')
        self.max_recv_bytes = numbytes

    def get_ip_address(self):
        return self.conn.getsockname()
