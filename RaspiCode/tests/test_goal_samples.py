import unittest
from unittest.mock import patch, Mock
from autonomous.goal_samples import Samples
import math

class TestGoalSamples(unittest.TestCase):

    def setUp(self):
        self.testSamples = Samples()

    def test_initial_position(self):
        self.testSamples.set_initial_arm_position()
        print("ANGLES: {}, {}, {}, {}".format(self.testSamples.angle_bottom,
                                              self.testSamples.angle_middle,
                                              self.testSamples.angle_top,
                                              self.testSamples.angle_gripper))

    def test_inverse_kinematics(self):
        arm_scale = 1
        arm_l1 = 6.5*arm_scale # length of first arm segment, cm
        arm_l2 = 6.5*arm_scale# length of second arm segment, cm
        arm_l3 = 10*arm_scale# length of gripper segment, cm
        servo_limit = 100
        angle_bottom = 97 # actual servo angles, in degrees
        angle_middle = -86
        angle_top = -21
        # angle_bottom = 90
        # angle_middle = 99
        # angle_top = 10
        gripper_x = arm_l1*math.cos(math.radians(angle_bottom)) +\
                    arm_l2*math.cos(math.radians(angle_bottom) +\
                                    math.radians(angle_middle)) +\
                    arm_l3*math.cos(math.radians(angle_bottom) +\
                                    math.radians(angle_middle) +\
                                    math.radians(angle_top))
        gripper_y = arm_l1*math.sin(math.radians(angle_bottom)) +\
                    arm_l2*math.sin(math.radians(angle_bottom) +\
                                    math.radians(angle_middle)) +\
                    arm_l3*math.sin(math.radians(angle_bottom) +\
                                    math.radians(angle_middle) +\
                                    math.radians(angle_top))
        gripper_gamma = math.radians(angle_bottom +\
                                     angle_middle +\
                                     angle_top)

        thet1,thet2,thet3 = self.testSamples._inverse_kinematics(gripper_x,gripper_y,gripper_gamma)
        print("OUTPUT OF INV KINEMATICS: {}, {}, {}".format(thet1,thet2,thet3))
        self.assertAlmostEqual(thet1,angle_bottom)
        self.assertAlmostEqual(thet2,angle_middle)
        self.assertAlmostEqual(thet3,angle_top)

    def test_slight_change(self):
        self.testSamples.angle_bottom = 0
        self.testSamples.angle_middle = 0
        self.testSamples.angle_top = 0
        self.testSamples.angle_gripper = 0
        # self.testSamples.gripper_x = 3
        # self.testSamples.gripper_y = 0
        set_top = 60
        num_iter = 25
        enable_assert = True
        for x in range(num_iter):
            self.testSamples._slight_change(0,0,set_top,0)
        print("ANGLES: {}, {}, {}, {}".format(self.testSamples.angle_bottom,
                                              self.testSamples.angle_middle,
                                              self.testSamples.angle_top,
                                              self.testSamples.angle_gripper))        
        if enable_assert:
            self.assertAlmostEqual(self.testSamples.angle_top,set_top, delta=1)

        set_top = 90
        for x in range(num_iter):
            self.testSamples._slight_change(0,0,set_top,0)
        print("ANGLES: {}, {}, {}, {}".format(self.testSamples.angle_bottom,
                                              self.testSamples.angle_middle,
                                              self.testSamples.angle_top,
                                              self.testSamples.angle_gripper))
        
        if enable_assert:
            self.assertAlmostEqual(self.testSamples.angle_top,set_top, delta=1)

        set_top = -45
        for x in range(num_iter):
            self.testSamples._slight_change(0,0,set_top,0)
        print("ANGLES: {}, {}, {}, {}".format(self.testSamples.angle_bottom,
                                              self.testSamples.angle_middle,
                                              self.testSamples.angle_top,
                                              self.testSamples.angle_gripper))
        if enable_assert:
            self.assertAlmostEqual(self.testSamples.angle_top,set_top, delta=1)

        set_top = 120
        for x in range(num_iter):
            self.testSamples._slight_change(0,0,set_top,0)
        print("ANGLES: {}, {}, {}, {}".format(self.testSamples.angle_bottom,
                                              self.testSamples.angle_middle,
                                              self.testSamples.angle_top,
                                              self.testSamples.angle_gripper))        
        if enable_assert:
            self.assertAlmostEqual(self.testSamples.angle_top, 100, delta=1)

        set_top = -130
        for x in range(num_iter):
            self.testSamples._slight_change(0,0,set_top,0)
        print("ANGLES: {}, {}, {}, {}".format(self.testSamples.angle_bottom,
                                              self.testSamples.angle_middle,
                                              self.testSamples.angle_top,
                                              self.testSamples.angle_gripper))
        if enable_assert:
            self.assertAlmostEqual(self.testSamples.angle_top, -100, delta=1)

        set_top = 0
        set_middle = 0
        set_bottom = 0
        set_gripper = 0
        for x in range(num_iter):
            self.testSamples._slight_change(set_bottom,set_middle,set_top,set_gripper)
        print("ANGLES: {}, {}, {}, {}".format(self.testSamples.angle_bottom,
                                              self.testSamples.angle_middle,
                                              self.testSamples.angle_top,
                                              self.testSamples.angle_gripper))        
        if enable_assert:
            self.assertAlmostEqual(self.testSamples.angle_top, set_top, delta=1)
            self.assertAlmostEqual(self.testSamples.angle_middle, set_middle, delta=1)
            self.assertAlmostEqual(self.testSamples.angle_bottom, set_bottom, delta=1)
            self.assertAlmostEqual(self.testSamples.angle_gripper, set_gripper, delta=1)


        set_top = 57
        set_middle = -12
        set_bottom = 90
        set_gripper = 82
        for x in range(num_iter):
            self.testSamples._slight_change(set_bottom,set_middle,set_top,set_gripper)
        print("ANGLES: {}, {}, {}, {}".format(self.testSamples.angle_bottom,
                                              self.testSamples.angle_middle,
                                              self.testSamples.angle_top,
                                              self.testSamples.angle_gripper))        
        if enable_assert:
            self.assertAlmostEqual(self.testSamples.angle_top, set_top, delta=1)
            self.assertAlmostEqual(self.testSamples.angle_middle, set_middle, delta=1)
            self.assertAlmostEqual(self.testSamples.angle_bottom, set_bottom, delta=1)
            self.assertAlmostEqual(self.testSamples.angle_gripper, set_gripper, delta=1)

