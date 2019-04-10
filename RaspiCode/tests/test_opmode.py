import unittest
from unittest.mock import patch, Mock
from interfaces.opmode import OpMode, OpModeError

class OpModeInstance(OpMode):
    def __init__(self):
        OpMode.__init__(self)
        self.register_name("MockOpMode")

    def start(self, args):
        print("starting")

    def stop(self, args):
        print("stopping")

    def submode_command(self, args):
        print(args[0])

class TestOpMode(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.ranSetup = False
        
    @patch('interfaces.opmode.cfg')
    def setUp(self, mocked_cfg):
        if not type(self).ranSetup:
            OpMode.opmodes_initialise()
            type(self).ranSetup = True
        
    def test_init(self):
        all_names = OpMode.get_all_names()
        if not 'MockOpMode' in all_names:
            self.fail()
            
