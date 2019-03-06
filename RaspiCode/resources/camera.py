import coreutils.configure as cfg
from resources.resource import Resource, Policy
import cv2
from threading import Thread

class CameraError(Exception):
    pass

class Camera(Resource):
    def __init__(self):
        Resource.__init__(self)
        self.policy = Policy.SHARED
        self.register_name("Camera")
        
        self.running = False
        self.source = cfg.cam_config.device()
        self.framerate = cfg.cam_config.capture_framerate()
        self.frame_width = cfg.cam_config.capture_frame_width()
        self.frame_height = cfg.cam_config.capture_frame_height()
        self.gst_comm = None
        # self.op_mode = cfg.global_config.operation_mode()
        # if self.op_mode == "RASPBERRYPI" or self.op_mode == "LAPTOP":
        #     self.source = 'v4l2src'
        # elif self.op_mode == "MAC":
        #     self.source = 'avfvideosrc'
        self._eval_gst_comm()
        self.cap = None
        self.ret = None
        self.frame = None

    def _capture(self):
        while True:
            self.ret,self.frame = self.cap.read()
            if not self.ret:
                break 

    def start(self):
        self.cap = cv2.VideoCapture(self.gst_comm)
        thread = Thread(target=self._capture, args=())
        thread.start()

    def stop(self):
        if self.cap is not None:
            self.cap.release()
        self.frame = None

    def get_frame(self):
        if self.ret:
            return self.frame
        return None
            
    def _eval_gst_comm(self):
        self.gst_comm = self.source+' ! video/x-raw,framerate='+str(self.framerate)+'/1,width='+str(self.frame_width)+',height='+str(self.frame_height)+' ! videoconvert ! appsink name=opencvsink sync=false'

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

