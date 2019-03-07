import unittest
from unittest.mock import patch, Mock
import interfaces.receiver as recvr
from coreutils.tcpsocket import TcpSocket, TcpSocketError

class RecvrImpl(recvr.Receiver):
    '''An implementation of Receiver.'''
    xval = 0
    yval = 0
    
    def __init__(self):
        recvr.Receiver.__init__(self)
        
    def store_received(self, recvd_list):
        pass


class TestReceiver(unittest.TestCase):

    def setUp(self):
        self.testImpl = RecvrImpl()

    def tearDown(self):
        pass

    def test_init(self):
        testImpl2 = RecvrImpl()
        self.assertEqual(testImpl2.state, recvr.ConnState.CLOSED)
        self.assertIsNone(testImpl2.socket)

    def test_connect_closed(self):
        self.testImpl.state = recvr.ConnState.CLOSED
        self.mock_tcpsock = Mock(spec_set=TcpSocket)
        with patch('interfaces.receiver.TcpSocket') as self.mock_tcpsock:
            self.testImpl.connect(9700)
            self.mock_tcpsock.return_value.set_max_recv_bytes.\
            assert_called_with(1024)
            self.mock_tcpsock.return_value.wait_for_connection.\
            assert_called_with()
        self.assertEqual(self.testImpl.state, recvr.ConnState.READY)

    def test_connect_closed_bad_port(self):
        self.testImpl.state = recvr.ConnState.CLOSED
        with self.assertRaises(recvr.ReceiverError):
            self.testImpl.connect('string')
        with self.assertRaises(recvr.ReceiverError):
            self.testImpl.connect(-5)
        with self.assertRaises(recvr.ReceiverError):
            self.testImpl.connect(4400.5)
        self.assertEqual(self.testImpl.state, recvr.ConnState.CLOSED)
        self.assertIsNone(self.testImpl.socket)

    def test_connect_closed_tcp_create_error(self):
        self.testImpl.disconnect_internal = method_call_logger(\
        self.testImpl.disconnect_internal)
        self.testImpl.state = recvr.ConnState.CLOSED
        self.mock_tcpsock = Mock(spec_set=TcpSocket)
        with patch('interfaces.receiver.TcpSocket') as self.mock_tcpsock:
            self.mock_tcpsock.side_effect = TcpSocketError
            with self.assertRaises(recvr.ReceiverError):
                self.testImpl.connect(9700)
            assert(self.testImpl.disconnect_internal.was_called)

    def test_connect_other_state(self):
        self.testImpl.state = recvr.ConnState.RUNNING
        with self.assertRaises(recvr.ReceiverError):
            self.testImpl.connect(9700)
        self.assertEqual(self.testImpl.state, recvr.ConnState.RUNNING)
        
        self.testImpl.state = recvr.ConnState.CLOSE_REQUESTED
        with self.assertRaises(recvr.ReceiverError):
            self.testImpl.connect(9700)
        self.assertEqual(self.testImpl.state, recvr.ConnState.CLOSE_REQUESTED)
        
        self.testImpl.state = recvr.ConnState.PENDING
        with self.assertRaises(recvr.ReceiverError):
            self.testImpl.connect(9700)
        self.assertEqual(self.testImpl.state, recvr.ConnState.PENDING)
        
        self.testImpl.state = recvr.ConnState.READY
        with self.assertRaises(recvr.ReceiverError):
            self.testImpl.connect(9700)
        self.assertEqual(self.testImpl.state, recvr.ConnState.READY)

    def test_connect_closed_tcp_wait_error(self):
        self.testImpl.disconnect_internal = method_call_logger(\
        self.testImpl.disconnect_internal)
        self.testImpl.state = recvr.ConnState.CLOSED
        self.mock_tcpsock = Mock(spec_set=TcpSocket)
        with patch('interfaces.receiver.TcpSocket') as self.mock_tcpsock:
            self.mock_tcpsock.return_value.wait_for_connection.side_effect =\
                TcpSocketError
            with self.assertRaises(recvr.ReceiverError):
                self.testImpl.connect(9700)
            assert(self.testImpl.disconnect_internal.was_called)
        self.assertEqual(self.testImpl.state, recvr.ConnState.CLOSED)

    def test_update_values_ready_state_reply_error(self):
        self.testImpl.disconnect_internal = method_call_logger(\
        self.testImpl.disconnect_internal)
        self.testImpl.state = recvr.ConnState.READY
        self.mock_tcpsock = Mock(spec_set=TcpSocket)
        mock_store_received = Mock()
        self.testImpl.socket = self.mock_tcpsock.return_value
        self.testImpl.store_received = mock_store_received
        self.mock_tcpsock.return_value.read.return_value = '40,35'
        self.mock_tcpsock.return_value.reply.side_effect = TcpSocketError
        self.testImpl.update_values()
        self.testImpl.store_received.assert_called_with(['40','35'])
        assert(self.testImpl.disconnect_internal.was_called)

    def test_update_values_ready_state_non_int_read(self):
        self.testImpl.disconnect_internal = method_call_logger(\
        self.testImpl.disconnect_internal)
        self.testImpl.state = recvr.ConnState.READY
        self.mock_tcpsock = Mock(spec_set=TcpSocket)
        self.testImpl.socket = self.mock_tcpsock.return_value
        self.mock_tcpsock.return_value.read.return_value='yoyo'
        self.testImpl.update_values()
        assert(self.testImpl.disconnect_internal.was_called)

    def test_update_values_ready_state_non_int_read2(self):
        self.testImpl.disconnect_internal = method_call_logger(\
        self.testImpl.disconnect_internal)
        self.testImpl.state = recvr.ConnState.READY
        self.mock_tcpsock = Mock(spec_set=TcpSocket)
        self.testImpl.socket = self.mock_tcpsock.return_value
        self.mock_tcpsock.return_value.read.return_value='12.2,45.8'
        self.testImpl.update_values()
        assert(self.testImpl.disconnect_internal.was_called)

    def test_update_values_ready_state_read_error(self):
        self.testImpl.disconnect_internal = method_call_logger(\
        self.testImpl.disconnect_internal)
        self.testImpl.state = recvr.ConnState.READY
        self.mock_tcpsock = Mock(spec_set=TcpSocket)
        self.testImpl.socket = self.mock_tcpsock.return_value
        self.mock_tcpsock.return_value.read.side_effect = TcpSocketError
        self.testImpl.update_values()
        assert(self.testImpl.disconnect_internal.was_called)

    def test_update_values_other_state(self):
        self.testImpl.disconnect_internal = method_call_logger(\
        self.testImpl.disconnect_internal)
        self.testImpl.state = recvr.ConnState.CLOSED
        self.testImpl.update_values()
        assert (not self.testImpl.disconnect_internal.was_called)

        self.testImpl.state = recvr.ConnState.CLOSE_REQUESTED
        self.mock_tcpsock = Mock(spec_set = TcpSocket)
        self.testImpl.socket = self.mock_tcpsock.return_value
        self.testImpl.update_values()
        assert(self.testImpl.disconnect_internal.was_called)

    def test_disconnect_internal(self):
        self.testImpl.state = recvr.ConnState.CLOSE_REQUESTED
        self.mock_tcpsock = Mock(spec_set=TcpSocket)
        self.testImpl.socket = self.mock_tcpsock.return_value
        self.testImpl.disconnect_internal()
        self.assertEqual(self.testImpl.state, recvr.ConnState.CLOSED)
        self.assertIsNone(self.testImpl.socket)


class method_call_logger(object):
    def __init__(self, meth):
        self.meth = meth
        self.was_called = False

    def __call__(self, code=None):
        self.meth()
        self.was_called = True                
