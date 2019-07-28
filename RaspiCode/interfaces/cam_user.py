from abc import ABC, ABCMeta, abstractmethod
import coreutils.configure as cfg
import coreutils.resource_manager as mgr
from coreutils.diagnostics import Diagnostics as dg
from coreutils.rwlock import RWLock
import cv2
import numpy as np
from threading import Thread
import time

class CameraUserError(Exception):
    '''Exception class that will be raised by classes implementing 
    CameraUser.'''
    pass

class CameraUser:
    '''Provides an interface to the camera resource.'''
    __metaclass__ = ABCMeta


    def __init__(self):
        self.camera = None
        self.stream_writer = None
        self.streaming = False
        self.framerate_list = []


    def _stream(self):
        '''Run in separate thread - cannot raise exceptions.'''
        if self.stream_writer is None:
            raise CameraUserError('Stream writer not initialised.')
        if not self.have_camera():
            raise CameraUserError('Camera not acquired: cannot stream.')

        if not self.camera.is_active():
            raise CameraUserError('Camera not active: cannot stream.')
        
        while self.streaming:
            t0 = time.time()
            frame = self.camera.get_frame()
            self.stream_writer.write(frame)
            t1 = time.time()
            self.framerate_list.append(1.0/(t1-t0))
            if len(self.framerate_list) == 100:
                # dg.print("Stream framerate: {} FPS".format(
                #     sum(self.framerate_list)/100))
                self.framerate_list = []
                
    def _stream_nondefault(self, source):
        if self.stream_writer is None:
            raise CameraUserError('Stream writer not initialised.')
        
        while self.streaming:
            t0 = time.time()
            frame = source.get_frame()
            self.stream_writer.write(frame)
            t1 = time.time()
            self.framerate_list.append(1.0/(t1-t0))
            if len(self.framerate_list) == 100:
                # dg.print("(Non-default) stream framerate: {} FPS".format(
                #     sum(self.framerate_list)/100))
                self.framerate_list = []

    def begin_stream(self, source=None):
        '''Stream source (default is direct camera output) to the specified \
        port.'''
        if self.streaming:
            raise CameraUserError('Already streaming: cannot start new stream.')
        if not self.have_camera():
            raise CameraUserError('Camera not acquired.')
        
        host = cfg.overall_config.get_connected_ip()
        if source is None:
            strm_port = cfg.cam_config.stream_port()
            strm_framerate = cfg.cam_config.stream_framerate()
            strm_width = cfg.cam_config.stream_frame_width()
            strm_height = cfg.cam_config.stream_frame_height()

            src_framerate = cfg.cam_config.capture_framerate()
            src_width = cfg.cam_config.capture_frame_width()
            src_height = cfg.cam_config.capture_frame_height()
        else:
            strm_port = source.stream_port()
            strm_framerate = source.stream_framerate()
            strm_width = source.stream_frame_width()
            strm_height = source.stream_frame_height()
            
            src_framerate = source.capture_framerate()
            src_width = source.capture_frame_width()
            src_height = source.capture_frame_height()
            
        device = cfg.cam_config.device()
        if device == 'rpicamsrc':
            compressor = 'omxh264enc'
            tune = ' '
        elif device == 'v4l2src' or device == 'avfvideosrc' \
            or device == "autovideosrc":
            compressor = 'x264enc'
            tune = ' tune=zerolatency '
        comm = 'appsrc ! videoconvert ! video/x-raw,width='+str(src_width)+\
            ',height='+str(src_height)+',framerate='+str(src_framerate)+\
            '/1,format=I420 ! '+compressor+tune+'! rtph264pay config-interval=1 pt=96 ! \
gdppay ! tcpserversink host='+host+' port='+str(strm_port)+' sync=false'

        self.stream_writer = cv2.VideoWriter(comm, cv2.CAP_GSTREAMER, 0, 
                            strm_framerate, (strm_width, strm_height),True)
        self.streaming = True
        
        if source is None:
            thread = Thread(target=self._stream, args=())
        else:
            thread = Thread(target=self._stream_nondefault, args=[source])
        thread.start()
        dg.print("Using camera device '{}' and encoder '{}'".format(device,compressor))
        dg.print("Streaming on IP address {} and port {}".format(host,strm_port))

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
            raise CameraUserError('Already have camera access: cannot \
reacquire.')
        try:
            self.camera = mgr.global_resources.get_shared("Camera")
        except mgr.ResourceError as e:
            dg.print(str(e))
            raise CameraUserError('Could not get access to camera.')

    def release_camera(self):
        if self.have_camera():
            mgr.global_resources.release("Camera")
            self.camera = None
        else:
            dg.print ("Warning (camera): release_camera called while not \
acquired.")

    def have_camera(self):
        '''Check if camera has been acquired.'''
        if self.camera is not None:
            return True
        return False

class Streamable(ABC):
    def __init__(self):
        self.frame_lock = RWLock()
        self.frame = np.zeros(3)
        
    def get_frame(self):
        self.frame_lock.acquire_read()
        frame = self.frame.copy()
        self.frame_lock.release()
        return frame

    def update_frame(self, frame):
        self.frame_lock.acquire_write()
        self.frame = frame
        self.frame_lock.release()
  
    @abstractmethod
    def stream_port(self):
        pass

    @abstractmethod
    def stream_framerate(self):
        pass

    @abstractmethod
    def stream_frame_width(self):
        pass
    
    @abstractmethod
    def stream_frame_height(self):
        pass

    @abstractmethod
    def capture_framerate(self):
        pass

    @abstractmethod
    def capture_frame_width(self):
        pass

    @abstractmethod
    def capture_frame_height(self):
        pass
