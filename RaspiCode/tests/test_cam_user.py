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
        self.mock_mgr.get_shared.assert_called_with("Camera")
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
        self.mock_mgr.release.assert_called_with("Camera")
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
        mock_cfg.overall_config.ip_address.return_value = '192.168.1.1'
        mock_cfg.cam_config.device.return_value = 'v4l2src'
        mock_cfg.cam_config.stream_port.return_value = 1000
        mock_cfg.cam_config.stream_framerate.return_value = 10
        mock_cfg.cam_config.stream_frame_width.return_value = 5000
        mock_cfg.cam_config.stream_frame_height.return_value = 2500
        mock_cfg.cam_config.capture_framerate.return_value = 10
        mock_cfg.cam_config.capture_frame_width.return_value = 5000
        mock_cfg.cam_config.capture_frame_height.return_value = 2500
        comm = 'appsrc ! videoconvert ! video/x-raw,width=5000,height=2500,framerate=10/1 ! x264enc tune=zerolatency ! rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=192.168.1.1 port=1000 sync=false'
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

    def test_stream_error_none_writer(self):
        self.testImpl.stream_writer = None
        with self.assertRaises(cam_user.CameraUserError):
            self.testImpl._stream()

    def test_stream_error_no_cam(self):
        have_cam_mock = Mock()
        have_cam_mock.return_value = False
        self.testImpl.have_camera = have_cam_mock
        with self.assertRaises(cam_user.CameraUserError):
            self.testImpl._stream()

    def test_stream_error_not_active(self):
        is_active_mock = Mock()
        is_active_mock.is_active.return_value = False
        self.testImpl.camera = Mock()
        self.testImpl.camera.is_active = is_active_mock
        with self.assertRaises(cam_user.CameraUserError):
            self.testImpl._stream()

    # def test_stream_error_get_cam_frame(self):
    #     get_frame = Mock()
    #     get_frame.side_effect = cam_user.CameraUserError
    #     self.testImpl.stream_writer = Mock()
    #     self.testImpl.have_camera = Mock()
    #     self.testImpl.have_camera.return_value = True
    #     self.testImpl.camera = Mock()
    #     self.testImpl.camera.is_active.return_value = True
    #     self.testImpl.get_camera_frame = get_frame
    #     self.testImpl._stream()
    #     self.testImpl.get_camera_frame.assert_called_with()
    #     self.testImpl.stream_writer.write.assert_not_called()

    # def test_stream_good(self):
    #     get_frame = Mock()
    #     frame = Mock()
    #     get_frame.return_value = frame
    #     self.testImpl.stream_writer = Mock()
    #     self.testImpl.have_camera = Mock()
    #     self.testImpl.have_camera.return_value = True
    #     self.testImpl.camera = Mock()
    #     self.testImpl.camera.is_active.return_value = True
    #     self.testImpl.get_camera_frame = get_frame
    #     self.testImpl._stream()
    #     self.testImpl.get_camera_frame.assert_called_with()
    #     self.testImpl.stream_writer.write.assert_called_with(frame)

            
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
            
