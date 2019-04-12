import unittest
from unittest.mock import patch, Mock
import start_rover

class TestStartRover(unittest.TestCase):

    @patch('start_rover.cfg.Configuration')
    def test_wrong_args(self, unused_mock_cfg):
        '''Invalid arguments to start the program. 
        > Program must terminate.'''
        with self.assertRaises(SystemExit):
            # too many arguments
            start_rover.main(['start_rover.py','3500','blablba','debug.xml'])
        with self.assertRaises(SystemExit):
            start_rover.main(['start_rover.py', '-2']) # negative
        with self.assertRaises(SystemExit):
            start_rover.main(['start_rover.py','-2','debug.xml']) # negative
        with self.assertRaises(SystemExit):
            start_rover.main(['start_rover.py', '2.5']) # float
        with self.assertRaises(SystemExit):
            start_rover.main(['start_rover.py','2.5','debug.xml']) # float
        with self.assertRaises(SystemExit):
            start_rover.main(['start_rover.py','100']) # too small
        with self.assertRaises(SystemExit):
            start_rover.main(['start_rover.py','50000000']) # too large
        with self.assertRaises(SystemExit):
            start_rover.main(['start_rover.py','one']) # port should be int
        with self.assertRaises(SystemExit):
            start_rover.main(['start_rover.py', 'debug.xml']) # no port

    @patch('start_rover.cfg.Configuration')
    def test_bad_settings(self, mock_cfg):
        '''ConfigurationError raised by configuration manager when initialising 
using specified settings file.
        > Configuration.settings_file() must be called, and program must 
        terminate.'''
        mock_cfg.settings_file.side_effect = start_rover.cfg.ConfigurationError
        with self.assertRaises(SystemExit):
            start_rover.main(['start_rover.py','5560','debug.xml'])
        mock_cfg.settings_file.assert_called_with('debug.xml')

    @patch('start_rover.OpMode')
    def test_opmode_initialise_error(self, mock_opmode):
        '''OpModeError raised during OpMode.opmodes_initialise().
        > OpMode.opmodes_initialise must be called and program must 
        terminate.'''
        mock_opmode.opmodes_initialise.side_effect = start_rover.OpModeError
        with self.assertRaises(SystemExit):
            start_rover.main(['start_rover.py','5560','debug.xml'])
        mock_opmode.opmodes_initialise.assert_called_with()

    @patch('start_rover.mgr.global_resources')
    def test_resource_manager_initialise_error(self, mock_mgr):
        '''ResourceError raised during global_resources.initialise().
        > global_resources.initialise must be called and program must 
        terminate.'''
        mock_mgr.initialise.side_effect = start_rover.mgr.ResourceError
        with self.assertRaises(SystemExit):
            start_rover.main(['start_rover.py', '5560', 'debug.xml'])
        mock_mgr.initialise.assert_called_with()

    @patch('start_rover.TcpSocket')
    def test_wait_connection_error(self, mock_sock):
        '''TcpSocketError raised while waiting for connection from remote.
        > Program must terminate.'''
        mock_sock.return_value.wait_for_connection.side_effect\
            = start_rover.TcpSocketError
        with self.assertRaises(SystemExit):
            start_rover.main(['start_rover.py','2409','debug.xml'])

    @patch('start_rover.TcpSocket')
    def test_read_connection_drop(self, mock_sock):
        '''Connection terminated (EOF) by remote.  
        > Program must terminate after calling launcher.release_all() to stop 
any active modes.'''
        start_rover.launcher.release_all = method_call_logger(\
        start_rover.launcher.release_all)        
        mock_sock.return_value.read.return_value = None
        with self.assertRaises(SystemExit):
            start_rover.main(['start_rover.py','2409','debug.xml'])
        assert(start_rover.launcher.release_all.was_called)

    @patch('start_rover.TcpSocket')
    def test_read_error(self, mock_sock):
        '''TcpSocketError raised while receiving command from remote.
        > Program must terminate after calling launcher.release_all() to stop 
any active modes.'''
        start_rover.launcher.release_all = method_call_logger(\
        start_rover.launcher.release_all)
        mock_sock.return_value.read.side_effect = start_rover.TcpSocketError
        with self.assertRaises(SystemExit):
            start_rover.main(['start_rover.py','2409','debug.xml'])
        assert(start_rover.launcher.release_all.was_called)

    @patch('start_rover.TcpSocket')
    @patch('start_rover.parse_entry')
    def test_reply_error(self, mock_parser, mock_sock):
        '''TcpSocketError raised while replying to remote after a valid command
 was received.
        > Program must terminate after calling launcher.release_all() to stop
any active modes. parse_entry should have been called with the right command. 
TcpSocket.reply() should have been called with 'ACK'.'''
        start_rover.launcher.release_all = method_call_logger(\
        start_rover.launcher.release_all)
        mock_sock.return_value.read.return_value = 'STOP_JOYSTICK'
        mock_sock.return_value.reply.side_effect = start_rover.TcpSocketError
        with self.assertRaises(SystemExit):
            start_rover.main(['start_rover.py','2409','debug.xml'])
        mock_parser.assert_called_with('STOP_JOYSTICK')
        mock_sock.return_value.reply.assert_called_with('ACK')
        assert(start_rover.launcher.release_all.was_called)

    @patch('start_rover.parse_entry')
    @patch('start_rover.TcpSocket')
    def test_command_error(self, mock_sock, mock_parser):
        '''CommandError raised by parse_entry. Test makes use of TcpSocketError
        on TcpSocket.reply so that the test can terminate.
        > Must send reply to remote containing the error string.'''
        mock_sock.return_value.read.return_value = "SOME BAD COMMAND"
        mock_sock.return_value.reply.side_effect = start_rover.TcpSocketError
        err_string = "bad command"
        mock_parser.side_effect = start_rover.CommandError(err_string)
        with self.assertRaises(start_rover.TcpSocketError):
            start_rover.main(['start_rover.py', '3500', 'debug.xml'])
        mock_sock.return_value.reply.assert_called_with(err_string)

    @patch('start_rover.OpMode')
    @patch('start_rover.launcher')
    def test_call_action_valid(self, mock_launcher, mock_opmode):
        '''call_action called in a valid way.
        > The correct launcher functions must be called with the right arguments 
given a valid command.'''
        comm = [start_rover.CommandPrefixes.START,'Joystick','5560']
        start_rover.call_action(comm)
        mock_launcher.launch_opmode.assert_called_with('Joystick',['5560'])

        comm = [start_rover.CommandPrefixes.STOP,'Joystick']
        start_rover.call_action(comm)
        mock_launcher.kill_opmode.assert_called_with('Joystick',[])

        comm = ['Joystick','hi']
        mock_mode = Mock()
        mock_mode.is_running.return_value = True
        mock_opmode.get.return_value = mock_mode
        start_rover.call_action(comm)
        mock_mode.is_running.assert_called_with()
        mock_mode.submode_command.assert_called_with(['hi'])

    @patch('start_rover.OpMode')
    @patch('start_rover.launcher')
    def test_call_action_invalid(self, mock_launcher, mock_opmode):
        '''Opmode.get called within call_action throws an error due to invalid 
object supplied as an argument to be used as a dict key.
        > call_action should handle the error by simply printing out the result and returning.
        Hence there should be no errors on calling call_action.'''
        comm = 'some invalid object that cannot be used as dict key'
        mock_opmode.get.side_effect = start_rover.OpModeError
        start_rover.call_action(comm)

    @patch('start_rover.OpMode')
    @patch('start_rover.launcher')
    def test_call_action_unhandled_exception(self, mock_launcher, mock_opmode):
        '''Some random exception thrown deep within the program may get 
propagated all the way up to where the a command is issued, which is call_action
.
        > Program must terminate after printing out the error.'''
        arg_list = [start_rover.CommandPrefixes.START, 'something']
        mock_launcher.launch_opmode.side_effect = Exception
        with self.assertRaises(SystemExit):
            start_rover.call_action(arg_list)
        
class method_call_logger(object):
    def __init__(self, meth):
        self.meth = meth
        self.was_called = False

    def __call__(self, code=None):
        self.meth()
        self.was_called = True           
