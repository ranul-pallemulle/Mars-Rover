import unittest
from unittest.mock import patch, Mock
import socket
import select
import coreutils.resource_manager as mgr

class TestResourceManager(unittest.TestCase):
    
    @patch('coreutils.resource_manager.motors.WheelMotors')
    @patch('coreutils.resource_manager.motors.ArmMotors')
    @patch('coreutils.resource_manager.camera.Camera')
    def setUp(self,mocked_cam,mocked_arm,mocked_wheels):
        self.manager = mgr.ResourceManager()
        
    @patch('coreutils.resource_manager.motors.WheelMotors')
    @patch('coreutils.resource_manager.motors.ArmMotors')
    @patch('coreutils.resource_manager.camera.Camera')
    def test_init(self,mocked_cam,mocked_arm,mocked_wheels):
        new_mgr = mgr.ResourceManager()
        self.assertEqual(new_mgr.resources['wheels'], new_mgr.FREE)
        self.assertEqual(new_mgr.resources['arm'], new_mgr.FREE)
        self.assertEqual(new_mgr.resources['camera'], 0)

    def test_get_unique(self):
        self.assertEqual(self.manager.resources['wheels'],self.manager.FREE)        
        wheels = self.manager.get_unique(mgr.Motors.WHEELS)
        self.assertIsNotNone(wheels)
        self.assertEqual(self.manager.resources['wheels'],self.manager.ACQUIRED)
        self.assertEqual(self.manager.resources['camera'],0)
        with self.assertRaises(mgr.ResourceError):
            camera = self.manager.get_unique(mgr.Camera.FEED)

    def test_get_shared(self):
        self.assertEqual(self.manager.resources['camera'],0)
        camera = self.manager.get_shared(mgr.Camera.FEED)
        self.assertEqual(self.manager.resources['camera'],1)
        
            
