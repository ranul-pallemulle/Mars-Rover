/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package Backend;

import static java.lang.Math.PI;
import static java.lang.Math.abs;
import static java.lang.Math.acos;
import static java.lang.Math.asin;
import static java.lang.Math.atan2;
import static java.lang.Math.cos;
import static java.lang.Math.sin;

/**
 *
 * @author Ranul Pallemulle
 */
public class RoboticArmController {
    
    private double segL; // length of arm segments
    private double max_ea; // elbow angle at which to flip
    private double lim_base; // limit of base servo angle
    private double lim_elbow; // limit of elbow servo angle
    private double lim_top; // limit of top servo angle
    private double lim_sum; // limit of sum of arm servo angles
    private double seg3down_ang; // angle of last segment when seg3down
    private boolean seg3down; // keep last segment down
    private boolean limits_active; // arm angles are limited
    private boolean sum_limit_active; // sum of arm angles is limited
    
    private double[] armX; // x coordinates of arm joints
    private double[] armY; // y coordinates of arm joints
    private double[] armT; // arm servo angles
    private double gripper_val; // gripper setting value
    
    
    public RoboticArmController(double[] x, double[] y, double[] theta) {
        armX = x;
        armY = y;
        armT = theta;
        gripper_val = 0;
        segL = 50;
        seg3down = false;
        limits_active = false;
        sum_limit_active = false;
        max_ea = 20 * PI/180;
        lim_base = 100 * PI/180;
        lim_elbow = 110 * PI/180;
        lim_top = 110 * PI/180;
        lim_sum = 180 * PI/180;
    }
    
    
    /**
     * Move arm by changing the coordinates of the elbow joint.
     * @param x
     * @param y
     * @return - successfully updated the arm coordinates
     */
    public boolean moveFirstJoint(double x, double y) {
        double dx1 = x - armX[0];
        double dy1 = y - armY[0];
        double base_ang = armT[0];
        double top_ang = armT[2];
        double dthet1 = atan2(dy1,dx1) - base_ang;
        base_ang = base_ang + dthet1;
        if (seg3down) {
            top_ang = seg3down_ang - armT[1] - base_ang;
        }
        boolean success = setAngles(base_ang, armT[1], top_ang, gripper_val);
        if (success) {
            forwardKinematics();
        }
        return success;
    }
    
    
    /**
     * Move arm by changing the coordinates of the top joint
     * @param x
     * @param y
     * @return - successfully updated the arm coordinates
     */
    public boolean moveSecondJoint(double x, double y) {
        boolean success;
        if (!seg3down) {
            double [] angs = inverseKinematics2R(armX[3],armY[3],x,y);
            double base_ang = angs[0];
            double elbow_ang = angs[1];
            success = setAngles(base_ang, elbow_ang, armT[2], gripper_val);
        }
        else {
            double reqx3 = x + segL*cos(seg3down_ang);
            double reqy3 = y + segL*sin(seg3down_ang);
            double[] angs = inverseKinematics2R(reqx3,reqy3,x,y);
            double base_ang = angs[0];
            double elbow_ang = angs[1];
            double top_ang = seg3down_ang - elbow_ang - base_ang;
            success = setAngles(base_ang, elbow_ang, top_ang, gripper_val);
        }
        
        if (success) {
            forwardKinematics();
        }
        return success;
    }
    
    
    /**
     * Move arm by changing the coordinates of the gripper joint
     * @param x
     * @param y
     * @return - successfully updated the arm coordinates
     */
    public boolean moveThirdJoint(double x, double y) {
        double reqx3 = x;
        double reqy3 = y;
        double gam;
        if (!seg3down) {
            double dx3 = reqx3 - armX[2];
            double dy3 = reqy3 - armY[2];
            gam = atan2(dy3,dx3);
        }
        else {
            gam = seg3down_ang;
        }
        
        // Calculate the required position of the lower two segments
        double reqx2 = reqx3 - segL*cos(gam);
        double reqy2 = reqy3 - segL*sin(gam);
        
        double[] angs = inverseKinematics2R(reqx3,reqy3,reqx2,reqy2);
        double base_ang = angs[0];
        double elbow_ang = angs[1];
        double top_ang = gam - elbow_ang - base_ang;
        if (top_ang < -PI) {
            top_ang = 2*PI + top_ang;
        }
        else if (top_ang > PI) {
            top_ang = top_ang - 2*PI;
        }
        
        boolean success = setAngles(base_ang, elbow_ang, top_ang, gripper_val);
        if (success) {
            forwardKinematics();
        }
        return success;
    }
    
    
    /**
     * Move arm by changing the individual servo angles
     * @param base
     * @param elbow
     * @param top
     * @param gripper
     * @return - successfully updated the arm coordinates
     */
    public boolean moveByServoAngles(double base, double elbow, double top, 
                                     double gripper) {
        boolean success = setAngles(base, elbow, top, gripper);
        if (success) {
            forwardKinematics();
        }
        return success;
    }
    
     public void moveGripper(double value) {
        gripper_val = value;
    }

    
    /**
     * If set is true, fix the last arm segment pointed at the floor.
     * @param set
     * @return - successfully updated the arm coordinates. If seg3down is 
     * enabled and arm update is unsuccessful, seg3down is disabled. Disabling 
     * seg3down is always a success;
     */
    public boolean enableSeg3Down(boolean set) {
        seg3down = set;
        boolean success;
        if (seg3down) {
            double reqx3 = armX[2] + cos(seg3down_ang)*segL;
            double reqy3 = armY[2] + sin(seg3down_ang)*segL;
            success = moveThirdJoint(reqx3, reqy3);
            if (!success) {
                seg3down = false;
            }
            return success;
        }
        return true;
    }
    
    
    /** 
     * Set the angle at which the arm points at the floor when seg3down is 
     * enabled.
     * @param value
     * @return successfully updated the arm coo
     */
    public boolean setSeg3DownOffsetAngle(double value) {
        seg3down_ang = value;
        if (seg3down) {
            double reqx3 = armX[2] + cos(seg3down_ang)*segL;
            double reqy3 = armY[2] + sin(seg3down_ang)*segL;
            return moveThirdJoint(reqx3,reqy3);
        }
        return false;
    }
    
    
    public void enableLimits(boolean set) {
        limits_active = set;
    }
    
    
    public void enableSumLimit(boolean set) {
        sum_limit_active = set;
    }
    
    
   
    
    
    public void setLimits(double base, double elbow, double top) {
        lim_base = base;
        lim_elbow = elbow;
        lim_top = top;
    }
    
    
    public void setSumLimit(double sum) {
        lim_sum = sum;
    }
    
    
    public void setLimits(double base, double elbow, double top, double sum) {
        lim_base = base;
        lim_elbow = elbow;
        lim_top = top;
        lim_sum = sum;
    }
    
    
    public void setSegmentLength(double len) {
        segL = len;
    }

    
    public void setElbowFlipAngle(double angle) {
        max_ea = angle * PI/180;
    }
    
    
    /// Getters
    public double[] getXCoords() {
        return armX;
    }
    
    public double[] getYCoords() {
        return armY;
    }
    
    
    
    /// private methods
    
    private boolean setAngles(double base, double elbow, double top, 
                              double gripper) {
        if (limits_active) {
            if (abs(base) > lim_base) {
                return false;
            }
            if (abs(elbow) > lim_elbow) {
                return false;
            }
            if (abs(top) > lim_top) {
                return false;
            }
            if (sum_limit_active && (abs(elbow + top) > lim_sum)) {
                return false;
            }
        }
        armT[0] = base;
        armT[1] = elbow;
        armT[2] = top;
        gripper_val = gripper;
        return true;
    }
    
    private void forwardKinematics() {
        armX[1] = armX[0] + cos(armT[0]) * segL;
        armY[1] = armY[0] + sin(armT[0]) * segL;
        armX[2] = armX[1] + cos(armT[0] + armT[1]) * segL;
        armY[2] = armY[1] + sin(armT[0] + armT[1]) * segL;
        armX[3] = armX[2] + cos(armT[0] + armT[1] + armT[2]) * segL;
        armY[3] = armY[2] + sin(armT[0] + armT[1] + armT[2]) * segL;
    }
    
    private double[] inverseKinematics2R(double reqx3, double reqy3, double reqx2, 
                                     double reqy2) {
        double lX2 = reqx2 - armX[0];
        double lY2 = reqy2 - armY[0];
        double lX3 = reqx3 - armX[0];
        double lY3 = reqy3 - armY[0];
        double[] res = new double[2];
        
        if (lX2*lX2 + lY2*lY2 < 4*segL*segL) { // can go to exact position
            double ct2 = ((lX2*lX2 + lY2*lY2)-2*segL*segL)/(2*segL*segL);
            double ang3 = atan2(lY3,lX3);
            double ang2 = atan2(lY2,lX2);
            if (armT[1] > 0) { // currently elbow down
                if (ang3-ang2 > 0) { // want elbow still down
                    res[1] = acos(ct2); // no need to flip
                }
                else { // want elbow up if possible
                    if (armT[1] < max_ea) { // elbow angle small enough to flip
                        res[1] = -acos(ct2); // flip
                    }
                    else { // elbow angle change would be too large, keep elbow down
                        res[1] = acos(ct2); // don't flip
                    }
                }
            }
            else { // currently elbow up
                if (ang3-ang2 < 0) { // want elbow still up
                    res[1] = -acos(ct2); // no need to flip
                }
                else { // want elbow down if possible
                    if (armT[1] > -max_ea) { // elbow angle small enough to flip
                        res[1] = acos(ct2); // flip
                    }
                    else { // elbow angle change would be too large, keep elbow up
                        res[1] = -acos(ct2); // don't flip
                    }
                }
            }
            double st2 = sin(res[1]);
            double A = segL + segL*ct2;
            double B = segL*st2;
            double AB2 = A*A + B*B;
            double ct1 = (lX2*A + lY2*B)/AB2;
            double st1 = (lY2*A - lX2*B)/AB2;
            if (ct1 > 0) {
                res[0] = asin(st1);
            }
            else {
                res[0] = PI - asin(st1);
            }
        } 
        else { // can't reach, follow angle only, with both segments straight
            double dthet1 = atan2(lY2,lX2) - armT[0];
            res[0] = armT[0] + dthet1;
            res[1] = 0; 
        }
        return res;
    }
}
