import unittest
from unittest.mock import patch, Mock
from joystick import joystick
from sockets.tcpsocket import TcpSocket, TcpSocketError

class TestJoystick(unittest.TestCase):

    def setUp(self):
        self.testjstick = joystick.Joystick()

    def tearDown(self):
        pass

    def test_init(self):
        testjstick2 = joystick.Joystick()
        self.assertEqual(testjstick2.state, joystick.ConnState.CLOSED)
        self.assertIsNone(testjstick2.socket)

    def test_connect_closed(self):
        self.testjstick.state = joystick.ConnState.CLOSED
        self.mock_tcpsock = Mock(spec_set=TcpSocket)
        with patch('joystick.joystick.TcpSocket') as self.mock_tcpsock:
            self.testjstick.connect(9700)
            self.mock_tcpsock.assert_called_with(9700)
            self.mock_tcpsock.return_value.set_max_recv_bytes.\
            assert_called_with(1024)
            self.mock_tcpsock.return_value.wait_for_connection.\
            assert_called_with()
        self.assertEqual(self.testjstick.state, joystick.ConnState.READY)

    def test_connect_closed_bad_port(self):
        self.testjstick.state = joystick.ConnState.CLOSED
        with self.assertRaises(joystick.JoystickError):
            self.testjstick.connect('string')
        with self.assertRaises(joystick.JoystickError):
            self.testjstick.connect(-5)
        with self.assertRaises(joystick.JoystickError):
            self.testjstick.connect(4400.5)
        self.assertEqual(self.testjstick.state,joystick.ConnState.CLOSED)
        self.assertIsNone(self.testjstick.socket)

    def test_connect_closed_tcp_create_error(self):
        self.testjstick.disconnect_internal = method_call_logger(\
        self.testjstick.disconnect_internal)
        self.testjstick.state = joystick.ConnState.CLOSED
        self.mock_tcpsock = Mock(spec_set=TcpSocket)
        with patch('joystick.joystick.TcpSocket') as self.mock_tcpsock:
            self.mock_tcpsock.side_effect = TcpSocketError
            with self.assertRaises(joystick.JoystickError):
                self.testjstick.connect(9700)
            assert(self.testjstick.disconnect_internal.was_called)

    def test_connect_other_state(self):
        self.testjstick.state = joystick.ConnState.RUNNING
        with self.assertRaises(joystick.JoystickError):
            self.testjstick.connect(9700)
        self.assertEqual(self.testjstick.state,joystick.ConnState.RUNNING)
        
        self.testjstick.state = joystick.ConnState.CLOSE_REQUESTED
        with self.assertRaises(joystick.JoystickError):
            self.testjstick.connect(9700)
        self.assertEqual(self.testjstick.state,joystick.ConnState.CLOSE_REQUESTED)
        
        self.testjstick.state = joystick.ConnState.PENDING
        with self.assertRaises(joystick.JoystickError):
            self.testjstick.connect(9700)
        self.assertEqual(self.testjstick.state,joystick.ConnState.PENDING)
        
        self.testjstick.state = joystick.ConnState.READY
        with self.assertRaises(joystick.JoystickError):
            self.testjstick.connect(9700)
        self.assertEqual(self.testjstick.state,joystick.ConnState.READY)

    def test_connect_closed_tcp_wait_error(self):
        self.testjstick.disconnect_internal = method_call_logger(\
        self.testjstick.disconnect_internal)
        self.testjstick.state = joystick.ConnState.CLOSED
        self.mock_tcpsock = Mock(spec_set=TcpSocket)
        with patch('joystick.joystick.TcpSocket') as self.mock_tcpsock:
            self.mock_tcpsock.return_value.wait_for_connection.side_effect =\
                TcpSocketError
            with self.assertRaises(joystick.JoystickError):
                self.testjstick.connect(9700)
            assert(self.testjstick.disconnect_internal.was_called)
        self.assertEqual(self.testjstick.state,joystick.ConnState.CLOSED)

    def test_update_values_ready_state_reply_error(self):
        self.testjstick.disconnect_internal = method_call_logger(\
        self.testjstick.disconnect_internal)
        self.testjstick.state = joystick.ConnState.READY
        self.mock_tcpsock = Mock(spec_set=TcpSocket)
        self.testjstick.socket = self.mock_tcpsock.return_value
        self.mock_tcpsock.return_value.read.return_value='40,35'
        self.mock_tcpsock.return_value.reply.side_effect = TcpSocketError
        self.testjstick.update_values()
        assert(self.testjstick.disconnect_internal.was_called)
        self.mock_tcpsock.return_value.reply.assert_called_with('ACK')
        self.assertEqual(self.testjstick.get_xval(),40)
        self.assertEqual(self.testjstick.get_yval(),35)

    def test_update_values_ready_state_reply_error2(self):
        self.testjstick.xval = 42
        self.testjstick.yval = 12
        self.testjstick.disconnect_internal = method_call_logger(\
        self.testjstick.disconnect_internal)
        self.testjstick.state = joystick.ConnState.READY
        self.mock_tcpsock = Mock(spec_set=TcpSocket)
        self.testjstick.socket = self.mock_tcpsock.return_value
        self.mock_tcpsock.return_value.read.return_value='101,35'
        self.mock_tcpsock.return_value.reply.side_effect = TcpSocketError
        self.testjstick.update_values()
        assert(self.testjstick.disconnect_internal.was_called)
        self.mock_tcpsock.return_value.reply.assert_called_with('ERR:RANGE')
        self.assertEqual(self.testjstick.get_xval(),42)
        self.assertEqual(self.testjstick.get_yval(),12)

    def test_update_values_ready_state_non_int_read(self):
        self.testjstick.disconnect_internal = method_call_logger(\
        self.testjstick.disconnect_internal)
        self.testjstick.state = joystick.ConnState.READY
        self.mock_tcpsock = Mock(spec_set=TcpSocket)
        self.testjstick.socket = self.mock_tcpsock.return_value
        self.mock_tcpsock.return_value.read.return_value='yoyo'
        self.testjstick.update_values()
        assert(self.testjstick.disconnect_internal.was_called)

    def test_update_values_ready_state_non_int_read2(self):
        self.testjstick.disconnect_internal = method_call_logger(\
        self.testjstick.disconnect_internal)
        self.testjstick.state = joystick.ConnState.READY
        self.mock_tcpsock = Mock(spec_set=TcpSocket)
        self.testjstick.socket = self.mock_tcpsock.return_value
        self.mock_tcpsock.return_value.read.return_value='12.2,45.8'
        self.testjstick.update_values()
        assert(self.testjstick.disconnect_internal.was_called)

    def test_update_values_ready_state_read_error(self):
        self.testjstick.disconnect_internal = method_call_logger(\
        self.testjstick.disconnect_internal)
        self.testjstick.state = joystick.ConnState.READY
        self.mock_tcpsock = Mock(spec_set=TcpSocket)
        self.testjstick.socket = self.mock_tcpsock.return_value
        self.mock_tcpsock.return_value.read.side_effect = TcpSocketError
        self.testjstick.update_values()
        assert(self.testjstick.disconnect_internal.was_called)

    def test_update_values_other_state(self):
        self.testjstick.xval = 42
        self.testjstick.yval = 13
        self.testjstick.disconnect_internal = method_call_logger(\
        self.testjstick.disconnect_internal)
        self.testjstick.state = joystick.ConnState.CLOSED
        self.testjstick.update_values()
        assert(not self.testjstick.disconnect_internal.was_called)
        self.assertEqual(self.testjstick.get_xval(),42)
        self.assertEqual(self.testjstick.get_yval(),13)

        self.testjstick.state = joystick.ConnState.CLOSE_REQUESTED
        self.mock_tcpsock = Mock(spec_set=TcpSocket)
        self.testjstick.socket = self.mock_tcpsock.return_value
        self.testjstick.update_values()
        assert(self.testjstick.disconnect_internal.was_called)

        self.testjstick.state = 'Some random thing'
        self.mock_tcpsock = Mock(spec_set=TcpSocket)
        self.testjstick.socket = self.mock_tcpsock.return_value
        self.testjstick.update_values()
        assert(self.testjstick.disconnect_internal.was_called)

    def test_disconnect_internal(self):
        self.testjstick.state = joystick.ConnState.CLOSE_REQUESTED
        self.mock_tcpsock = Mock(spec_set=TcpSocket)
        self.testjstick.socket = self.mock_tcpsock.return_value
        self.testjstick.disconnect_internal()
        self.assertEqual(self.testjstick.state, joystick.ConnState.CLOSED)
        self.assertIsNone(self.testjstick.socket)
 
class method_call_logger(object):
    def __init__(self, meth):
        self.meth = meth
        self.was_called = False

    def __call__(self, code=None):
        self.meth()
        self.was_called = True      

            
    
