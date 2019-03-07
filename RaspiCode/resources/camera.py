import coreutils.configure as cfg
from resources.resource import Resource, Policy
import cv2
from threading import Thread
from sys import platform

class CameraError(Exception):
    pass

class Camera(Resource):
    def __init__(self):
        self.framerate = cam_config.capture_framerate()
        self.frame_width=cam_config.capture_frame_width()
        self.frame_height=cam_config.capture_frame_height()
        self.gst_comm = None
        self.op_mode = cfg.global_config.operation_mode()
        if self.op_mode == "RASPBERRYPI":
            # self.source = "v4l2src"
            self.source = "raspivid"
        elif self.op_mode == "LAPTOP":
            if platform == "darwin":
                self.source = 'avfvideosrc'
            else:
                self.source = "v4l2src"
        else:
            raise CameraError('Unknown operation mode: no availabe video source.')
        self.cap = None
        self.active = False

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
        ret,frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return frame
        return None
            
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

