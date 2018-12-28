import unittest
from unittest.mock import patch, Mock
from interfaces.receiver import ConnState, ReceiverError
from robotic_arm import arm
from coreutils.tcpsocket import TcpSocket, TcpSocketError

class TestArm(unittest.TestCase):

    @patch('coreutils.resource_manager')
    def setUp(self, mock_mgr):
        self.testarm = arm.RoboticArm(mock_mgr)

    def test_store_received(self):
        recvd_list = [120, 180, 90]
        ret = self.testarm.store_received(recvd_list)
        self.assertEqual(ret, 'ACK')
        vals = self.testarm.get_values(None)
        self.assertEqual(vals, (120, 180, 90))
        recvd_list = [200, 180, 20]
        ret = self.testarm.store_received(recvd_list)
        self.assertEqual(ret, 'ERR:RANGE')
        recvd_list = [20, 30, 50 , 180]
        ret = self.testarm.store_received(recvd_list)
        self.assertEqual(ret, None)
        recvd_list = [10]
        ret = self.testarm.store_received(recvd_list)
        self.assertEqual(ret, None)
        recvd_list = ['blabla', 'bla']
        ret = self.testarm.store_received(recvd_list)
        self.assertEqual(ret, None)

class method_call_logger:
    def __init__(self, meth):
        self.meth = meth
        self.was_called = False

    def __call__(self, code=None):
        self.meth()
        self.was_called = True
