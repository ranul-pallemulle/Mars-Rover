from interfaces.actuator import Actuator, ActuatorError
from coreutils.diagnostics import Diagnostics as dg
import math

class ControllerError(Exception):
    '''Exception class for controllers'''
    pass

class IK3RArmController(Actuator):
    '''Inverse kinematics robotic arm controller for 3-rotation planar
    manipulator.'''

    def __init__(self,
                 l1 = 1, l2 = 1, l3 = 1,
                 thet1 = 0, thet2 = 0, thet3 = 0, gripper = 0):
        Actuator.__init__(self)
        self.arm_l1 = l1         # lengths of arm segments (cm)
        self.arm_l2 = l2
        self.arm_l3 = l3
        self.angle_bottom = thet1   # servo angles (degrees)
        self.angle_middle = thet2
        self.angle_top = thet3
        self.angle_gripper = gripper
        self.ref_x = 0          # reference coordinates (if unset,
                                # everything is measured relative to
                                # base servo hinge)
        self.ref_y = 0
        self.end_x = 0          # coordinates of free end
        self.end_y = 0
        self.gamma = 0          # inclination of end segment to
                                # horizon (radians)

    def get_values(self, motor_set):
        with self.condition:
            return (self.angle_gripper, self.angle_top,
                    self.angle_middle, self.angle_bottom)

    def activate(self):
        self.acquire_motors("Arm")
        if not self.have_acquired("Arm"):
            dg.print("Cannot access arm motors for inverse kinematics.")
        self.begin_actuate()
        with self.condition:
            self.condition.notify() # provide initial angles to motors
        self.end_x, self.end_y, self.gamma = self._forward_kinematics(
            self.angle_bottom, self.angle_middle, self.angle_top)

        
    def deactivate(self):
        if self.have_acquired("Arm"):
            self.release_motors("Arm")

    def set_reference(self,x,y):
        '''Set reference coordinates. 0,0 refer to the base servo
        hinge.'''
        self.ref_x = x
        self.ref_y = y

    def set_position(self, x, y, gamma):
        thet1, thet2, thet3 = self._inverse_kinematics(x,y,gamma)
        with self.condition:
            self.angle_bottom = thet1
            self.angle_middle = thet2
            self.angle_top = thet3
            self.condition.notify()

    def _forward_kinematics(self, thet1, thet2, thet3):
        end_x = \
            self.arm_l1*math.cos(math.radians(thet1)) +\
            self.arm_l2*math.cos(math.radians(thet1) +\
                                 math.radians(thet2)) +\
            self.arm_l3*math.cos(math.radians(thet1) +\
                                 math.radians(thet2) +\
                                 math.radians(thet3))
        end_y = \
            self.arm_l1*math.sin(math.radians(thet1)) +\
            self.arm_l2*math.sin(math.radians(thet1) +\
                                 math.radians(thet2)) +\
            self.arm_l3*math.sin(math.radians(thet1) +\
                                 math.radians(thet2) +\
                                 math.radians(thet3))
        gamma = \
            math.radians(self.angle_bottom +\
                         self.angle_middle +\
                         self.angle_top)
        return (end_x,end_y,gamma)

    def _inverse_kinematics(self, x, y, gamma):
        '''Obtain angles needed to bring the the free end of the arm
        to x,y with inclination gamma. x and y provided must be
        relative to self.ref_x, self.ref_y. gamma is measured in
        radians. Raises exception if unreachable.'''
        arm_l1 = self.arm_l1
        arm_l2 = self.arm_l2
        arm_l3 = self.arm_l3
        xfb = x + self.ref_x    # x from base servo hinge
        yfb = y + self.ref_y    # y from base servo hinge

        # first evaluate coordinates of the end of second arm segment
        x2R = xfb - arm_l3 * math.cos(gamma)
        y2R = yfb - arm_l3 * math.sin(gamma)
        ct2 = (((x2R**2) + (y2R**2)) - ((arm_l1**2) + (arm_l2**2)))\
            /(2*arm_l1*arm_l2) # cos(theta2)

        if gamma > 0:
            thet2 = math.acos(ct2) # may raise exception if unreachable
        else:
            thet2 = -math.acos(ct2)
        st2 = math.sin(thet2)

        A = arm_l1 + arm_l2*ct2
        B = arm_l2*st2
        AB2 = A**2 + B**2
        ct1 = (x2R*A + y2R*B)/AB2
        st1 = (y2R*A - x2R*B)/AB2
        if ct1 > 0:             # principle angles
            thet1 = math.asin(st1)
        else:
            thet1 = math.pi - math.asin(st1)

        thet3 = gamma - thet2 - thet1
        return (math.degrees(thet1), math.degrees(thet2),
        math.degrees(thet3))

class PIDDriveController(Actuator):
    '''PID control of wheel motors for driving. Differential steering
    used for changes in direction and turning on the spot. Overall
    wheel speeds are computed as the combination of an angular speed
    (proportional to the difference in speed between the left and
    right side of the rover) and the translation speed (average of the
    left and right side speeds of the rover).'''

    def __init__(self, kp = 0, ki = 0, kd = 0):
        Actuator.__init__(self)
        self.kp = kp            # proportional gain
        self.ki = ki            # integral gain
        self.kd = kd            # differential gain
        self.omega = 0          # angular speed
        self.spd = 0            # translation speed

    def activate(self):
        self.acquire_motors("Wheels")
        if not self.have_acquired("Wheels"):
            dg.print("Cannot access wheel motors for PID control.")
        self.begin_actuate()
        with self.condition:
            self.condition.notify()

    def deactivate(self):
        if self.have_acquired("Wheels"):
            self.release_motors("Wheels")

    def _pid(self,relx,rely):
        '''relx and rely in birds-eyeview coordinates.'''
        pass

