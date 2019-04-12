import unittest
from unittest.mock import patch, Mock
from coreutils.diagnostics import Diagnostics, DiagState, DiagnosticsError
from coreutils.tcpsocket import TcpSocketError
from collections import deque

class TestDiagnostics(unittest.TestCase):

    @patch('coreutils.diagnostics.cfg')
    def test_initialise_not_enabled(self, mock_cfg):
        mock_cfg.overall_config.diagnostics_enabled.return_value = False
        Diagnostics.initialise()
        mock_cfg.overall_config.diagnostics_enabled.assert_called_with()
        mock_cfg.overall_config.diagnostics_port.assert_not_called()

    @patch('coreutils.diagnostics.Thread')
    @patch('coreutils.diagnostics.cfg')
    def test_initialise_enabled(self, mock_cfg, mock_thread):
        mock_cfg.overall_config.diagnostics_enabled.return_value = True
        mock_cfg.overall_config.diagnostics_port.return_value = 5000
        thread = Mock()
        mock_thread.return_value = thread
        Diagnostics.initialise()
        mock_thread.assert_called_with(target=Diagnostics._make_socket_connection, args=[5000])
        thread.start.assert_called_with()

    @patch('coreutils.diagnostics.TcpSocket')
    def test_make_socket_connection(self, mock_socket):
        ms = Mock()
        mock_socket.return_value = ms
        self.assertEqual(Diagnostics.state, DiagState.CLOSED)
        
        Diagnostics._make_socket_connection(5570)
        mock_socket.assert_called_with(5570)
        ms.wait_for_connection.assert_called_with()
        ms.set_max_recv_bytes.assert_called_with(1024)
        self.assertEqual(Diagnostics.state, DiagState.ESTABLISHED)
        Diagnostics.state = DiagState.CLOSED

    @patch('coreutils.diagnostics.TcpSocket')
    def test_make_socket_connection_socket_error(self, mock_socket):
        mock_socket.side_effect = TcpSocketError
        self.assertEqual(Diagnostics.state, DiagState.CLOSED)
        
        with self.assertRaises(DiagnosticsError):
            Diagnostics._make_socket_connection(5570)
        self.assertEqual(Diagnostics.state, DiagState.CLOSED)            

    @patch('coreutils.diagnostics.TcpSocket')
    def test_make_socket_wait_error(self, mock_socket):
        ms = Mock()
        mock_socket.return_value = ms
        ms.wait_for_connection.side_effect = TcpSocketError
        self.assertEqual(Diagnostics.state, DiagState.CLOSED)

        with self.assertRaises(DiagnosticsError):
            Diagnostics._make_socket_connection(5570)
        self.assertEqual(Diagnostics.state, DiagState.CLOSED)

    def test_print_closed(self):
        self.assertEqual(Diagnostics.state, DiagState.CLOSED)
        Diagnostics.socket = Mock()
        Diagnostics.buf = deque(maxlen = 20)
        self.assertEqual(len(Diagnostics.buf), 0)
        Diagnostics.print("hi")
        self.assertEqual(len(Diagnostics.buf), 1)
        Diagnostics.print("hi again")
        self.assertEqual(len(Diagnostics.buf), 2)
        Diagnostics.socket.reply.assert_not_called()
        self.assertEqual(Diagnostics.state, DiagState.CLOSED)

    def test_print_established(self):
        self.assertEqual(Diagnostics.state, DiagState.CLOSED)
        Diagnostics.socket = Mock()
        Diagnostics.state = DiagState.ESTABLISHED
        Diagnostics.buf = deque(maxlen = 20)
        self.assertEqual(len(Diagnostics.buf), 0)
        Diagnostics.print("hi")
        self.assertEqual(len(Diagnostics.buf), 0)
        Diagnostics.socket.reply.assert_called_with("hi")
        Diagnostics.print("hi again")
        self.assertEqual(len(Diagnostics.buf), 0)
        Diagnostics.socket.reply.assert_called_with("hi again")
        self.assertEqual(Diagnostics.state, DiagState.ESTABLISHED)
        Diagnostics.state = DiagState.CLOSED

    def test_print_established_error(self):
        self.assertEqual(Diagnostics.state, DiagState.CLOSED)
        Diagnostics.socket = Mock()
        Diagnostics.state = DiagState.ESTABLISHED
        Diagnostics.buf = deque(maxlen = 20)
        Diagnostics.socket.reply.side_effect = TcpSocketError
        self.assertEqual(len(Diagnostics.buf), 0)
        with self.assertRaises(DiagnosticsError):
            Diagnostics.print("hi")
        self.assertEqual(len(Diagnostics.buf), 0)
        Diagnostics.socket.reply.assert_called_with("hi")
        self.assertEqual(Diagnostics.state, DiagState.CLOSED)
        
        
