import coreutils.configure as cfg
import coreutils.resource_manager as mgr
from autonomous.auto_mode import Goal, GoalError
from autonomous.cv_engine import OpenCVHaar
from interfaces.actuator import Actuator, ActuatorError
from threading import Thread
import time
import cv2

class Samples(Goal, Actuator):
    '''Autonomous mode goal for picking up samples.'''
    
    def __init__(self):
        Goal.__init__(self)
        Actuator.__init__(self)
        self.register_name("Samples")
        self.cv_engine = OpenCVHaar()
        self.ultrasound = None
        self.k1 = 1.0
        self.xval = 0
        self.yval = 0
        self.angle_bottom = 0
        self.angle_middle = 0
        self.angle_top = 0
        self.angle_gripper = 0
        self.rate_list = []
                                        
    def run(self):
        self.acquire_motors("Wheels")
        self.acquire_motors("Arm")
        if not self.have_acquired("Wheels") or not self.have_acquired("Arm"):
            raise GoalError("Could not get access to motors.")
        self.ultrasound = mgr.global_resources.get_shared("Ultrasound")
        if self.ultrasound is None:
            raise GoalError("Could not get access to ultrasound sensor.")
        thread_samples = Thread(target=self.pick_samples, args=[])
        thread_samples.start()
        self.begin_actuate()

    def cleanup(self):
        self.cv_engine.deactivate()
        if self.have_acquired("Wheels"):
            self.release_motors("Wheels")
        if self.have_acquired("Arm"):
            self.release_motors("Arm")
        if self.ultrasound is not None:
            mgr.global_resources.release("Ultrasound")
        
    def get_values(self, motor_set):
        if motor_set == "Wheels":
            with self.condition:
                return (self.xval, self.yval)
        elif motor_set == "Arm":
            with self.condition:
                return (self.angle_gripper, self.angle_top, self.angle_middle, self.angle_bottom)
        
    def pid_wheels(self, relx, rely):
        with self.condition:
            self.xval = self.k1*relx
            self.yval = self.k1*rely
            # print("xval: {}, yval: {}".format(self.xval,self.yval))
            self.condition.notify()
            
    def pid_arm_y(self, rely):
        with self.condition:
            self.xval = 0
            self.yval = 0
            # print("xval: {}, yval: {}".format(self.xval,self.yval))
            self.condition.notify()
            
    def pid_arm_height(self, height):
        with self.condition:
            self.xval = 0
            self.yval = 0
            # print("xval: {}, yval: {}".format(self.xval,self.yval))
            self.condition.notify()
    
    def pick_samples(self):
        self.cv_engine.activate()
        sample_bbox = []
        frame_width = cfg.cam_config.capture_frame_width()
        frame_height = cfg.cam_config.capture_frame_height()
        centre_x = frame_width/2
        centre_y = frame_height/2
        while self.cv_engine.is_active():
            t0 = time.time()
            sample_bbox = self.cv_engine.find_obj() # sample bounding box
            t1 = time.time()
            self.rate_list.append(1.0/(t1-t0))
            if len(self.rate_list) == 100:
                print("Image processing rate: {} FPS".format(sum(self.rate_list)/100))
                self.rate_list = []
            if len(sample_bbox) == 0:
                continue
            else:
                x,y = (sample_bbox[0][0]+sample_bbox[0][2]/2,
                          sample_bbox[0][1]+sample_bbox[0][3]/2)
                z = self.ultrasound.read()
                relx = (x-centre_x)*100.0/centre_x
                rely = -(y-centre_y)*100.0/centre_y
                print("{}, {}, {}".format(relx, rely, z))
                if abs(relx) > 5 or abs(rely) > 5:
                    self.pid_wheels(relx,rely)
                else:
                    self.pid_arm_y(rely)
                    self.pid_arm_height(z)
