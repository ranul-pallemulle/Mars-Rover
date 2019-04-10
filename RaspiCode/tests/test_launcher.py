import unittest
from unittest.mock import patch, Mock
from coreutils import launcher
from interfaces.opmode import OpModeError
# from coreutils.parser import CommandTypes

class TestLauncher(unittest.TestCase):

    def setUp(self):
        pass

    @patch('coreutils.launcher.OpMode')
    # @patch(launcher.kill_opmode)
    def test_release_all(self, mock_OpMode):
        mock_OpMode.get_all_names.return_value = ["test"]
        launcher.kill_opmode = method_call_logger(launcher.kill_opmode)
        mock_mode = Mock()
        mock_mode.is_stopped.return_value = False
        mock_OpMode.get.return_value = mock_mode
        launcher.release_all()
        assert(launcher.kill_opmode.was_called)


    @patch('coreutils.launcher.OpMode')
    def test_launch_opmode_invalid_mode(self, mock_OpMode):
        mock_OpMode.get.return_value = None
        with self.assertRaises(launcher.LauncherError):
            launcher.launch_opmode('somename')
        mock_OpMode.get.assert_called_with('somename')

        
    @patch('coreutils.launcher.OpMode')
    def test_launch_opmode_valid_noargs(self, mock_OpMode):
        mode = Mock()
        mock_OpMode.get.return_value = mode
        launcher.launch_opmode('somename')
        mock_OpMode.get.assert_called_with('somename')
        mode.start.assert_called_with([])
        
    @patch('coreutils.launcher.OpMode')    
    def test_launch_opmode_error(self, mock_OpMode):
        mode = Mock()
        mode.start.side_effect = OpModeError
        mock_OpMode.get.return_value = mode
        with self.assertRaises(launcher.LauncherError):
            launcher.launch_opmode('somename')
        mock_OpMode.get.assert_called_with('somename')

    @patch('coreutils.launcher.OpMode')
    def test_kill_opmode_invalid_mode(self, mock_OpMode):
        mock_OpMode.get.return_value = None
        with self.assertRaises(launcher.LauncherError):
            launcher.kill_opmode('somename')
        mock_OpMode.get.assert_called_with('somename')

    @patch('coreutils.launcher.OpMode')
    def test_kill_opmode_valid_noargs(self, mock_OpMode):
        mode = Mock()
        mock_OpMode.get.return_value = mode
        launcher.kill_opmode('somename')
        mock_OpMode.get.assert_called_with('somename')
        mode.stop.assert_called_with([])

    @patch('coreutils.launcher.OpMode')
    def test_kill_opmode_error(self, mock_OpMode):
        mode = Mock()
        mode.stop.side_effect = OpModeError
        mock_OpMode.get.return_value = mode
        with self.assertRaises(launcher.LauncherError):
            launcher.kill_opmode('somename')
        mock_OpMode.get.assert_called_with('somename')

        
class method_call_logger(object):
    def __init__(self, meth):
        self.meth = meth
        self.was_called = False

    def __call__(self, code=None):
        # self.meth("Wheels")
        self.was_called = True
