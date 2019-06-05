from abc import ABC, abstractmethod
import coreutils.configure as cfg
from autonomous.auto_mode import Goal, GoalError
from coreutils.diagnostics import Diagnostics as dg
from interfaces.cam_user import CameraUser, CameraUserError
from interfaces.actuator import Actuator, ActuatorError
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
        if self.have_camera():
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

        
class Samples(Goal, Actuator):
    '''Autonomous mode goal for picking up samples.'''
    
    def __init__(self):
        Goal.__init__(self)
        Actuator.__init__(self)
        self.register_name("Samples")
        self.cv_engine = OpenCVHaar()
        self.k1 = 1.0
        self.xval = 0
        self.yval = 0
        self.angle_bottom = 0
        self.angle_middle = 0
        self.angle_top = 0
        self.angle_gripper = 0
                                        
    def run(self):
        self.acquire_motors("Wheels")
        self.acquire_motors("Arm")
        if not self.have_acquired("Wheels") or not self.have_acquired("Arm"):
            raise GoalError("Could not get access to motors.")
        thread_samples = Thread(target=self.pick_samples, args=[])
        thread_samples.start()
        self.begin_actuate()

    def cleanup(self):
        self.cv_engine.deactivate()
        if self.have_acquired("Wheels"):
            self.release_motors("Wheels")
        if self.have_acquired("Arm"):
            self.release_motors("Arm")
        
    def get_values(self, motor_set):
        if motor_set == "Wheels":
            with self.condition:
                return (self.xval, self.yval)
        elif motor_set == "Arm":
            with self.condition:
                return (self.angle_gripper, self.angle_top, self.angle_middle, self.angle_bottom)
        
    def pid_wheels(self, relx):
        with self.condition:
            self.xval = self.k1*relx
            self.yval = 0
            self.condition.notify()
            
    def pid_arm_y(self, rely):
        with self.condition:
            self.xval = 0
            self.yval = 0
            self.condition.notify()
            
    def pid_arm_height(self, height):
        with self.condition:
            self.xval = 0
            self.yval = 0
            self.condition.notify()
    
    def pick_samples(self):
        self.cv_engine.activate()
        sample_bbox = []
        frame_width = cfg.cam_config.capture_frame_width()
        frame_height = cfg.cam_config.capture_frame_height()
        centre_x = frame_width/2
        centre_y = frame_height/2
        while self.cv_engine.is_active():
            sample_bbox = self.cv_engine.find_obj() # sample bounding box
            if len(sample_bbox) == 0:
                continue
            else:
                x,y = (sample_bbox[0][0]+sample_bbox[0][2]/2,
                          sample_bbox[0][1]+sample_bbox[0][3]/2)
                z = sample_bbox[0][2]
                relx = (x-centre_x)*100.0/centre_x
                rely = (y-centre_y)*100.0/centre_y
                print("{}, {}".format(relx, rely))
                if abs(relx) > 1:
                    self.pid_wheels(relx)
                else:
                    self.pid_arm_y(rely)
                    self.pid_arm_height(z)
