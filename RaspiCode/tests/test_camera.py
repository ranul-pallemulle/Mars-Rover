import unittest
from unittest.mock import patch, Mock
import resources.camera as camera
import coreutils.configure as cfg
import time

class TestCamera(unittest.TestCase):

    def setUp(self):
        self.testcam = camera.Camera()

    def test_init(self):
        testcam2 = camera.Camera()
        self.assertEqual(testcam2.running, False)
        op_mode = cfg.global_config.operation_mode()
        if op_mode == "LAPTOP":
            self.assertEqual(testcam2.framerate, 30)
            self.assertEqual(testcam2.frame_width, 640)
            self.assertEqual(testcam2.frame_height, 480)
            gst_str = 'v4l2src ! video/x-raw,framerate=30/1,width=640,height=480 ! videoconvert ! appsink name=opencvsink sync=false'
            self.assertEqual(testcam2.gst_comm, gst_str)            
        elif op_mode == "RASPBERRYPI":
            self.assertEqual(testcam2.framerate, 30)
            self.assertEqual(testcam2.frame_width, 200)
            self.assertEqual(testcam2.frame_height, 150)
            gst_str = 'v4l2src ! video/x-raw,framerate=30/1,width=200,height=150 ! videoconvert ! appsink name=opencvsink sync=false'
            self.assertEqual(testcam2.gst_comm, gst_str)

    def test_get_frame_bad(self):
        self.assertEqual(self.testcam.is_running(),False)
        self.assertIsNone(self.testcam.get_frame())

    def test_eval_gst_comm_good(self):
        self.assertEqual(self.testcam.is_running(), False)
        self.testcam.source = 'v4l2src'
        self.testcam.framerate = 100
        self.testcam.frame_width = 5000
        self.testcam.frame_height = 2000
        self.testcam._eval_gst_comm()
        gst_str = 'v4l2src ! video/x-raw,framerate=100/1,width=5000,height=2000 ! videoconvert ! appsink name=opencvsink sync=false'
        self.assertEqual(self.testcam.gst_comm, gst_str)

    def test_eval_gst_bad(self):
        self.testcam.running = True
        with self.assertRaises(camera.CameraError):
            self.testcam._eval_gst_comm()

    @patch('resources.camera.Thread')
    @patch('resources.camera.cv2')
    def test_start(self, mock_cv2, mock_thread):
        mock_thread_retval = Mock()
        mock_thread.return_value = mock_thread_retval        
        self.assertEqual(self.testcam.running,False)
        self.testcam.start()
        mock_thread.assert_called_with(args=(),target=self.testcam._capture)
        mock_thread_retval.start.assert_called_with()
        self.assertEqual(self.testcam.running,True)

    def test_stop(self):
        self.testcam.cap = Mock()
        self.testcam.running = True
        self.testcam.stop()
        self.testcam.cap.release.assert_called_with()
        self.assertEqual(self.testcam.running, False)

    def test_start_bad(self):
        self.testcam.running = True
        with self.assertRaises(camera.CameraError):
            self.testcam.start()

    def test_stop_bad(self):
        self.testcam.running = False
        with self.assertRaises(camera.CameraError):
            self.testcam.stop()
        
