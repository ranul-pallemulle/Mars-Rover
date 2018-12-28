import unittest
from unittest.mock import patch, Mock
from interfaces.receiver import ConnState, ReceiverError
from joystick import joystick
from coreutils.tcpsocket import TcpSocket, TcpSocketError

class TestJoystick(unittest.TestCase):
    
    @patch('coreutils.resource_manager')
    def setUp(self, mock_mgr):
        self.testjstick = joystick.Joystick(mock_mgr)

    def test_store_received(self):
        recvd_list = [40,75]
        ret = self.testjstick.store_received(recvd_list)
        self.assertEqual(ret, 'ACK')
        vals = self.testjstick.get_values(None)
        self.assertEqual(vals, (40,75))
        recvd_list = [120,40]
        ret = self.testjstick.store_received(recvd_list)
        self.assertEqual(ret, 'ERR:RANGE')
        recvd_list = [20,30,40]
        ret = self.testjstick.store_received(recvd_list)
        self.assertEqual(ret, None)
        recvd_list = [10]
        ret = self.testjstick.store_received(recvd_list)
        self.assertEqual(ret, None)
        recvd_list = ['blabla','bla']
        ret = self.testjstick.store_received(recvd_list)
        self.assertEqual(ret, None)
        
        
class method_call_logger(object):
    def __init__(self, meth):
        self.meth = meth
        self.was_called = False

    def __call__(self, code=None):
        self.meth()
        self.was_called = True      

            
    
