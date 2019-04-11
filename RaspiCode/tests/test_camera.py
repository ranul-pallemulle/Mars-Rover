import unittest
from unittest.mock import patch, Mock
import resources.camera as camera
import coreutils.configure as cfg
import time
from sys import platform

class TestCamera(unittest.TestCase):

    @patch('resources.camera.cfg')
    def setUp(self,mock_cfg):
        mock_cfg.cam_config = cfg.CameraConfiguration('tests/testsettings.xml')
        self.testcam = camera.Camera()

    @patch('resources.camera.cfg')
    def test_init(self,mock_cfg):
        mock_cfg.cam_config = cfg.CameraConfiguration('tests/testsettings.xml')
        testcam2 = camera.Camera()
        self.assertEqual(testcam2.active, False)
        # op_mode = cfg.global_config.operation_mode()
        # if op_mode == "LAPTOP":
            # self.assertEqual(testcam2.framerate, 30)
            # self.assertEqual(testcam2.frame_width, 640)
            # self.assertEqual(testcam2.frame_height, 480)
            # gst_str = 'v4l2src ! video/x-raw,framerate=30/1,width=640,height=480 ! videoconvert ! appsink name=opencvsink sync=false'
            # self.assertEqual(testcam2.gst_comm, gst_str)
        #     if platform == 'darwin':
        #         self.assertEqual(testcam2.source, 'avfvideosrc')
        #     else:
        #         self.assertEqual(testcam2.source, 'v4l2src')
        # elif op_mode == "RASPBERRYPI":
            # self.assertEqual(testcam2.framerate, 30)
            # self.assertEqual(testcam2.frame_width, 200)
            # self.assertEqual(testcam2.frame_height, 150)
            # gst_str = 'v4l2src ! video/x-raw,framerate=30/1,width=200,height=150 ! videoconvert ! appsink name=opencvsink sync=false'
            # self.assertEqual(testcam2.gst_comm, gst_str)
            # self.assertEqual(testcam2.source, 'v4l2src')
        self.assertIsNone(testcam2.cap)
        self.assertFalse(testcam2.active)
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
        # mock_cv2.cvtColor.return_value = mock_frame
        self.assertEqual(self.testcam.get_frame(), mock_frame)
        # mock_cv2.cvtColor.assert_called_with(mock_frame, mock_cv2.COLOR_BGR2RGB)

    def test_eval_gst_comm_good(self):
        self.testcam.source = 'v4l2src'
        self.testcam.framerate = 100
        self.testcam.frame_width = 5000
        self.testcam.frame_height = 2000
        self.testcam._eval_gst_comm()
        gst_str = 'v4l2src ! video/x-raw,framerate=100/1,width=5000,height=2000 ! videoconvert ! appsink name=opencvsink sync=false'
        self.assertEqual(self.testcam.gst_comm, gst_str)

    # def test_eval_gst_bad(self):
    #     self.testcam.running = True
    #     with self.assertRaises(camera.CameraError):
    #         self.testcam._eval_gst_comm()

    # @patch('resources.camera.Thread')
    # @patch('resources.camera.cv2')
    # def test_start(self, mock_cv2, mock_thread):
    #     mock_thread_retval = Mock()
    #     mock_thread.return_value = mock_thread_retval        
    #     self.assertEqual(self.testcam.running,False)
    #     self.testcam.start()
    #     mock_thread.assert_called_with(args=(),target=self.testcam._capture)
    #     mock_thread_retval.start.assert_called_with()
    #     self.assertEqual(self.testcam.running,True)

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

    # def test_stop(self):
    #     self.testcam.cap = Mock()
    #     self.testcam.running = True
    #     self.testcam.stop()
    #     self.testcam.cap.release.assert_called_with()
    #     self.assertEqual(self.testcam.running, False)

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
        
