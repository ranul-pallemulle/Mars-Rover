import coreutils.configure as cfg
from coreutils.rwlock import RWLock
from resources.resource import Resource, ResourceRawError, Policy
import cv2
import numpy as np
from threading import Thread, Lock
from multiprocessing import Process, Queue

class CameraError(Exception):
    pass

class Camera(Resource):
    '''Provides access to the camera or webcam on the device. Operational modes
     can access this by inheriting from the CameraUser interface.
     Camera access implementation uses OpenCV in combination with gstreamer.'''
    def __init__(self):
        '''Register name and access policy. Obtain settings from 
        CameraConfiguration. Initialise members.'''
        Resource.__init__(self)
        self.policy = Policy.SHARED
        self.register_name("Camera")
        try:
            self.source = cfg.cam_config.device() # gstreamer device name
            self.framerate = cfg.cam_config.capture_framerate()
            self.frame_width=cfg.cam_config.capture_frame_width()
            self.frame_height=cfg.cam_config.capture_frame_height()
        except cfg.ConfigurationError as e:
            raise ResourceRawError(str(e))
        self.gst_comm = None    # string corresponding to gstreamer pipe
        self.cap = None         # opencv capture object
        self.active = False
        self.camlock = RWLock() # allow multiple readers, single writer
        self.frame = np.zeros(3)       # current camera frame

    def shared_init(self):
        '''Called by resource manager when camera is acquired for the first
        time.
        '''
        self.start_capture()

    def shared_deinit(self):
        '''Called by resource manager when the last user releases the camera.'''
        self.stop_capture()

    def _capture(self):
        '''Run in a separate thread. While camera is active, store the current
        camera frame.'''
        while self.active:
            ret,img = self.cap.read()
            if ret:             # capture was successful
                self.camlock.acquire_write()
                self.frame = img
                self.camlock.release()

    def _cv2_videocapture_wrapper(self,timeout=5):
        timeout_over = False
        timeout_lock = Lock()
        initialised = False
        init_lock = Lock()
        def _wait_for_cap():
            import time
            nonlocal timeout_over
            time.sleep(timeout)
            with timeout_lock:
                timeout_over = True
        def _init_cap():
            nonlocal initialised
            self.cap = cv2.VideoCapture(self.gst_comm)
            with init_lock:
                initialised = True
        timeout_thread = Thread(target=_wait_for_cap, args=())
        cap_thread = Thread(target=_init_cap, args=())
        cap_thread.daemon = True
        timeout_thread.start()
        cap_thread.start()
        while True:
            with timeout_lock:
                if timeout_over:
                    return False
            with init_lock:
                if initialised:
                    return True

    def start_capture(self):
        '''Begin camera operation, if it is not already active.'''
        if not self.active:
            self._eval_gst_comm()
            # self.cap = cv2.VideoCapture(self.gst_comm) # get camera access
            cam_initialised = self._cv2_videocapture_wrapper()
            if not cam_initialised:
                raise CameraError('Error in argument to cv2.VideoCapture: check camera settings.')
            if not self.cap.isOpened():
                raise CameraError('Error in argument to cv2.VideoCapture: check camera settings.')
            for i in range(5):
                ret, img = self.cap.read()
                self.frame = img # initialise self.frame with a valid frame
            self.active = True  # Allow _capture loop to start                
            Thread(target=self._capture, args=()).start()
        else:
            raise CameraError('Camera already initialised: release before \
reinitialising.')

    def stop_capture(self):
        '''End camera operation.'''
        if self.active:
            self.active = False # Allow _capture loop to end
            self.cap.release()  # release camera from program
        else:
            raise CameraError('Camera already inactive: cannot deactivate.')

    def get_frame(self):
        '''If camera is active, return (a deep copy of) the current frame. Else,
        throw an exception.'''
        # if self.active:
        self.camlock.acquire_read()
        frame = self.frame.copy()
        self.camlock.release()
        return frame
        # raise CameraError('Camera not active: cannot get frame.')
            
    def _eval_gst_comm(self):
        '''Evaluate a gstreamer pipeline string to initialise the OpenCV 
        VideoCapture object with.'''
        self.gst_comm = self.source+' ! video/x-raw,framerate='+ \
            str(self.framerate)+'/1,width='+str(self.frame_width)+',height='+ \
            str(self.frame_height)+ \
            ' ! videoconvert ! appsink name=opencvsink sync=false'

    def is_active(self):
        return self.active
