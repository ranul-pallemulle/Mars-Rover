import unittest
from unittest.mock import patch, Mock
from autonomous.goal_samples import Samples
import math

class TestGoalSamples(unittest.TestCase):

    def setUp(self):
        self.testSamples = Samples()

    def test_initial_position(self):
        self.testSamples.set_initial_arm_position()
        print("ANGLES: {}, {}, {}, {}".format(math.degrees(self.testSamples.angle_bottom),
                                              math.degrees(self.testSamples.angle_middle),
                                              math.degrees(self.testSamples.angle_top),
                                              math.degrees(self.testSamples.angle_gripper)))        

    def test_slight_change(self):
        self.testSamples.angle_bottom = 0
        self.testSamples.angle_middle = 0
        self.testSamples.angle_top = 0
        self.testSamples.angle_gripper = 0
        # self.testSamples.gripper_x = 3
        # self.testSamples.gripper_y = 0
        set_top = math.radians(60)
        num_iter = 25
        enable_assert = True
        for x in range(num_iter):
            self.testSamples._slight_change(0,0,set_top,0)
        print("ANGLES: {}, {}, {}, {}".format(math.degrees(self.testSamples.angle_bottom),
                                              math.degrees(self.testSamples.angle_middle),
                                              math.degrees(self.testSamples.angle_top),
                                              math.degrees(self.testSamples.angle_gripper)))
        if enable_assert:
            self.assertAlmostEqual(self.testSamples.angle_top,set_top, delta=math.radians(1))

        set_top = math.radians(90)
        for x in range(num_iter):
            self.testSamples._slight_change(0,0,set_top,0)
        print("ANGLES: {}, {}, {}, {}".format(math.degrees(self.testSamples.angle_bottom),
                                              math.degrees(self.testSamples.angle_middle),
                                              math.degrees(self.testSamples.angle_top),
                                              math.degrees(self.testSamples.angle_gripper)))
        if enable_assert:
            self.assertAlmostEqual(self.testSamples.angle_top,set_top, delta=math.radians(1))

        set_top = math.radians(-45)
        for x in range(num_iter):
            self.testSamples._slight_change(0,0,set_top,0)
        print("ANGLES: {}, {}, {}, {}".format(math.degrees(self.testSamples.angle_bottom),
                                              math.degrees(self.testSamples.angle_middle),
                                              math.degrees(self.testSamples.angle_top),
                                              math.degrees(self.testSamples.angle_gripper)))
        if enable_assert:
            self.assertAlmostEqual(self.testSamples.angle_top,set_top, delta=math.radians(1))

        set_top = math.radians(120)
        for x in range(num_iter):
            self.testSamples._slight_change(0,0,set_top,0)
        print("ANGLES: {}, {}, {}, {}".format(math.degrees(self.testSamples.angle_bottom),
                                              math.degrees(self.testSamples.angle_middle),
                                              math.degrees(self.testSamples.angle_top),
                                              math.degrees(self.testSamples.angle_gripper)))
        if enable_assert:
            self.assertAlmostEqual(self.testSamples.angle_top, math.radians(90), delta=math.radians(1))

        set_top = math.radians(-120)
        for x in range(num_iter):
            self.testSamples._slight_change(0,0,set_top,0)
        print("ANGLES: {}, {}, {}, {}".format(math.degrees(self.testSamples.angle_bottom),
                                              math.degrees(self.testSamples.angle_middle),
                                              math.degrees(self.testSamples.angle_top),
                                              math.degrees(self.testSamples.angle_gripper)))
        if enable_assert:
            self.assertAlmostEqual(self.testSamples.angle_top, math.radians(-90), delta=math.radians(1))

        set_top = math.radians(0)
        set_middle = math.radians(0)
        set_bottom = math.radians(0)
        set_gripper = math.radians(0)
        for x in range(num_iter):
            self.testSamples._slight_change(set_bottom,set_middle,set_top,set_gripper)
        print("ANGLES: {}, {}, {}, {}".format(math.degrees(self.testSamples.angle_bottom),
                                              math.degrees(self.testSamples.angle_middle),
                                              math.degrees(self.testSamples.angle_top),
                                              math.degrees(self.testSamples.angle_gripper)))
        if enable_assert:
            self.assertAlmostEqual(self.testSamples.angle_top, set_top, delta=math.radians(1))
            self.assertAlmostEqual(self.testSamples.angle_middle, set_middle, delta=math.radians(1))
            self.assertAlmostEqual(self.testSamples.angle_bottom, set_bottom, delta=math.radians(1))
            self.assertAlmostEqual(self.testSamples.angle_gripper, set_gripper, delta=math.radians(1))


        set_top = math.radians(57)
        set_middle = math.radians(-12)
        set_bottom = math.radians(90)
        set_gripper = math.radians(82)
        for x in range(num_iter):
            self.testSamples._slight_change(set_bottom,set_middle,set_top,set_gripper)
        print("ANGLES: {}, {}, {}, {}".format(math.degrees(self.testSamples.angle_bottom),
                                              math.degrees(self.testSamples.angle_middle),
                                              math.degrees(self.testSamples.angle_top),
                                              math.degrees(self.testSamples.angle_gripper)))
        if enable_assert:
            self.assertAlmostEqual(self.testSamples.angle_top, set_top, delta=math.radians(1))
            self.assertAlmostEqual(self.testSamples.angle_middle, set_middle, delta=math.radians(1))
            self.assertAlmostEqual(self.testSamples.angle_bottom, set_bottom, delta=math.radians(1))
            self.assertAlmostEqual(self.testSamples.angle_gripper, set_gripper, delta=math.radians(1))

