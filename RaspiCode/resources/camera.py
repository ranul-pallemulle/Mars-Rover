import coreutils.configure as cfg
from resources.resource import Resource, ResourceRawError, Policy
import cv2
from threading import Lock
from sys import platform

class CameraError(Exception):
    pass

class Camera(Resource):
    def __init__(self):
        Resource.__init__(self)
        self.policy = Policy.SHARED
        self.register_name("Camera")
        try:
            self.source = cfg.cam_config.device()
            self.framerate = cfg.cam_config.capture_framerate()
            self.frame_width=cfg.cam_config.capture_frame_width()
            self.frame_height=cfg.cam_config.capture_frame_height()
        except cfg.ConfigurationError as e:
            raise ResourceRawError(str(e))
        self.gst_comm = None
        self.cap = None
        self.active = False
        self.camlock = Lock()

    def shared_init(self):
       self.start_capture()

    def shared_deinit(self):
        self.stop_capture()

    def start_capture(self):
        if self.cap is None and not self.active:
            self._eval_gst_comm()
            self.cap = cv2.VideoCapture(self.gst_comm)
            self.active = True
        else:
            raise CameraError('Camera already initialised: release before reinitialising.')

    def stop_capture(self):
        if self.cap is not None and self.active:
            self.cap.release()
            self.cap = None
            self.active = False
        else:
            raise CameraError('Camera already released: cannot release.')

    def get_frame(self):
        if self.active:
            with self.camlock:
                ret,frame = self.cap.read()
            if ret:
                return frame
            return None
        raise CameraError('Camera not active: cannot get frame.')
            
    def _eval_gst_comm(self):
        self.gst_comm = self.source+' ! video/x-raw,framerate='+str(self.framerate)+'/1,width='+str(self.frame_width)+',height='+str(self.frame_height)+' ! videoconvert ! appsink name=opencvsink sync=false'

    def is_active(self):
        return self.active

    def get_framerate(self):
        return self.framerate

    def get_frame_height(self):
        return self.frame_height

    def get_frame_width(self):
        return self.frame_width

    def set_framerate(self, framerate):
        self.framerate = framerate
        self._eval_gst_comm

    def set_frame_height(self, frame_height):
        self.frame_height = frame_height
        self._eval_gst_comm

    def set_frame_width(self, frame_width):
        self.frame_width = frame_width
        self._eval_gst_comm

