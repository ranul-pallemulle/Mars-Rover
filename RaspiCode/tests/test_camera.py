import unittest
from unittest.mock import patch, Mock
from resources.resource import Resource, ResourceRawError, Policy
import resources.camera as camera
import coreutils.configure as cfg
import time
from sys import platform

class TestCamera(unittest.TestCase):

    @patch('resources.camera.cfg')
    def setUp(self,mock_cfg):
        # self.mock_cfg.cam_config = cfg.CameraConfiguration('tests/testsettings.xml')
        mock_cfg.cam_config.device.return_value = 'v4l2src'
        mock_cfg.cam_config.capture_framerate.return_value = 60
        mock_cfg.cam_config.capture_frame_width.return_value = 200
        mock_cfg.cam_config.capture_frame_height.return_value = 150
        self.testcam = camera.Camera()

    def tearDown(self):
        Resource.resource_list = dict()

    def test_init(self):
        self.assertEqual(self.testcam.active, False)
        self.assertEqual(self.testcam.policy, Policy.SHARED)
        self.assertEqual(self.testcam.name, "Camera")
        self.assertEqual(self.testcam.source, "v4l2src")
        self.assertEqual(self.testcam.framerate, 60)
        self.assertEqual(self.testcam.frame_width, 200)
        self.assertEqual(self.testcam.frame_height, 150)
        self.assertIsNone(self.testcam.gst_comm)
        self.assertIsNone(self.testcam.cap)
        self.assertFalse(self.testcam.active)

    @patch('resources.camera.cfg')
    def test_init_nodevice(self, mock_cfg):
        mock_cfg.ConfigurationError = cfg.ConfigurationError
        mock_cfg.cam_config.device.side_effect = cfg.ConfigurationError
        mock_cfg.cam_config.capture_framerate.return_value = 60
        mock_cfg.cam_config.capture_frame_width.return_value = 200
        mock_cfg.cam_config.capture_frame_height.return_value = 150        
        with self.assertRaises(ResourceRawError):
            camera.Camera()
        
    @patch('resources.camera.cv2')
    def test_get_frame(self, mock_cv2):
        self.assertEqual(self.testcam.is_active(),False)
        with self.assertRaises(camera.CameraError):
            self.testcam.get_frame()
        self.testcam.active = True
        self.testcam.cap = Mock()
        mock_frame = Mock()
        self.testcam.cap.read.return_value = (False, mock_frame)
        self.assertIsNone(self.testcam.get_frame())
        self.assertTrue(self.testcam.active)
        self.testcam.cap.read.return_value = (True, mock_frame)
        self.assertEqual(self.testcam.get_frame(), mock_frame)
        
    def test_eval_gst_comm(self):
        self.testcam.source = 'v4l2src'
        self.testcam.framerate = 100
        self.testcam.frame_width = 5000
        self.testcam.frame_height = 2000
        self.testcam._eval_gst_comm()
        gst_str = 'v4l2src ! video/x-raw,framerate=100/1,width=5000,height=2000 ! videoconvert ! appsink name=opencvsink sync=false'
        self.assertEqual(self.testcam.gst_comm, gst_str)

    @patch('resources.camera.cv2')
    def test_start_capture(self, mock_cv2):
        self.testcam.cap = Mock()
        with self.assertRaises(camera.CameraError):
            self.testcam.start_capture()
        self.testcam.cap = None
        self.testcam.active = True
        with self.assertRaises(camera.CameraError):
            self.testcam.start_capture()
        self.testcam.cap = None
        self.testcam.active = False
        self.testcam.start_capture()
        mock_cv2.VideoCapture.assert_called_with(self.testcam.gst_comm)
        self.assertTrue(self.testcam.active)

    def test_stop_capture(self):
        self.testcam.cap = None
        self.testcam.active = True
        with self.assertRaises(camera.CameraError):
            self.testcam.stop_capture()
        self.testcam.cap = Mock()
        self.testcam.active = False
        with self.assertRaises(camera.CameraError):
            self.testcam.stop_capture()
        self.testcam.cap = Mock()
        self.testcam.active = True
        backup_cap = self.testcam.cap
        self.testcam.stop_capture()
        backup_cap.release.assert_called_with()
        self.assertIsNone(self.testcam.cap)
        self.assertFalse(self.testcam.active)
        
