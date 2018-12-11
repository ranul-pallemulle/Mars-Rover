import unittest
from unittest.mock import patch, Mock
import socket
import select
from sockets import tcpsocket
from threading import Thread

class TestTcpSocket(unittest.TestCase):

    def setUp(self):
        self.mock_sock = Mock(spec_set=socket.socket)
        with patch('socket.socket') as self.mock_sock:
            self.testtcp = tcpsocket.TcpSocket(5560)
         
    def tearDown(self):
        pass

    def test_init(self):
        self.mock_sock = Mock(spec_set=socket.socket)
        with patch('socket.socket') as self.mock_sock:
            testtcp2 = tcpsocket.TcpSocket(4560)
            self.mock_sock.return_value.setblocking.assert_called_with(1)
            self.mock_sock.return_value.bind.assert_called_with(('',4560))
            self.assertIsNotNone(testtcp2.sock)

    @patch('socket.socket')
    def test_init_addr_in_use(self,mocked_socket):
#        self.mock_sock = Mock(spec_set=socket.socket)
        mocked_socket.return_value.bind.side_effect = OverflowError
        with self.assertRaises(tcpsocket.TcpSocketError):
            testtcp2 = tcpsocket.TcpSocket(4560)
            self.assertIsNone(testtcp2.sock)

    def test_init_bad_port(self):
        with self.assertRaises(tcpsocket.TcpSocketError):
            testtcp2 = tcpsocket.TcpSocket('something')
            self.assertIsNone(testtcp2.sock)
        with self.assertRaises(tcpsocket.TcpSocketError):
            testtcp2 = tcpsocket.TcpSocket(12.5)
            self.assertIsNone(testtcp2.sock)            
        with self.assertRaises(tcpsocket.TcpSocketError):
            testtcp2 = tcpsocket.TcpSocket(-4)
            self.assertIsNone(testtcp2.sock)            

    @patch('sockets.tcpsocket.select.select')
    def test_wait_for_connection_accept_error(self,mock_select):
        self.mock_sock.return_value.accept.return_value = Mock(),Mock()
        self.mock_sock.return_value.accept.side_effect = socket.error
        self.testtcp.close = method_call_logger(self.testtcp.close)
        assert(not self.testtcp.close.was_called)
        self.assertIsNotNone(self.testtcp.sock)
        mock_select.return_value = [[self.testtcp.sock],[],[]]
        with patch('socket.socket') as self.mock_sock:
            with self.assertRaises(tcpsocket.TcpSocketError):
                self.testtcp.wait_for_connection()
            assert(self.testtcp.close.was_called)
            self.assertIsNone(self.testtcp.sock)

    @patch('sockets.tcpsocket.select.select')
    def test_wait_for_connecton_disconn(self,mock_select):
        self.testtcp.close = method_call_logger(self.testtcp.close)
        assert(not self.testtcp.close.was_called)
        self.assertIsNotNone(self.testtcp.sock)
        self.testtcp.disconn_listener = Mock(spec_set=socket.socket)
        mock_select.return_value = [[self.testtcp.disconn_listener],[],[]]
        with self.assertRaises(tcpsocket.TcpSocketError):
            self.testtcp.wait_for_connection()
        assert(self.testtcp.close.was_called)
        self.assertIsNone(self.testtcp.sock)

    def test_wait_for_connection_sock_none(self):
        self.mock_sock.return_value.accept.return_value = Mock(),Mock()
        self.testtcp.close = method_call_logger(self.testtcp.close)
        assert(not self.testtcp.close.was_called)
        self.assertIsNotNone(self.testtcp.sock)
        self.testtcp.sock = None
        with self.assertRaises(tcpsocket.TcpSocketError):
            self.testtcp.wait_for_connection()
        assert(self.testtcp.close.was_called)
        self.assertIsNone(self.testtcp.sock)

    @patch('sockets.tcpsocket.select.select')
    def test_read(self,mock_select):
        self.testtcp.close = method_call_logger(self.testtcp.close)
        self.mock_conn = Mock(spec_set=socket.socket)
        self.mock_conn.return_value.recv.return_value = str.encode('19')
        self.testtcp.conn = self.mock_conn.return_value
        mock_select.return_value = [[self.testtcp.conn],[],[]]
        self.assertEqual(self.testtcp.read(),'19')
        assert(not self.testtcp.close.was_called)
        self.assertIsNotNone(self.testtcp.sock)
        self.assertIsNotNone(self.testtcp.conn)

    @patch('sockets.tcpsocket.select.select')
    def test_read_EOF(self,mock_select):
        self.mock_conn = Mock(spec_set=socket.socket)
        self.mock_conn.return_value.recv.return_value = str.encode('')
        self.testtcp.conn = self.mock_conn.return_value
        self.testtcp.close = method_call_logger(self.testtcp.close)
        mock_select.return_value = [[self.testtcp.conn],[],[]]
        assert(not self.testtcp.close.was_called)
        self.assertIsNotNone(self.testtcp.conn)
        self.assertEqual(self.testtcp.read(), None)
        assert(self.testtcp.close.was_called)
        self.assertIsNone(self.testtcp.sock)
        self.assertIsNone(self.testtcp.conn)

    @patch('sockets.tcpsocket.select.select')
    def test_read_disconn(self,mock_select):
        self.testtcp.conn = Mock()
        mock_select.return_value = [[self.testtcp.disconn_listener],[],[]]
        self.testtcp.close = method_call_logger(self.testtcp.close)
        assert(not self.testtcp.close.was_called)
        self.assertIsNotNone(self.testtcp.conn)
        self.assertEqual(self.testtcp.read(), None)
        assert(self.testtcp.close.was_called)
        self.assertIsNone(self.testtcp.sock)
        self.assertIsNone(self.testtcp.conn)
        
    @patch('sockets.tcpsocket.select.select')
    def test_read_recv_error(self,mock_select):
        self.mock_conn = Mock(spec_set=socket.socket)
        self.mock_conn.return_value.recv.return_value = str.encode('19')
        self.mock_conn.return_value.recv.side_effect = OSError
        self.testtcp.conn = self.mock_conn.return_value
        mock_select.return_value = [[self.testtcp.conn],[],[]]
        self.testtcp.close = method_call_logger(self.testtcp.close)
        assert(not self.testtcp.close.was_called)
        self.assertIsNotNone(self.testtcp.sock)
        self.assertIsNotNone(self.testtcp.conn)

        with self.assertRaises(tcpsocket.TcpSocketError):
            self.testtcp.read()
        assert(self.testtcp.close.was_called)
        self.assertIsNone(self.testtcp.sock)
        self.assertIsNone(self.testtcp.conn)

    def test_read_conn_none(self):
        self.testtcp.conn = None
        self.testtcp.close = method_call_logger(self.testtcp.close)
        assert(not self.testtcp.close.was_called)
        self.assertIsNotNone(self.testtcp.sock)

        with self.assertRaises(tcpsocket.TcpSocketError):
            self.testtcp.read()
        assert(self.testtcp.close.was_called)
        self.assertIsNone(self.testtcp.sock)
        self.assertIsNone(self.testtcp.conn)

    def test_reply(self):
        self.mock_conn = Mock(spec_set=socket.socket)
        self.testtcp.conn = self.mock_conn.return_value
        self.testtcp.close = method_call_logger(self.testtcp.close)
        self.testtcp.reply('12')
        self.testtcp.conn.sendall.assert_called_with(str.encode('12'))
        assert(not self.testtcp.close.was_called)
        self.assertIsNotNone(self.testtcp.sock)
        self.assertIsNotNone(self.testtcp.conn)

        self.mock_conn.return_value.sendall.side_effect = OSError
        self.testtcp.conn = self.mock_conn.return_value
        self.testtcp.close = method_call_logger(self.testtcp.close)
        with self.assertRaises(tcpsocket.TcpSocketError):
            self.testtcp.reply('12')
        assert(self.testtcp.close.was_called)
        self.assertIsNone(self.testtcp.sock)
        self.assertIsNone(self.testtcp.conn)

    def test_reply_non_string(self):
        self.mock_conn = Mock(spec_set=socket.socket)
        self.testtcp.conn = self.mock_conn.return_value
        self.testtcp.close = method_call_logger(self.testtcp.close)
        with self.assertRaises(tcpsocket.TcpSocketError):
            self.testtcp.reply(12)
        assert(self.testtcp.close.was_called)
        self.assertIsNone(self.testtcp.sock)
        self.assertIsNone(self.testtcp.conn)

    def test_reply_conn_none(self):
        self.testtcp.conn = None
        self.testtcp.close = method_call_logger(self.testtcp.close)
        assert(not self.testtcp.close.was_called)
        self.assertIsNotNone(self.testtcp.sock)
        with self.assertRaises(tcpsocket.TcpSocketError):
            self.testtcp.reply('12')
        assert(self.testtcp.close.was_called)
        self.assertIsNone(self.testtcp.sock)
        self.assertIsNone(self.testtcp.conn)

    def test_close(self):
        self.mock_conn = Mock(spec_set=socket.socket)
        self.testtcp.conn = self.mock_conn.return_value

        self.assertIsNotNone(self.testtcp.sock)
        self.testtcp.close()
        self.assertIsNone(self.testtcp.conn)
        self.assertIsNone(self.testtcp.sock)

    def test_close_with_error(self):
        self.mock_conn = Mock(spec_set=socket.socket)
        self.mock_conn.return_value.close.side_effect = socket.error
        self.testtcp.conn = self.mock_conn.return_value
        self.assertIsNotNone(self.testtcp.sock)
        self.testtcp.close()
        self.assertIsNone(self.testtcp.conn)
        self.assertIsNone(self.testtcp.sock)

    def test_set_max_recv_bytes_double_input(self):
        self.testtcp.close = method_call_logger(self.testtcp.close)
        assert(not self.testtcp.close.was_called)
        self.assertIsNotNone(self.testtcp.sock)
        try:
            self.testtcp.set_max_recv_bytes(12)
        except Exception:
            self.fail('Exception in a valid case')
        assert(not self.testtcp.close.was_called)
        self.assertEqual(self.testtcp.max_recv_bytes,12)

        with self.assertRaises(tcpsocket.TcpSocketError):
            self.testtcp.set_max_recv_bytes(12.00001)
        assert(self.testtcp.close.was_called)
        self.assertIsNone(self.testtcp.sock)
        self.assertIsNone(self.testtcp.conn)

    def test_set_max_recv_bytes_invalid_input(self):
        self.testtcp.close = method_call_logger(self.testtcp.close)
        assert(not self.testtcp.close.was_called)
        self.assertIsNotNone(self.testtcp.sock)
        with self.assertRaises(tcpsocket.TcpSocketError):
            self.testtcp.set_max_recv_bytes('Hello')
        assert(self.testtcp.close.was_called)
        self.assertIsNone(self.testtcp.sock)
        self.assertIsNone(self.testtcp.conn)

    def test_set_max_recv_bytes_neg_input(self):
        self.testtcp.close = method_call_logger(self.testtcp.close)
        assert(not self.testtcp.close.was_called)
        self.assertIsNotNone(self.testtcp.sock)
        with self.assertRaises(tcpsocket.TcpSocketError):
            self.testtcp.set_max_recv_bytes(-12)
        assert(self.testtcp.close.was_called)
        self.assertIsNone(self.testtcp.sock)
        self.assertIsNone(self.testtcp.conn)

    def test_concurrent_access(self):
        real_tcp = tcpsocket.TcpSocket(4580)
        thread = Thread(target=real_tcp.wait_for_connection,args=())
        thread.start()
        real_tcp.unblock()
        thread.join()
        self.assertIsNone(real_tcp.sock)
        self.assertIsNone(real_tcp.conn)

class method_call_logger(object):
    def __init__(self, meth):
        self.meth = meth
        self.was_called = False

    def __call__(self, code=None):
        self.meth()
        self.was_called = True                
