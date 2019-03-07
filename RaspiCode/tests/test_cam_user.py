import unittest
from unittest.mock import patch,Mock
import interfaces.cam_user as cam_user
import coreutils.resource_manager as mgr
from resources.camera import CameraError


class CamUserImpl(cam_user.CameraUser):
    def __init__(self):
        cam_user.CameraUser.__init__(self)

class TestCamUser(unittest.TestCase):

    def setUp(self):
        self.mock_mgr = Mock(spec_set=mgr.ResourceManager)
        cam_user.mgr.global_resources = self.mock_mgr
        self.testImpl = CamUserImpl()

    def tearDown(self):
        pass

    def test_init(self):
        testImpl2 = CamUserImpl()
        self.assertIsNone(testImpl2.camera)
        self.assertIsNone(testImpl2.stream_writer)
        self.assertFalse(testImpl2.streaming)

    def test_acquire_camera(self):
        self.assertIsNone(self.testImpl.camera)
        self.mock_mgr.get_shared.return_value = Mock()
        self.testImpl.acquire_camera()
        self.mock_mgr.get_shared.assert_called_with(mgr.Camera.FEED)
        self.assertIsNotNone(self.testImpl.camera)

        self.setUp()
        self.mock_mgr.get_shared.side_effect = mgr.ResourceError
        with self.assertRaises(cam_user.CameraUserError):
            self.testImpl.acquire_camera()

        self.setUp()
        self.testImpl.camera = Mock()
        with self.assertRaises(cam_user.CameraUserError):
            self.testImpl.acquire_camera()

    def test_release_camera(self):
        self.testImpl.camera = Mock()
        self.testImpl.release_camera()
        self.mock_mgr.release.assert_called_with(mgr.Camera.FEED)
        self.assertIsNone(self.testImpl.camera)

    def test_have_acquired(self):
        self.assertIsNone(self.testImpl.camera)
        self.assertEqual(self.testImpl.have_camera(), False)
        self.testImpl.camera = Mock()
        self.assertEqual(self.testImpl.have_camera(), True)

    @patch('interfaces.cam_user.Thread')
    @patch('interfaces.cam_user.cv2')
    @patch('interfaces.cam_user.cfg')
    def test_begin_stream_none_source(self, mock_cfg, mock_cv2, mock_thread):
        mock_cfg.global_config.ip_address.return_value = '192.168.1.1'
        mock_cfg.global_config.operation_mode.return_value = 'LAPTOP'
        mock_camconfig = Mock()
        mock_camconfig.stream_port.return_value = 1000
        mock_camconfig.stream_framerate.return_value = 10
        mock_camconfig.stream_frame_width.return_value = 5000
        mock_camconfig.stream_frame_height.return_value = 2500
        mock_camconfig.capture_framerate.return_value = 10
        mock_camconfig.capture_frame_width.return_value = 5000
        mock_camconfig.capture_frame_height.return_value = 2500
        mock_cfg.CameraConfiguration.return_value = mock_camconfig
        comm = 'appsrc ! videoconvert ! video/x-raw,width=5000,height=2500,framerate=10/1 ! x264enc tune=zerolatency speed-preset=ultrafast bitrate=8000 ! rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=192.168.1.1 port=1000 sync=false'
        mock_thread_retval = Mock()
        mock_thread.return_value = mock_thread_retval
        self.testImpl.camera = Mock()
        self.assertFalse(self.testImpl.streaming)
        self.testImpl.begin_stream()
        mock_cv2.VideoWriter.assert_called_with(comm, mock_cv2.CAP_GSTREAMER, 0, 10, (5000,2500),True)
        self.assertTrue(self.testImpl.streaming)
        mock_thread.assert_called_with(args=(), target=self.testImpl._stream)
        mock_thread_retval.start.assert_called_with()

        self.setUp()
        self.assertFalse(self.testImpl.streaming)
        with self.assertRaises(cam_user.CameraUserError):
            self.testImpl.begin_stream()

    def test_end_stream(self):
        self.testImpl.stream_writer = Mock()
        backup_writer = self.testImpl.stream_writer
        self.testImpl.streaming = True
        self.testImpl.end_stream()
        backup_writer.release.assert_called_with()
        self.assertIsNone(self.testImpl.stream_writer)
        self.assertFalse(self.testImpl.streaming)

        self.setUp()
        self.assertFalse(self.testImpl.streaming)
        with self.assertRaises(cam_user.CameraUserError):
            self.testImpl.end_stream()

    # def test_stream_not_streaming(self):
    #     self.testImpl.stream_writer = Mock()
    #     self.testImpl.camera = Mock()
    #     self.assertFalse(self.testImpl.streaming)
        
    def test_start_camera_capture(self):
        pass

    def test_stop_camera_capture(self):
        pass

    def test_get_camera_frame(self):
        self.testImpl.camera = Mock() # have_camera returns True
        self.testImpl.get_camera_frame()
        self.testImpl.camera.get_frame.assert_called_with()
        self.testImpl.have_camera = Mock()
        self.testImpl.have_camera.return_value = False
        with self.assertRaises(cam_user.CameraUserError):
            self.testImpl.get_camera_frame()
        self.testImpl.camera.get_frame.side_effect = CameraError
        self.testImpl.have_camera.return_value = True
        with self.assertRaises(cam_user.CameraUserError):
            self.testImpl.get_camera_frame()
            
