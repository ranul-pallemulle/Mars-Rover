import unittest
from unittest.mock import patch, Mock
from coreutils import launcher
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

    def test_launch_opmode(self):
        pass

    def test_kill_opmode(self):
        pass

    # def test_launch_joystick_errors(self):
    #     with self.assertRaises(launcher.LauncherError):
    #         launcher.launch_joystick([CommandTypes.START_ARM, '4450'])
    #     with self.assertRaises(launcher.LauncherError):
    #         launcher.launch_joystick([CommandTypes.START_JOYSTICK])        
    #     with self.assertRaises(launcher.LauncherError):
    #         launcher.launch_joystick([CommandTypes.START_JOYSTICK, ])
    #     with self.assertRaises(launcher.LauncherError):
    #         launcher.launch_joystick([CommandTypes.START_JOYSTICK,'\n'])
    #     with self.assertRaises(launcher.LauncherError):
    #         launcher.launch_joystick([CommandTypes.START_JOYSTICK,'445.2'])
    #     with self.assertRaises(launcher.LauncherError):
    #         # reserved port
    #         launcher.launch_joystick([CommandTypes.START_JOYSTICK,'445'])

    # def test_kill_joystick_errors(self):
    #     with self.assertRaises(launcher.LauncherError):
    #         # wrong command
    #         launcher.kill_joystick([CommandTypes.STOP_ARM])
    #     with self.assertRaises(launcher.LauncherError):
    #         # uninitialised
    #         launcher.kill_joystick([CommandTypes.STOP_JOYSTICK])
    #     with self.assertRaises(launcher.LauncherError):
    #         # uninitialised
    #         launcher.kill_joystick([CommandTypes.STOP_JOYSTICK, '\n'])
    #     with self.assertRaises(launcher.LauncherError):
    #         # uninitialised
    #         launcher.kill_joystick([CommandTypes.STOP_JOYSTICK, ])

    # def test_launch_arm_errors(self):
    #     with self.assertRaises(launcher.LauncherError):
    #         launcher.launch_arm([CommandTypes.START_JOYSTICK, '4450'])
    #     with self.assertRaises(launcher.LauncherError):
    #         launcher.launch_arm([CommandTypes.START_ARM])
    #     with self.assertRaises(launcher.LauncherError):
    #         launcher.launch_arm([CommandTypes.START_ARM, ])
    #     with self.assertRaises(launcher.LauncherError):
    #         launcher.launch_arm([CommandTypes.START_ARM,'\n'])
    #     with self.assertRaises(launcher.LauncherError):
    #         launcher.launch_arm([CommandTypes.START_ARM,'445.2'])
    #     with self.assertRaises(launcher.LauncherError):
    #         # reserved port
    #         launcher.launch_arm([CommandTypes.START_ARM,'445'])

    # def test_kill_arm_errors(self):
    #     with self.assertRaises(launcher.LauncherError):
    #         # wrong command
    #         launcher.kill_arm([CommandTypes.STOP_JOYSTICK])
    #     with self.assertRaises(launcher.LauncherError):
    #         # uninitialised
    #         launcher.kill_arm([CommandTypes.STOP_ARM])
    #     with self.assertRaises(launcher.LauncherError):
    #         # uninitialised
    #         launcher.kill_arm([CommandTypes.STOP_ARM, '\n'])
    #     with self.assertRaises(launcher.LauncherError):
    #         # uninitialised
    #         launcher.kill_arm([CommandTypes.STOP_ARM, ])

class method_call_logger(object):
    def __init__(self, meth):
        self.meth = meth
        self.was_called = False

    def __call__(self, code=None):
        # self.meth("Wheels")
        self.was_called = True
