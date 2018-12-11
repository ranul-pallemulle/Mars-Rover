import unittest
from unittest.mock import patch, Mock
import start_rover

class TestStartRover(unittest.TestCase):

    @patch('start_rover.parse')
    def test_wrong_args(self,mock_parser):
        with self.assertRaises(SystemExit):
            start_rover.main(['start_rover.py','-2','blablba'])
        with self.assertRaises(SystemExit):
            start_rover.main(['start_rover.py','-2'])
        with self.assertRaises(SystemExit):
            start_rover.main(['start_rover.py','2.5'])
        with self.assertRaises(SystemExit):
            start_rover.main(['start_rover.py','one'])
            
        with patch('start_rover.TcpSocket') as mock_sock:
            mock_sock.return_value.wait_for_connection.side_effect\
            = start_rover.TcpSocketError
            with self.assertRaises(SystemExit):
                start_rover.main(['start_rover.py','2409'])
                
        with patch('start_rover.TcpSocket') as mock_sock:
            mock_sock.return_value.read.return_value = None
            with self.assertRaises(SystemExit):
                start_rover.main(['start_rover.py','2409'])
                
        start_rover.launcher.release_all = method_call_logger(\
        start_rover.launcher.release_all)
        with patch('start_rover.TcpSocket') as mock_sock:
            mock_sock.return_value.read.side_effect = start_rover.TcpSocketError
            with self.assertRaises(SystemExit):
                start_rover.main(['start_rover.py','2409'])
            assert(start_rover.launcher.release_all.was_called)

        with patch('start_rover.TcpSocket') as mock_sock:
            mock_sock.return_value.read.return_value = 'STOP_JOYSTICK'
            mock_sock.return_value.reply.side_effect = start_rover.TcpSocketError
            with self.assertRaises(SystemExit):
                start_rover.main(['start_rover.py','2409'])
            mock_parser.assert_called_with('STOP_JOYSTICK')
            mock_sock.return_value.reply.assert_called_with('ACK\n')

    def test_call_action(self):
        with patch('start_rover.launcher') as mock_launcher:
            start_rover.call_action(\
            [start_rover.CommandTypes.START_JOYSTICK,'5560'])
            mock_launcher.launch_joystick.assert_called_with(\
            [start_rover.CommandTypes.START_JOYSTICK,'5560'])
            start_rover.call_action(\
            [start_rover.CommandTypes.STOP_JOYSTICK])
            mock_launcher.kill_joystick.assert_called_with(\
            [start_rover.CommandTypes.STOP_JOYSTICK])
        
class method_call_logger(object):
    def __init__(self, meth):
        self.meth = meth
        self.was_called = False

    def __call__(self, code=None):
        self.meth()
        self.was_called = True           
