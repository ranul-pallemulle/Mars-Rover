import unittest
from unittest.mock import patch, Mock
import math
import matplotlib.pyplot as plt
# import numpy as np

"""Sample is fixed in the rover frame. Aim is for the tip of the gripper to 
reach the sample."""
x_rs = 10 # sample coordinates in the rover frame.
y_rs = -10
arm_scale = 1
arm_l1 = 6.5*arm_scale # length of first arm segment, cm
arm_l2 = 6.5*arm_scale # length of second arm segment, cm
arm_l3 = 10*arm_scale # length of gripper segment, cm
angle_bottom = 83 # actual servo angles, in degrees
angle_middle = -56
angle_top = -111
angle_gripper = 0
servo_limit = 120
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


def _inverse_kinematics(x, y, gamma):
    x2R = x - arm_l3 * math.cos(gamma) # x for the tip of the second segment
    y2R = y - arm_l3 * math.sin(gamma) # y for the tip of the second segment
    ct2 = (((x2R**2) + (y2R**2)) - ((arm_l1**2) + (arm_l2**2)))/(2*arm_l1*arm_l2) # cos(theta2)
    try:
        if gamma > 0: # gripper looking up
        # print(ct2)
            thet2 = math.acos(ct2) # elbow down configuration for 2R manipulator problem
        else:
        # print(ct2)
            thet2 = -math.acos(ct2) # elbow up configuration
        st2 = math.sin(thet2)
    except Exception:
        print("Sample unreachable")
        return None

    A = arm_l1 + arm_l2*ct2
    B = arm_l2*st2
    AB2 = (A**2) + (B**2)
    ct1 = (x2R*A + y2R*B)/AB2
    st1 = (y2R*A - x2R*B)/AB2
    if ct1 > 0:             # principle angles
        thet1 = math.asin(st1)
    else:
        thet1 = math.pi - math.asin(st1)

    thet3 = gamma - thet2 - thet1
    return (math.degrees(thet1), math.degrees(thet2), math.degrees(thet3))                             


def _slight_change(theta1,theta2,theta3,gripper):
    global angle_bottom, angle_middle, angle_top, angle_gripper
    global gripper_x, gripper_y, gripper_gamma
    dthet = [               # angle changes required
                theta1 - angle_bottom,
                theta2 - angle_middle,
                theta3 - angle_top,
                gripper - angle_gripper
            ]
    sign = lambda delta: delta and (1,-1)[delta < 0] # 0 if delta==0 otherwise +-1        
    for idx, delta in enumerate(dthet):
        if abs(delta) > 50:
            dthet[idx] = sign(delta)*10 # 10
        elif abs(delta) > 10:
            dthet[idx] = sign(delta)*4 # 4
        elif abs(delta) > 5: 
            dthet[idx] = sign(delta)*2 # 2
        elif abs(delta) > 2: 
            dthet[idx] = sign(delta)*1 # 1
        elif abs(delta) > 0.5:
            dthet[idx] = sign(delta)*1 # if delta==0, sign==0 and dthet[idx]==0
        else:
            dthet[idx] = sign(delta)*0.02
    new_thet1 = angle_bottom + dthet[0]
    new_thet2 = angle_middle + dthet[1]
    new_thet3 = angle_top + dthet[2]
    new_gripper = angle_gripper + dthet[3]
   
    if abs(new_thet1) < servo_limit:
        angle_bottom = new_thet1
    else:
        angle_bottom = sign(new_thet1)*servo_limit
    if abs(new_thet2) < servo_limit:
        angle_middle = new_thet2
    else:
        angle_middle = sign(new_thet2)*servo_limit
    if abs(new_thet3) <= servo_limit:
        angle_top = new_thet3
    else:
        angle_top = sign(new_thet3)*servo_limit
    if abs(new_gripper) < servo_limit:
        angle_gripper = new_gripper
    else:
        angle_gripper = sign(new_gripper)*servo_limit

    print("ANGLES: {},{},{}".format(angle_bottom,
                                    angle_middle,
                                    angle_top))

    angle_bottom_rad = math.radians(angle_bottom)
    angle_middle_rad = math.radians(angle_middle)
    angle_top_rad = math.radians(angle_top)
    
    gripper_gamma = angle_bottom_rad + angle_middle_rad + angle_top_rad
    gripper_x = arm_l1*math.cos(angle_bottom_rad) + \
                    arm_l2*math.cos(angle_bottom_rad + angle_middle_rad) + \
                    arm_l3*math.cos(angle_bottom_rad + angle_middle_rad + angle_top_rad)
    gripper_y = arm_l1*math.sin(angle_bottom_rad) + \
                    arm_l2*math.sin(angle_bottom_rad + angle_middle_rad) + \
                    arm_l3*math.sin(angle_bottom_rad + angle_middle_rad + angle_top_rad)

    return angle_bottom,angle_middle,angle_top,angle_gripper

def pid_arm(relz, rely):
    del_gamma = math.atan2(rely,relz+arm_l3)
    new_gamma = gripper_gamma + del_gamma
    # new_gamma = math.radians(-90)

    # get sample coordinates in rover frame (origin at base servo)
    xs = gripper_x + relz*math.cos(gripper_gamma) - rely*math.sin(gripper_gamma)
    ys = gripper_y + relz*math.sin(gripper_gamma) + rely*math.cos(gripper_gamma)

    print("REQUESTED XY: {}, {}".format(xs,ys))
    print("CURRENT XY: {}, {}".format(gripper_x,gripper_y))
    # get angle changes needed using inverse kinematics and set them
    res = _inverse_kinematics(xs,ys,new_gamma)
    if res is not None:
        thet1,thet2,thet3 = res
        _slight_change(thet1,thet2,thet3,0)

def pid_arm_spec_gamma(targetz, targety, gamma):
    # get sample coordinates in rover frame (origin at base servo)
    xs = gripper_x + targetz*math.cos(gripper_gamma) - targety*math.sin(gripper_gamma)
    ys = gripper_y + targetz*math.sin(gripper_gamma) + targety*math.cos(gripper_gamma)

    print("REQUESTED XY: {}, {}".format(xs,ys))
    print("CURRENT XY: {}, {}".format(gripper_x,gripper_y))
    # get angle changes needed using inverse kinematics and set them
    res = _inverse_kinematics(xs,ys,gamma)
    if res is not None:
        thet1,thet2,thet3 = res
        _slight_change(thet1,thet2,thet3,0)

def pid_arm_seg3down(relz,rely):
    new_gamma = math.radians(-90)

    # get sample coordinates in rover frame (origin at base servo)
    xs = gripper_x + relz*math.cos(gripper_gamma) - rely*math.sin(gripper_gamma)
    ys = gripper_y + relz*math.sin(gripper_gamma) + rely*math.cos(gripper_gamma)

    print("REQUESTED XY: {}, {}".format(xs,ys))
    print("CURRENT XY: {}, {}".format(gripper_x,gripper_y))
    # get angle changes needed using inverse kinematics and set them
    res = _inverse_kinematics(xs,ys,new_gamma)
    if res is not None:
        thet1,thet2,thet3 = res
        _slight_change(thet1,thet2,thet3,0)
    
def _get_joint_coords():
    j1_x = arm_l1*math.cos(math.radians(angle_bottom))
    j2_x = j1_x + arm_l2*math.cos(math.radians(angle_bottom+angle_middle))
    j3_x = j2_x + arm_l3*math.cos(math.radians(angle_bottom+angle_middle+angle_top))

    j1_y = arm_l1*math.sin(math.radians(angle_bottom))
    j2_y = j1_y + arm_l2*math.sin(math.radians(angle_bottom+angle_middle))
    j3_y = j2_y + arm_l3*math.sin(math.radians(angle_bottom+angle_middle+angle_top))

    return ([0, j1_x,j2_x,j3_x],[0, j1_y,j2_y,j3_y])

def check_lengths_validity(xarr_init,yarr_init, xarr_fin, yarr_fin):
    len_init = []
    for i in range(len(xarr_init) - 1):
        length = math.sqrt((xarr_init[i]-xarr_init[i+1])**2 + (yarr_init[i]-yarr_init[i+1])**2)
        len_init.append(length)

    len_fin = []
    for i in range(len(xarr_fin) - 1):
        length = math.sqrt((xarr_fin[i]-xarr_fin[i+1])**2 + (yarr_fin[i]-yarr_fin[i+1])**2)
        len_fin.append(length)

    err = [fin-ini for fin,ini in zip(len_fin,len_init)]
    print(err)


class TestSampleSimulation(unittest.TestCase):
    def setUp(self):
        pass

    # def test_check_coords(self):
    #     #print("Initial x,y,gamma: {},{},{}".format(gripper_x,gripper_y,math.degrees(gripper_gamma)))
    #     target_x = 11#gripper_x + 0.5
    #     target_y = -10#gripper_y + 0.5
    #     jx_coords,jy_coords = _get_joint_coords()
    #     plt.plot(jx_coords,jy_coords,'bo-')
    #     plt.plot(target_x,target_y,'yo')
    #     for i in range(50):
    #         rx = math.cos(gripper_gamma)*(target_x - gripper_x) +\
    #              math.sin(gripper_gamma)*(target_y - gripper_y)
    #         ry = math.cos(gripper_gamma)*(target_y - gripper_y) -\
    #              math.sin(gripper_gamma)*(target_x - gripper_x)
    #         pid_arm(rx,ry)
    #         print("RELATIVE x,y: {},{}".format(rx,ry))
    #     # #print("Final x,y,gamma: {},{},{}".format(gripper_x,gripper_y,math.degrees(gripper_gamma)))
    #     # pid_arm_full(rx,ry)
    #     jx_coords_fin,jy_coords_fin = _get_joint_coords()
    #     plt.plot(jx_coords_fin,jy_coords_fin,'ro-')
    #     plt.axes().set_aspect('equal')
    #     check_lengths_validity(jx_coords,jy_coords,jx_coords_fin,jy_coords_fin)
    #     plt.show()

    def test_scout_mode(self):
        '''Fix x2R and y2R and only have gamma change'''
        global angle_bottom, angle_middle, angle_top, angle_gripper
        global gripper_x, gripper_y, gripper_gamma
        orig_x = 20
        orig_y = 0
        gripper_x = orig_x # 17
        gripper_y = orig_y # -5
        sample_x = 40
        sample_y = -10
        gripper_gamma = math.atan2(sample_y-gripper_y,sample_x-gripper_x)
        angle_bottom,angle_middle,angle_top = _inverse_kinematics(gripper_x,gripper_y,gripper_gamma)
        jx,jy = _get_joint_coords()
        plt.plot(jx,jy,'bo-')
        plt.plot(sample_x,sample_y,'yo')
        x2R = orig_x - arm_l3*math.cos(gripper_gamma)
        y2R = orig_y - arm_l3*math.sin(gripper_gamma)
        for j in range(20):
            sample_x -= 1.55
            for i in range(500):
                rx = math.cos(gripper_gamma)*(sample_x - gripper_x) +\
                    math.sin(gripper_gamma)*(sample_y - gripper_y)
                ry = math.cos(gripper_gamma)*(sample_y - gripper_y) -\
                    math.sin(gripper_gamma)*(sample_x - gripper_x)
                del_gamma = math.atan2(ry,rx+arm_l3)
                new_gamma = gripper_gamma + del_gamma

                #changed_x = math.cos(gripper_gamma)*(orig_x - gripper_x) +\
                #            math.sin(gripper_gamma)*(orig_y - gripper_y)
                #changed_y = math.cos(gripper_gamma)*(orig_y - gripper_y) -\
                #            math.sin(gripper_gamma)*(orig_x - gripper_x)
                new_x = x2R + arm_l3*math.cos(new_gamma)
                new_y = y2R + arm_l3*math.sin(new_gamma)
                del_x = math.cos(gripper_gamma)*(new_x - gripper_x) +\
                            math.sin(gripper_gamma)*(new_y - gripper_y)
                del_y = math.cos(gripper_gamma)*(new_y - gripper_y) -\
                            math.sin(gripper_gamma)*(new_x - gripper_x)
                pid_arm_spec_gamma(del_x,del_y,new_gamma)
                print("NEW GAMMA: {}".format(math.degrees(new_gamma)))
            plt.plot(sample_x,sample_y,'yo')
        jxf,jyf = _get_joint_coords()
        plt.plot(jxf,jyf,'ro-')
        plt.axes().set_aspect('equal')
        check_lengths_validity(jx,jy,jxf,jyf)
        plt.show()

        

    # def test_slight_change(self):
    #     global angle_bottom, angle_middle, angle_top, angle_gripper
    #     req_bottom,req_middle,req_top,req_grip = (angle_bottom + 60,
    #                                              angle_middle + 10,
    #                                              angle_top + 5,
    #                                              angle_gripper + 2)
    #     print("INITIAL :{},{},{},{}".format(angle_bottom,
    #                                         angle_middle,
    #                                         angle_top,
    #                                         angle_gripper))
    #     for i in range(1000):
    #         thet1,thet2,thet3,thet_grip = _slight_change(req_bottom,
    #                                                      req_middle,
    #                                                      req_top,
    #                                                      req_grip)
    #     print("FINAL :{},{},{},{}".format(thet1,
    #                                         thet2,
    #                                         thet3,
    #                                         thet_grip))                                                     

    # def test_check_coords2(self):
    #     global angle_bottom, angle_middle, angle_top, angle_gripper
    #     global gripper_x, gripper_y, gripper_gamma
    #     print("Initial x,y,gamma: {},{},{}".format(gripper_x,gripper_y,math.degrees(gripper_gamma)))
    #     target_x = gripper_x - 3
    #     target_y = gripper_y 
    #     jx_coords,jy_coords = _get_joint_coords()
    #     plt.plot(jx_coords,jy_coords,'bo-')
    #     angle_bottom, angle_middle, angle_top = _inverse_kinematics(target_x,target_y,math.radians(-90))
    #     angle_bottom_rad = math.radians(angle_bottom)
    #     angle_middle_rad = math.radians(angle_middle)
    #     angle_top_rad = math.radians(angle_top)
    
    #     gripper_gamma = angle_bottom_rad + angle_middle_rad + angle_top_rad
    #     gripper_x = arm_l1*math.cos(angle_bottom_rad) + \
    #                 arm_l2*math.cos(angle_bottom_rad + angle_middle_rad) + \
    #                 arm_l3*math.cos(angle_bottom_rad + angle_middle_rad + angle_top_rad)
    #     gripper_y = arm_l1*math.sin(angle_bottom_rad) + \
    #                 arm_l2*math.sin(angle_bottom_rad + angle_middle_rad) + \
    #                 arm_l3*math.sin(angle_bottom_rad + angle_middle_rad + angle_top_rad)
    #     jx_coords_fin,jy_coords_fin = _get_joint_coords()
    #     plt.plot(jx_coords_fin,jy_coords_fin,'ro-')
    #     plt.axes().set_aspect('equal')
    #     check_lengths_validity(jx_coords,jy_coords,jx_coords_fin,jy_coords_fin)
    #     plt.plot(target_x,target_y,'yo')
    #     plt.show()
