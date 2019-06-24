import coreutils.configure as cfg
import coreutils.resource_manager as mgr
from autonomous.auto_mode import Goal, GoalError
from autonomous.cv_engine import OpenCVHaar
from interfaces.actuator import Actuator, ActuatorError
from threading import Thread
import math
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
        self.rate_list = []
        self.smooth_param = 10 # divide angle changes into this many steps
        # wheels variables and parameters
        self.k1 = 1.0
        self.xval = 0
        self.yval = 0
        # arm variables and parameters
        self.arm_l1 = 1 # length of first arm segment
        self.arm_l2 = 1 # length of second arm segment
        self.arm_l3 = 1 # length of gripper segment
        self.servo_limit = math.pi/2
        self.angle_bottom = 0 # actual servo angles
        self.angle_middle = 0
        self.angle_top = 0
        self.angle_gripper = 0
        self.gripper_x = self.arm_l1 + self.arm_l2 + self.arm_l3 # gripper tip x position relative to base servo
        self.gripper_y = 0
        self.gripper_gamma = 0 # gripper angle relative to ground
                                        
    def run(self):
        self.acquire_motors("Wheels")
        self.acquire_motors("Arm")
        if not self.have_acquired("Wheels") or not self.have_acquired("Arm"):
            raise GoalError("Could not get access to motors.")
        self.ultrasound = mgr.global_resources.get_shared("Ultrasound")
        if self.ultrasound is None:
            raise GoalError("Could not get access to ultrasound sensor.")
        self.set_initial_arm_position()
        self.cv_engine.activate()
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
            self.ultrasound = None
        
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
            self.condition.notify() # actuate

    def set_initial_arm_position(self):
        thet1,thet2,thet3 = self._inverse_kinematics(self.gripper_x,self.gripper_y,self.gripper_gamma)
        with self.condition:
            self.angle_bottom = thet1
            self.angle_middle = thet2
            self.angle_top = thet3
            self.condition.notify()

    def _inverse_kinematics(self, x, y, gamma):
        '''
        x and y are measured relative to the base servo. They are the coordinates of the tip of the gripper.
        positive x is in the forward driving direction, positive y is away from the ground. 
        gamma is the orientation of the gripper. gamma=0 means the gripper segment is parallel to the ground.
        Note that self.gamma is the current orientation, while gamma is the orientation to set.
        gamma=-pi/2 means the gripper is pointing at the ground.
        angles theta1,theta2,theta3 are the servo angles at base,middle,top along the arm.
        they are assumed to be -pi/2 < theta < pi/2.
        angles returned are in radians.
        '''
        arm_l1 = self.arm_l1
        arm_l2 = self.arm_l2
        arm_l3 = self.arm_l3

        x2R = x - arm_l3 * math.cos(gamma) # x for the tip of the second segment
        y2R = y - arm_l3 * math.sin(gamma) # y for the tip of the second segment
        ct2 = ((x2R**2 + y2R**2) - (arm_l1**2 + arm_l2**2))/(2*arm_l1*arm_l2) # cos(theta2)
        if gamma > 0: # gripper looking up
            thet2 = math.acos(ct2) # elbow down configuration for 2R manipulator problem
        else:
            thet2 = -math.acos(ct2) # elbow up configuration
        st2 = math.sin(thet2)

        A = arm_l1 + arm_l2*ct2
        B = arm_l2*st2
        AB2 = A**2 + B**2
        #ct1 = (x2R*A + y2R*B)/AB2
        st1 = (y2R*A - x2R*B)/AB2
        thet1 = math.asin(st1)

        thet3 = gamma - thet2 - thet1
        return (thet1, thet2, thet3)

    def _smooth_update(self, theta1, theta2, theta3, gripper):
        ''' Moves the arm in small increments until the final goal is reached. '''
        dthet1 = (theta1 - self.angle_bottom) / self.smooth_param
        dthet2 = (theta2 - self.angle_middle) / self.smooth_param
        dthet3 = (theta3 - self.angle_top) / self.smooth_param
        dgrip = (gripper - self.angle_gripper) / self.smooth_param
        for x in range(self.smooth_param):
            new_thet1 = self.angle_bottom + dthet1
            new_thet2 = self.angle_middle + dthet2
            new_thet3 = self.angle_top + dthet3
            new_gripper = self.angle_gripper + dgrip
            with self.condition:
                if abs(new_thet1) < self.servo_limit:
                    self.angle_bottom = new_thet1
                if abs(new_thet2) < self.servo_limit:
                    self.angle_middle = new_thet2
                if abs(new_thet3) < self.servo_limit:
                    self.angle_top = new_thet3
                if abs(new_gripper) < self.servo_limit:
                    self.angle_gripper = new_gripper
                self.condition.notify()
        self.gripper_gamma = self.angle_bottom + self.angle_middle + self.angle_top
        self.gripper_x = self.arm_l1*math.cos(self.angle_bottom) + \
                         self.arm_l2*math.cos(self.angle_bottom + self.angle_middle) + \
                         self.arm_l3*math.cos(self.angle_bottom + self.angle_middle + self.angle_top)
        self.gripper_y = self.arm_l1*math.sin(self.angle_bottom) + \
                         self.arm_l2*math.sin(self.angle_bottom + self.angle_middle) + \
                         self.arm_l3*math.sin(self.angle_bottom + self.angle_middle + self.angle_top)
        

    def _slight_change(self,theta1, theta2, theta3, gripper):
        ''' Moves the arm a certain amount towards the final position '''
        dthet = [               # angle changes required
            theta1 - self.angle_bottom,
            theta2 - self.angle_middle,
            theta3 - self.angle_top,
            gripper - self.angle_gripper
        ]
        sign = lambda delta: delta and (1,-1)[delta < 0] # 0 if delta==0 otherwise +-1        
        for idx, delta in enumerate(dthet):
            if abs(delta) > math.radians(50):
                dthet[idx] = sign(delta)*math.radians(10)
            elif abs(delta) > math.radians(10):
                dthet[idx] = sign(delta)*math.radians(4)
            elif abs(delta) > math.radians(5):
                dthet[idx] = sign(delta)*math.radians(2)
            else:
                dthet[idx] = sign(delta)*math.radians(1) # if delta==0, sign==0 and dthet[idx]==0
        new_thet1 = self.angle_bottom + dthet[0]
        new_thet2 = self.angle_middle + dthet[1]
        new_thet3 = self.angle_top + dthet[2]
        new_gripper = self.angle_gripper + dthet[3]
        with self.condition:
            if abs(new_thet1) < self.servo_limit:
                self.angle_bottom = new_thet1
            else:
                self.angle_bottom = sign(new_thet1)*self.servo_limit
            if abs(new_thet2) < self.servo_limit:
                self.angle_middle = new_thet2
            else:
                self.angle_middle = sign(new_thet2)*self.servo_limit
            if abs(new_thet3) <= self.servo_limit:
                self.angle_top = new_thet3
            else:
                self.angle_top = sign(new_thet3)*self.servo_limit
            if abs(new_gripper) < self.servo_limit:
                self.angle_gripper = new_gripper
            else:
                self.angle_gripper = sign(new_gripper)*self.servo_limit
            self.condition.notify()
        self.gripper_gamma = self.angle_bottom + self.angle_middle + self.angle_top
        self.gripper_x = self.arm_l1*math.cos(self.angle_bottom) + \
                         self.arm_l2*math.cos(self.angle_bottom + self.angle_middle) + \
                         self.arm_l3*math.cos(self.angle_bottom + self.angle_middle + self.angle_top)
        self.gripper_y = self.arm_l1*math.sin(self.angle_bottom) + \
                         self.arm_l2*math.sin(self.angle_bottom + self.angle_middle) + \
                         self.arm_l3*math.sin(self.angle_bottom + self.angle_middle + self.angle_top)


    def pid_arm(self, relz, rely):
        ''' 
        Perform a single iteration of PID control on the arm.
        Input is the coordinates of the sample in the gripper frame of reference.
        The output is a step change in servo angles to move the arm closer (reduce relz,rely)
        '''
        # stop driving
        # with self.condition:
        #     self.xval = 0
        #     self.yval = 0
        #     self.condition.notify()

        # get change of gamma needed to align with sample
        del_gamma = math.atan2(rely,relz+self.arm_l3)
        new_gamma = self.gripper_gamma + del_gamma

        # get sample coordinates in rover frame (origin at base servo)
        xs = self.gripper_x + relz*math.cos(self.gripper_gamma) - rely*math.sin(self.gripper_gamma)
        ys = self.gripper_y + relz*math.sin(self.gripper_gamma) + rely*math.sin(self.gripper_gamma)

        # get angle changes needed using inverse kinematics and set them
        thet1,thet2,thet3 = self._inverse_kinematics(xs,ys,new_gamma)
        # self._smooth_update(thet1,thet2,thet3,0)
        self._slight_change(thet1,thet2,thet3,0)
        
    
    def pick_samples(self):
        sample_bbox = [] # coordinates of bounding box around detected sample 
        frame_width = cfg.cam_config.capture_frame_width()
        frame_height = cfg.cam_config.capture_frame_height()
        centre_x = frame_width/2 # coordinates of centre of the frame
        centre_y = frame_height/2
        while self.cv_engine.is_active():
            t0 = time.time()
            sample_bbox = self.cv_engine.find_obj() # get bounding box
            t1 = time.time()
            self.rate_list.append(1.0/(t1-t0))
            if len(self.rate_list) == 100:
                print("Image processing rate: {} FPS".format(sum(self.rate_list)/100))
                self.rate_list = []
            if len(sample_bbox) == 0: # no sample found
                continue
            else:
                # sample found - use only one if multiple detected (sample_bbox[0])
                x,y = (sample_bbox[0][0]+sample_bbox[0][2]/2,
                          sample_bbox[0][1]+sample_bbox[0][3]/2)
                relz = self.ultrasound.read() # get height from the ground
                relx = (x-centre_x)*100.0/centre_x # percentage distance from centre of frame
                rely = -(y-centre_y)*100.0/centre_y
                print("{}, {}, {}".format(relx, rely, relz))
                if abs(relx) > 5 or abs(rely) > 5: # get the sample near the centre of the frame
                    self.pid_wheels(relx,rely)
                else: # sample is near the centre of the frame - move arm to pick it up
                    self.pid_wheels(0,0)
                    self.pid_arm(relz,rely)
