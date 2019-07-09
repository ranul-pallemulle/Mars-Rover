from abc import ABC, abstractmethod
from coreutils.diagnostics import Diagnostics as dg
import coreutils.configure as cfg
from interfaces.cam_user import CameraUser, CameraUserError, Streamable
from threading import Lock
import cv2
import time

class CVEngineError(Exception):
    '''Exception class raised by CVEngine'''
    pass

class CVEngine(ABC, CameraUser):
    '''Computer vision engine: has object recognition functionality.'''
    def __init__(self):
        CameraUser.__init__(self)
        self.active = False
        self.active_lock = Lock()

    def activate(self):
        try:
            self.acquire_camera()
        except CameraUserError as e:
            raise CVEngineError("CVEngine could not acquire camera: "+str(e))
        try:
            self.initialise()
        except Exception as e:
            raise CVEngineError("Initialisation failed for CVEngine '{}': ".format(self.__class__.__name__) + str(e))
        with self.active_lock:
            self.active = True

    def deactivate(self):
        with self.active_lock:
            self.active = False
        time.sleep(1)
        if self.have_camera():
            self.release_camera()
        try:
            self.deinitialise()
        except Exception as e:
            raise CVEngineError("Deinitialisation failed for CVEngine '{}': ".format(self.__class__.__name__) + str(e))

    def is_active(self):
        with self.active_lock:
            return self.active

    @classmethod
    def get_engine(cls, name):
        for x in cls.__subclasses__():
            if x.__name__ == name:
                return x()
        raise CVEngineError("No CVEngine named '{}' found".format(name))

    @abstractmethod
    def initialise(self):
        '''Any initialisation (e.g loading a haarcascades file).'''
        pass

    @abstractmethod
    def deinitialise(self):
        '''Any releasing of resources (e.g closing a file).'''
        pass
    
    @abstractmethod
    def find_obj(self):
        '''Return a bounding box (coordinates) of the object within the
current camera fram.'''
        pass


class OpenCVHaar(CVEngine, Streamable):
    
    def __init__(self):
        CVEngine.__init__(self)
        Streamable.__init__(self)

    def initialise(self):
        self.cascade = cv2.CascadeClassifier('autonomous/haarcascade_samples_hydepark_30_30.xml')#autonomous/haarcascade_samples_hydepark_30_30.xml
        
    def deinitialise(self):
        pass

    def find_obj(self):
        frame = self.camera.get_frame()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        objects = []
        try:
            objects = self.cascade.detectMultiScale(gray,1.1,50) #1.1,250 # 1.1,500
        except Exception as e:
            dg.print(str(e))
        for (x,y,w,h) in objects:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)
        self.update_frame(frame) # for streaming
        return objects
    
    def stream_port(self):
        port = cfg.auto_config.stream_port()
        return port

    def stream_framerate(self):
        frate = cfg.auto_config.stream_framerate()
        return frate
    
    def stream_frame_width(self):
        width = cfg.auto_config.stream_frame_width()
        return width
    
    def stream_frame_height(self):
        height = cfg.auto_config.stream_frame_height()
        return height
    
    def capture_framerate(self):
        frate = cfg.auto_config.capture_framerate()
        return frate
    
    def capture_frame_width(self):
        width = cfg.auto_config.capture_frame_width()
        return width
    
    def capture_frame_height(self):
        height = cfg.auto_config.capture_frame_height()
        return height
