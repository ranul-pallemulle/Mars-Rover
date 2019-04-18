import coreutils.configure as cfg
from coreutils.diagnostics import Diagnostics as dg
from coreutils.tcpsocket import TcpSocket, TcpSocketError

''' Utilities for multiprocessing through attached units. '''
class OffloadError(Exception):
    pass

def register_name(unitname):
    if not cfg.Configuration.ready():
        raise OffloadError("Settings file not parsed.")
    dg.print("Registering unit {}...".format(unitname))
    
class OffloadSocket:
    max_bytes = 128

    def __init__(self, port):
        self.sock = None
        self.conn = None
        self.disconn_listener, self.disconn_sender = socket.socketpair()
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.setblocking(1)
        except (socket.error, OverflowError, TypeError) as e:
            self.close()
            raise OffloadError(str(e))

    def connect(self):
        pass
