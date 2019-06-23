import coreutils.configure as cfg
from coreutils.rwlock import RWLock
from resources.resource import Resource, ResourceRawError, Policy
import cv2
import numpy as np
from threading import Thread
import socket

class IPCameraError(Exception):
    pass

class IPCamera(Resource):
    '''Provides access to the camera or webcam on the device. Operational modes
     can access this by inheriting from the CameraUser interface.
     Camera access implementation uses OpenCV in combination with gstreamer.'''
    def __init__(self):
        '''Register name and access policy. Obtain settings from 
        CameraConfiguration. Initialise members.'''
        Resource.__init__(self)
        self.policy = Policy.SHARED
        self.register_name("IPCamera")
        try:
            self.host = None    # ip adddress of IP camera
            self.port = None    # port on IP camera
            # self.source = cfg.cam_config.device() # gstreamer device name
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
        self.host = socket.gethostbyname('aresdepcam.local')
        print("IP camera ip adress: {}".format(self.host))
        self.port = 5564
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

    def start_capture(self):
        '''Begin camera operation, if it is not already active.'''
        if not self.active:
            self._eval_gst_comm()
            self.cap = cv2.VideoCapture(self.gst_comm) # get camera access
            for i in range(5):
                ret, img = self.cap.read()
                self.frame = img # initialise self.frame with a valid frame
            if not ret:
                raise IPCameraError("IP Camera could not be initialised")
            else:
                print("IP Camera working")
            self.active = True  # Allow _capture loop to start                
            Thread(target=self._capture, args=()).start()
        else:
            raise IPCameraError('Camera already initialised: release before \
reinitialising.')

    def stop_capture(self):
        '''End camera operation.'''
        if self.active:
            self.active = False # Allow _capture loop to end
            self.cap.release()  # release camera from program
        else:
            raise IPCameraError('Camera already inactive: cannot deactivate.')

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
        source = 'tcpclientsrc host='+self.host+' port='+str(self.port)+ \
                 ' ! gdpdepay ! rtph264depay ! avdec_h264'
        
        # self.gst_comm = source+' ! video/x-raw,framerate='+ \
        #     str(self.framerate)+'/1,width='+str(self.frame_width)+',height='+ \
        #     str(self.frame_height)+ \
        #     ' ! videoconvert ! appsink name=opencvsink sync=false'

        self.gst_comm = source+ \
            ' ! videoconvert ! appsink name=opencvsink sync=false'
        
        print(self.gst_comm)

    def is_active(self):
        return self.active
