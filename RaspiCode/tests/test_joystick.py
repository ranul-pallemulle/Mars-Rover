import unittest
from unittest.mock import patch, Mock
from interfaces.opmode import OpModeError
from interfaces.receiver import ConnState, ReceiverError
from joystick import joystick
from coreutils.tcpsocket import TcpSocket, TcpSocketError

class TestJoystick(unittest.TestCase):
    
    def setUp(self):
        self.testjstick = joystick.Joystick()

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

    def test_get_values(self):
        vals = self.testjstick.get_values(None)
        self.assertEqual(vals, (0,0))
        self.testjstick.xval = 5
        self.testjstick.yval = 10
        vals = self.testjstick.get_values(None)
        self.assertEqual(vals, (5,10))

    def test_start(self):
        self.testjstick.connect = method_call_logger(self.testjstick.connect)
        self.testjstick.begin_receive = method_call_logger(self.testjstick.begin_receive)
        self.testjstick.begin_actuate = method_call_logger(self.testjstick.begin_actuate)
        self.testjstick.have_acquired = method_call_logger(self.testjstick.have_acquired)
        self.testjstick.stop = method_call_logger(self.testjstick.stop)
        self.testjstick.acquire_motors = method_call_logger(self.testjstick.acquire_motors)

        self.testjstick.have_acquired.set_return_value(False)

        self.testjstick.controller_lock = Mock()

        with self.assertRaises(OpModeError):
            self.testjstick.start([5000])

        assert(self.testjstick.connect.was_called)
        assert(self.testjstick.begin_receive.was_called)
        assert(self.testjstick.acquire_motors.was_called)
        assert(self.testjstick.have_acquired.was_called)
        assert(self.testjstick.stop.was_called)
        assert(not self.testjstick.begin_actuate.was_called)


        self.testjstick.begin_receive = method_call_logger(self.testjstick.begin_receive)
        self.testjstick.begin_actuate = method_call_logger(self.testjstick.begin_actuate)
        self.testjstick.have_acquired = method_call_logger(self.testjstick.have_acquired)
        self.testjstick.stop = method_call_logger(self.testjstick.stop)
        self.testjstick.acquire_motors = method_call_logger(self.testjstick.acquire_motors)

        self.testjstick.have_acquired.set_return_value(True)

        self.testjstick.start([5000])

        assert(self.testjstick.begin_receive.was_called)
        assert(self.testjstick.acquire_motors.was_called)
        assert(self.testjstick.have_acquired.was_called)
        assert(not self.testjstick.stop.was_called)
        assert(self.testjstick.begin_actuate.was_called)

    def test_stop(self):
        self.testjstick.have_acquired = method_call_logger(self.testjstick.have_acquired)
        self.testjstick.release_motors = method_call_logger(self.testjstick.release_motors)
        self.testjstick.disconnect = method_call_logger(self.testjstick.disconnect)
        self.testjstick.is_stopped = method_call_logger(self.testjstick.is_stopped)
        self.testjstick.connection_active = method_call_logger(self.testjstick.connection_active)

        self.testjstick.is_stopped.set_return_value(False)
        self.testjstick.have_acquired.set_return_value(True)
        self.testjstick.connection_active.set_return_value(True)

        self.testjstick.stop(None)

        assert(self.testjstick.release_motors.was_called)
        assert(self.testjstick.disconnect.was_called)

        self.testjstick.have_acquired = method_call_logger(self.testjstick.have_acquired)
        self.testjstick.release_motors = method_call_logger(self.testjstick.release_motors)
        self.testjstick.disconnect = method_call_logger(self.testjstick.disconnect)

        self.testjstick.have_acquired.set_return_value(False)

        self.testjstick.stop(None)

        assert(not self.testjstick.release_motors.was_called)
        assert(self.testjstick.disconnect.was_called)
        
        
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
        
