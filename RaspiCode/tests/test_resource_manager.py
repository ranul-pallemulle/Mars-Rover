import unittest
from unittest.mock import patch, Mock
import socket
import select
import coreutils.resource_manager as mgr
from coreutils.resource_manager import Motors
from coreutils.resource_manager import Camera

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
        self.assertEqual(new_mgr.resources[Motors.WHEELS], new_mgr.FREE)
        self.assertEqual(new_mgr.resources[Motors.ARM], new_mgr.FREE)
        self.assertEqual(new_mgr.resources[Camera.FEED], 0)

    def test_get_unique(self):
        self.assertEqual(self.manager.resources[Motors.WHEELS],self.manager.FREE)        
        wheels = self.manager.get_unique(Motors.WHEELS)
        self.assertIsNotNone(wheels)
        self.assertEqual(self.manager.resources[Motors.WHEELS],self.manager.ACQUIRED)
        self.assertEqual(self.manager.resources[Camera.FEED],0)
        with self.assertRaises(mgr.ResourceError):
            camera = self.manager.get_unique(Camera.FEED)

    def test_get_shared(self):
        self.assertEqual(self.manager.resources[Camera.FEED],0)
        camera = self.manager.get_shared(Camera.FEED)
        self.assertEqual(self.manager.resources[Camera.FEED],1)
        
    def test_release(self):
        self.assertEqual(self.manager.resources[Camera.FEED],0)
        camera = self.manager.get_shared(Camera.FEED)
        self.assertEqual(self.manager.resources[Camera.FEED],1)
        camera2 = self.manager.get_shared(Camera.FEED)
        self.assertEqual(self.manager.resources[Camera.FEED],2)
        self.manager.release(Camera.FEED)
        self.assertEqual(self.manager.resources[Camera.FEED],1)
        self.manager.release(Camera.FEED)
        self.assertEqual(self.manager.resources[Camera.FEED],0)
        with self.assertRaises(mgr.ResourceError):
            self.manager.release(Motors.ARM) # unacquired
        with self.assertRaises(mgr.ResourceError):
            self.manager.release(Motors.WHEELS) # unacquired
        with self.assertRaises(mgr.ResourceError):
            self.manager.release(22) # unknown
            
