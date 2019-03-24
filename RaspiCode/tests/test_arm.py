import unittest
from unittest.mock import patch, Mock
from interfaces.receiver import ConnState, ReceiverError
from robotic_arm import arm
from coreutils.tcpsocket import TcpSocket, TcpSocketError

class TestArm(unittest.TestCase):

    @patch('coreutils.resource_manager')
    def setUp(self, mock_mgr):
        self.testarm = arm.RoboticArm()

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

    def test_get_values(self):
        vals = self.testarm.get_values(None)
        self.assertEqual(vals, (0,0,0))
        self.testarm.angle_1 = 5
        self.testarm.angle_2 = 10
        self.testarm.angle_3 = 20
        vals = self.testarm.get_values(None)
        self.assertEqual(vals, (5,10,20))

    def test_start(self):
        self.testarm.begin_receive = method_call_logger(self.testarm.begin_receive)
        self.testarm.begin_actuate = method_call_logger(self.testarm.begin_actuate)
        self.testarm.have_acquired = method_call_logger(self.testarm.have_acquired)
        self.testarm.stop = method_call_logger(self.testarm.stop)
        self.testarm.acquire_motors = method_call_logger(self.testarm.acquire_motors)

        self.testarm.have_acquired.set_return_value(False)

        self.testarm.controller_lock = Mock()
        
        self.testarm.start()

        assert(self.testarm.begin_receive.was_called)
        assert(self.testarm.acquire_motors.was_called)
        assert(self.testarm.have_acquired.was_called)
        assert(self.testarm.stop.was_called)
        assert(not self.testarm.begin_actuate.was_called)


        self.testarm.begin_receive = method_call_logger(self.testarm.begin_receive)
        self.testarm.begin_actuate = method_call_logger(self.testarm.begin_actuate)
        self.testarm.have_acquired = method_call_logger(self.testarm.have_acquired)
        self.testarm.stop = method_call_logger(self.testarm.stop)
        self.testarm.acquire_motors = method_call_logger(self.testarm.acquire_motors)

        self.testarm.have_acquired.set_return_value(True)

        self.testarm.start()

        assert(self.testarm.begin_receive.was_called)
        assert(self.testarm.acquire_motors.was_called)
        assert(self.testarm.have_acquired.was_called)
        assert(not self.testarm.stop.was_called)
        assert(self.testarm.begin_actuate.was_called)

    def test_stop(self):
        self.testarm.have_acquired = method_call_logger(self.testarm.have_acquired)
        self.testarm.release_motors = method_call_logger(self.testarm.release_motors)
        self.testarm.disconnect = method_call_logger(self.testarm.disconnect)
        self.testarm.is_running = method_call_logger(self.testarm.is_running)
        self.testarm.connection_active = method_call_logger(self.testarm.connection_active)

        self.testarm.is_running.set_return_value(True)
        self.testarm.have_acquired.set_return_value(True)
        self.testarm.connection_active.set_return_value(True)

        self.testarm.stop()

        assert(self.testarm.release_motors.was_called)
        assert(self.testarm.disconnect.was_called)

        self.testarm.have_acquired = method_call_logger(self.testarm.have_acquired)
        self.testarm.release_motors = method_call_logger(self.testarm.release_motors)
        self.testarm.disconnect = method_call_logger(self.testarm.disconnect)

        self.testarm.have_acquired.set_return_value(False)

        self.testarm.stop()

        assert(not self.testarm.release_motors.was_called)
        assert(self.testarm.disconnect.was_called)
        
        
class method_call_logger:
    def __init__(self, meth):
        self.meth = meth
        self.was_called = False
        self.side_effect = None
        self.return_value = None

    def __call__(self, code=None):
        # self.meth()
        self.was_called = True
        if self.side_effect is not None:
            self.side_effect()
        if self.return_value is not None:
            return self.return_value

    def set_side_effect(self, sideeff):
        self.side_effect = sideeff

    def set_return_value(self, retval):
        self.return_value = retval
