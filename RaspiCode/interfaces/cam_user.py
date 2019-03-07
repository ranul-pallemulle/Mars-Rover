from abc import ABCMeta, abstractmethod
import coreutils.configure as cfg
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
            raise CamerUserError('Stream writer not initialised.')
        if not self.have_camera():
            raise CameraUserError('Camera not acquired: cannot stream.')

        if not self.camera.is_active():
            raise CameraUserError('Camera not active: cannot stream.')
        
        while self.streaming:
            if self.camera.is_active():
                frame = self.camera.get_frame()
            else:
                break
            if frame is not None:
                self.stream_writer.write(frame)

    def begin_stream(self, source=None):
        '''Stream source (default is direct camera output) to the specified port.'''
        if self.streaming:
            raise CameraUserError('Already streaming: cannot start new stream.')
        if not self.have_camera():
            raise CameraUserError('Camera not acquired.')
        
        host = cfg.global_config.ip_address()
        if source is None:
            cam_config = cfg.CameraConfiguration()
            strm_port = cam_config.stream_port()
            strm_framerate = cam_config.stream_framerate()
            strm_width = cam_config.stream_frame_width()
            strm_height = cam_config.stream_frame_height()

            src_framerate = cam_config.capture_framerate()
            src_width = cam_config.capture_frame_width()
            src_height = cam_config.capture_frame_height()
        else:
            pass
        op_mode = cfg.global_config.operation_mode()
        if op_mode == "RASPBERRYPI":
            compressor = 'omxh264enc'
            tune = ' '
        elif op_mode == "LAPTOP":
            compressor = 'x264enc'
            tune = ' tune=zerolatency '
        comm = 'appsrc ! videoconvert ! video/x-raw,width='+str(src_width)+',height='+str(src_height)+',framerate='+str(src_framerate)+'/1 ! '+compressor+tune+'speed-preset=superfast bitrate=8000 ! h264parse ! rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host='+host+' port='+str(strm_port)+' sync=false'

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
            self.camera = mgr.global_resources.get_shared(mgr.Camera.FEED)
        except mgr.ResourceError as e:
            print(str(e))
            raise CameraUserError('Could not get access to camera.')

    def release_camera(self):
        if self.have_camera():
            mgr.global_resources.release(mgr.Camera.FEED)
            self.camera = None
        else:
            print ("Warning (camera): release_camera called while not acquired.")

    def have_camera(self):
        '''Check if camera has been acquired.'''
        if self.camera is not None:
            return True
        return False


