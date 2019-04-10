import unittest
from unittest.mock import patch, Mock
import interfaces.actuator as act
import coreutils.resource_manager as mgr
from threading import Thread
import time

class ActImpl(act.Actuator):
    '''An implementation of Actuator.'''
    def __init__(self):
        act.Actuator.__init__(self)

    def get_values(self, motor_set):
        pass

class TestActuator(unittest.TestCase):

    def setUp(self):
        self.mock_mgr = Mock(spec_set=mgr.ResourceManager)
        act.mgr.global_resources = self.mock_mgr
        self.testImpl = ActImpl()

    def tearDown(self):
        pass

    def test_init(self):
        testImpl2 = ActImpl()
        self.assertEqual(testImpl2.release_was_called, False)
        self.assertEqual(len(testImpl2.motor_list),0)

    def test_acquire_motors(self):
        self.assertEqual(len(self.testImpl.motor_list), 0)
        self.mock_mgr.get_unique.return_value = Mock()
        self.testImpl.acquire_motors("Wheels")
        self.mock_mgr.get_unique.assert_called_with("Wheels")
        self.assertEqual(len(self.testImpl.motor_list), 1)

        self.setUp()
        self.mock_mgr.get_unique.side_effect = mgr.ResourceError
        with self.assertRaises(act.ActuatorError):
            self.testImpl.acquire_motors("Wheels")
        
        self.setUp()
        self.mock_mgr.get_unique.return_value = None
        self.testImpl.acquire_motors("Wheels")
        self.assertEqual(len(self.testImpl.motor_list), 0)
        
    def test_release_motors(self):
        self.assertEqual(len(self.testImpl.motor_list), 0)
        self.assertEqual(self.testImpl.release_was_called, False)
        self.testImpl.motor_list["Wheels"] = Mock()
        self.testImpl.release_motors("Wheels")
        self.mock_mgr.release.assert_called_with("Wheels")

    def test_have_acquired(self):
        self.assertEqual(len(self.testImpl.motor_list), 0)
        self.assertEqual(self.testImpl.have_acquired("Wheels"), False)
        self.testImpl.motor_list["Wheels"] = Mock()
        self.assertEqual(self.testImpl.have_acquired("Wheels"), True)


class method_call_logger(object):
    def __init__(self, meth):
        self.meth = meth
        self.was_called = False

    def __call__(self, code=None):
        self.meth("Wheels")
        self.was_called = True       
        
