import unittest
from unittest.mock import patch, Mock
from coreutils import launcher
from coreutils.parser import CommandTypes

class TestLauncher(unittest.TestCase):

    def test_launch_joystick_errors(self):
        with self.assertRaises(launcher.LauncherError):
            launcher.launch_joystick([CommandTypes.START_ARM, '4450'])
        with self.assertRaises(launcher.LauncherError):
            launcher.launch_joystick([CommandTypes.START_JOYSTICK])        
        with self.assertRaises(launcher.LauncherError):
            launcher.launch_joystick([CommandTypes.START_JOYSTICK, ])
        with self.assertRaises(launcher.LauncherError):
            launcher.launch_joystick([CommandTypes.START_JOYSTICK,'\n'])
        with self.assertRaises(launcher.LauncherError):
            launcher.launch_joystick([CommandTypes.START_JOYSTICK,'445.2'])
        with self.assertRaises(launcher.LauncherError):
            # reserved port
            launcher.launch_joystick([CommandTypes.START_JOYSTICK,'445'])

    def test_kill_joystick_errors(self):
        with self.assertRaises(launcher.LauncherError):
            # wrong command
            launcher.kill_joystick([CommandTypes.STOP_ARM])
        with self.assertRaises(launcher.LauncherError):
            # uninitialised
            launcher.kill_joystick([CommandTypes.STOP_JOYSTICK])
        with self.assertRaises(launcher.LauncherError):
            # uninitialised
            launcher.kill_joystick([CommandTypes.STOP_JOYSTICK, '\n'])
        with self.assertRaises(launcher.LauncherError):
            # uninitialised
            launcher.kill_joystick([CommandTypes.STOP_JOYSTICK, ])

    def test_launch_arm_errors(self):
        with self.assertRaises(launcher.LauncherError):
            launcher.launch_arm([CommandTypes.START_JOYSTICK, '4450'])
        with self.assertRaises(launcher.LauncherError):
            launcher.launch_arm([CommandTypes.START_ARM])
        with self.assertRaises(launcher.LauncherError):
            launcher.launch_arm([CommandTypes.START_ARM, ])
        with self.assertRaises(launcher.LauncherError):
            launcher.launch_arm([CommandTypes.START_ARM,'\n'])
        with self.assertRaises(launcher.LauncherError):
            launcher.launch_arm([CommandTypes.START_ARM,'445.2'])
        with self.assertRaises(launcher.LauncherError):
            # reserved port
            launcher.launch_arm([CommandTypes.START_ARM,'445'])

    def test_kill_arm_errors(self):
        with self.assertRaises(launcher.LauncherError):
            # wrong command
            launcher.kill_arm([CommandTypes.STOP_JOYSTICK])
        with self.assertRaises(launcher.LauncherError):
            # uninitialised
            launcher.kill_arm([CommandTypes.STOP_ARM])
        with self.assertRaises(launcher.LauncherError):
            # uninitialised
            launcher.kill_arm([CommandTypes.STOP_ARM, '\n'])
        with self.assertRaises(launcher.LauncherError):
            # uninitialised
            launcher.kill_arm([CommandTypes.STOP_ARM, ])

