from abc import ABC, abstractmethod
from autonomous.auto_mode import Goal, GoalError
from coreutils.diagnostics import Diagnostics as dg
from interfaces.cam_user import CameraUser, CameraUserError
from threading import Thread, Lock
import time
import cv2

class CVEngine(ABC, CameraUser):
    '''Computer vision engine: has object recognition functionality.'''
    def __init__(self):
        CameraUser.__init__(self)
        self.active = False
        self.active_lock = Lock()

    def activate(self):
        self.initialise()
        self.acquire_camera()
        with self.active_lock:
            self.active = True

    def deactivate(self):
        with self.active_lock:
            self.active = False
        time.sleep(1)
        self.release_camera()

    def is_active(self):
        with self.active_lock:
            return self.active

    @abstractmethod
    def initialise(self):
        '''Any initialisation (e.g loading a haarcascades file).'''
        pass
    
    @abstractmethod
    def find_obj(self):
        '''Return a bounding box (coordinates) of the object within the
current camera fram.'''
        pass


class OpenCVHaar(CVEngine):

    def initialise(self):
        self.cascade = cv2.CascadeClassifier('autonomous/haarcascade_frontalface_default.xml')
            
    def find_obj(self):
        try:
            frame = self.get_camera_frame()
        except CameraUserError as e:
            dg.print(str(e))
            self.deactivate()
            return
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        objects = []
        try:
            objects = self.cascade.detectMultiScale(gray)
        except Exception as e:
            dg.print(str(e))
        return objects

        
class Samples(Goal):
    '''Autonomous mode goal for picking up samples.'''
    
    def __init__(self):
        Goal.__init__(self)
        self.register_name("Samples")
        self.cv_engine = OpenCVHaar()     # TODO: get specific cv_engine
                                        # from config file
    def run(self):
        thread = Thread(target=self.pick_samples, args=[])
        thread.start()

    def cleanup(self):
        self.cv_engine.deactivate()

    def pick_samples(self):
        self.cv_engine.activate()

        while self.cv_engine.is_active():
            objs = self.cv_engine.find_obj()
            dg.print(objs)
            
