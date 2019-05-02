from abc import ABCMeta, abstractmethod
import coreutils.configure as cfg
# from resources.camera import CameraError
import coreutils.resource_manager as mgr
import cv2
from threading import Thread
import numpy as np

class CameraUserError(Exception):
    '''Exception class that will be raised by classes implementiong CameraUser.'''
    pass

class CameraUser:
    '''Provides an interface to the camera resource.'''
    __metaclass__ = ABCMeta

    def __init__(self):
        self.camera = None
        self.stream_writer = None
        self.streaming = False

    def _stream(self):
        if self.stream_writer is None:
            raise CameraUserError('Stream writer not initialised.')
        if not self.have_camera():
            raise CameraUserError('Camera not acquired: cannot stream.')

        if not self.camera.is_active():
            raise CameraUserError('Camera not active: cannot stream.')
        
        while self.streaming:
            try:
                frame = self.get_camera_frame()
            except CameraUserError:
                continue
            self.stream_writer.write(frame)

    def get_camera_frame(self):
        if self.have_camera():
            try:
                frame = self.camera.get_frame()
                if frame is not None:
                    return np.array(frame)
            except Exception as e:
                raise CameraUserError(str(e))
            raise CameraUserError('Error in camera frame.')
        raise CameraUserError('Camera not acquired.')

    def begin_stream(self, source=None):
        '''Stream source (default is direct camera output) to the specified port.'''
        if self.streaming:
            raise CameraUserError('Already streaming: cannot start new stream.')
        if not self.have_camera():
            raise CameraUserError('Camera not acquired.')
        
        host = cfg.overall_config.ip_address()
        if source is None:
            strm_port = cfg.cam_config.stream_port()
            strm_framerate = cfg.cam_config.stream_framerate()
            strm_width = cfg.cam_config.stream_frame_width()
            strm_height = cfg.cam_config.stream_frame_height()

            src_framerate = cfg.cam_config.capture_framerate()
            src_width = cfg.cam_config.capture_frame_width()
            src_height = cfg.cam_config.capture_frame_height()
        else:
            pass
        device = cfg.cam_config.device()
        if device == 'rpicamsrc':
            compressor = 'omxh264enc'
            tune = ' '
        elif device == 'v4l2src':
            compressor = 'x264enc'
            tune = ' tune=zerolatency '
        elif device == 'avfvideosrc':
            compressor = 'x264enc'
            tune = ' tune=zerolatency '
        comm = 'appsrc ! videoconvert ! video/x-raw,width='+str(src_width)+',height='+str(src_height)+',framerate='+str(src_framerate)+'/1 ! '+compressor+tune+'! rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host='+host+' port='+str(strm_port)+' sync=false'

        self.stream_writer = cv2.VideoWriter(comm, cv2.CAP_GSTREAMER, 0, strm_framerate, (strm_width, strm_height),True)
        self.streaming = True

        thread = Thread(target=self._stream, args=())
        thread.start()

    def end_stream(self):
        '''Stop streaming.'''
        if not self.streaming:
            raise CameraUserError('Cannot stop streaming: stream not active.')
        self.streaming = False  # stop _stream
        self.stream_writer.release()
        self.stream_writer = None

    def acquire_camera(self):
        '''Get shared access to the camera.'''
        if self.have_camera():
            raise CameraUserError('Already have camera access: cannot reacquire.')
        try:
            self.camera = mgr.global_resources.get_shared(self,"Camera")
        except mgr.ResourceError as e:
            print(str(e))
            raise CameraUserError('Could not get access to camera.')

    def release_camera(self):
        if self.have_camera():
            mgr.global_resources.release(self,"Camera")
            self.camera = None
        else:
            print ("Warning (camera): release_camera called while not acquired.")

    def have_camera(self):
        '''Check if camera has been acquired.'''
        if self.camera is not None:
            return True
        return False

    def cam_user_manual_set_released(self):
        self.camera = None


