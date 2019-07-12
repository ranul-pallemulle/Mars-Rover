/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package UI;

import java.awt.Dimension;
import static java.lang.Math.PI;
import static java.lang.Math.abs;
import static java.lang.Math.acos;
import static java.lang.Math.asin;
import static java.lang.Math.atan2;
import static java.lang.Math.cos;
import static java.lang.Math.sin;
import java.net.URL;
import java.util.ResourceBundle;
import javax.swing.SwingUtilities;
import javafx.beans.value.ChangeListener;
import javafx.beans.value.ObservableValue;
import javafx.embed.swing.SwingNode;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.Scene;
import javafx.scene.control.ComboBox;
import javafx.scene.input.MouseEvent;
import javafx.scene.layout.AnchorPane;
import javafx.scene.shape.Circle;
import javafx.scene.shape.Line;
import javafx.scene.text.Text;
import org.freedesktop.gstreamer.Bin;
import org.freedesktop.gstreamer.Gst;
import org.freedesktop.gstreamer.Pipeline;

/**
 * FXML Controller class
 *
 * @author Ranul Pallemulle
 */
public class MainFxmlController implements Initializable {
    
    @FXML private Circle joyBackCircle;
    @FXML private Circle joyFrontCircle;
    @FXML private Text dispJoyX;
    @FXML private Text dispJoyY;
    @FXML private Circle armJoint1;
    @FXML private Circle armJoint2;
    @FXML private Circle armJoint3;
    @FXML private Line lineSeg1;
    @FXML private Line lineSeg2;
    @FXML private Line lineSeg3;
    @FXML private ComboBox ipSelector;
    @FXML private SwingNode videoScreen;
    
    private double joyMouseX;
    private double joyMouseY;
    private double[] armX = {250,300,350,400};
    private double[] armY = {250,250,250,250};
    private double[] armT = {0,0,0};
    private final double segL = 50;
    private final double max_ea = 20 * PI/180; // max elbow angle at which flipping is allowed
    
    private String ipAddress;
    private String gstPipeline;
    
    /**
     * Initializes the controller class.
     * @param url
     * @param rb
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        ipSelector.getItems().setAll("WiFi","Ethernet","Local");
        ipSelector.getSelectionModel().selectedItemProperty().addListener(
                new ChangeListener<String>() {
                @Override public void changed(
                ObservableValue<? extends String> selected, String oldS, String newS) {
                    switch (newS) {
                        case "WiFi":
                            break;
                        case "Ethernet":
                            break;
                        case "Local":
                            break;
                        default:
                            break;
                    }
                }});
        
        createVideoScreen(videoScreen);
    }
    
    /**
     * Event handler for mouse press on joystick.
     * @param e 
     */
    public void pressCoordsJoystick (MouseEvent e) {
        joyMouseX = e.getX();
        joyMouseY = e.getY();
    }
    
    /**
     * Event handler for when mouse is released after dragging joystick.
     * @param e
     */
    public void snapBackJoystick (MouseEvent e) {
        double centerx = joyBackCircle.getCenterX();
        double centery = joyBackCircle.getCenterY();
        joyFrontCircle.setCenterX(centerx);
        joyFrontCircle.setCenterY(centery);
        dispJoyX.setText(String.format("%.1f",centerx));
        dispJoyY.setText(String.format("%.1f",-centery));
    }
    
    /**
     * Event handler for when mouse is dragged on joystick.
     * @param e
     */
    public void updateJoystick (MouseEvent e) {
        // get distance between click and drag
        double drag_delx = e.getX() - joyMouseX;
        double drag_dely = e.getY() - joyMouseY;
        
        // get new position of joystick
        double joy_newx = joyBackCircle.getCenterX() + drag_delx;
        double joy_newy = joyBackCircle.getCenterY() + drag_dely;
        
        // calculate radial displacement
        double rad2 = joy_newx * joy_newx +
                     joy_newy * joy_newy;
        double maxrad = joyBackCircle.getRadius() - joyFrontCircle.getRadius();
        if (rad2 < maxrad * maxrad) {
            joyFrontCircle.setCenterX(joy_newx);
            joyFrontCircle.setCenterY(joy_newy);
        }
        else {
            double angle = atan2(joy_newy,joy_newx);
            joy_newx = joyBackCircle.getCenterX() + maxrad * cos(angle);
            joy_newy = joyBackCircle.getCenterY() + maxrad * sin(angle);
            joyFrontCircle.setCenterX(joy_newx);
            joyFrontCircle.setCenterY(joy_newy);
            
        }
        
        dispJoyX.setText(String.format("%.1f",joy_newx));
        dispJoyY.setText(String.format("%.1f",-joy_newy));
    }
    
    /**
     * Event handler for when the gripper slider is moved
     * @param e 
     */
    public void updateGripperSlider (MouseEvent e) {
        
    }
    
    /**
     * Event handler for when the gripper snapper is pressed
     * @param e 
     */
    public void snapGripperSlider (MouseEvent e) {
        
    }
    
    /**
     * Event handler for when the first arm joint is dragged
     * @param e 
     */
    public void updateArmSeg1 (MouseEvent e) {
        // Find new base servo angle
        double dx1 = e.getX() - armX[0];
        double dy1 = e.getY() - armY[0];
        double dthet1 = atan2(dy1,dx1) - armT[0];
        armT[0] = armT[0] + dthet1;
        // Find coordinates of joints
        armX[1] = armX[0] + cos(armT[0]) * segL;
        armY[1] = armY[0] + sin(armT[0]) * segL;
        armX[2] = armX[1] + cos(armT[0] + armT[1]) * segL;
        armY[2] = armY[1] + sin(armT[0] + armT[1]) * segL;
        armX[3] = armX[2] + cos(armT[0] + armT[1] + armT[2]) * segL;
        armY[3] = armY[2] + sin(armT[0] + armT[1] + armT[2]) * segL;
        
        armJoint1.setCenterX(armX[1]);
        armJoint1.setCenterY(armY[1]);
        armJoint2.setCenterX(armX[2]);
        armJoint2.setCenterY(armY[2]);
        armJoint3.setCenterX(armX[3]);
        armJoint3.setCenterY(armY[3]);
        lineSeg1.setEndX(armX[1]);
        lineSeg1.setEndY(armY[1]);
        lineSeg2.setStartX(armX[1]);
        lineSeg2.setStartY(armY[1]);
        lineSeg2.setEndX(armX[2]);
        lineSeg2.setEndY(armY[2]);
        lineSeg3.setStartX(armX[2]);
        lineSeg3.setStartY(armY[2]);
        lineSeg3.setEndX(armX[3]);
        lineSeg3.setEndY(armY[3]);
        
    }
    
    /**
     * Event handler for when the second arm joint is dragged
     * @param e 
     */    
    public void updateArmSeg2 (MouseEvent e) {
        double reqx2 = e.getX();
        double reqy2 = e.getY();
        // requested position might be outside two segment circle
        if ((reqx2 - armX[0])*(reqx2 - armX[0]) + 
            (reqy2 - armY[0])*(reqy2 - armY[0])
                < 4*segL*segL) { // can go to exact position
            armX[2] = reqx2;
            armY[2] = reqy2;
            double lX = armX[2] - armX[0];
            double lY = armY[2] - armY[0];
            double ct2 = ((lX*lX + lY*lY)-2*segL*segL)/(2*segL*segL);
            if (armT[2] > 0) { // need elbow down
                armT[1] = acos(ct2);
            }
            else { // need elbow up
                armT[1] = -acos(ct2);
            }
            double st2 = sin(armT[1]);
            double A = segL + segL*ct2;
            double B = segL*st2;
            double AB2 = A*A + B*B;
            double ct1 = (lX*A + lY*B)/AB2;
            double st1 = (lY*A - lX*B)/AB2;
            if (ct1 > 0) {
                armT[0] = asin(st1);
            }
            else {
                armT[0] = PI - asin(st1);
            }
        } 
        else { // can't reach, follow angle only, with both segments straight
            double dx2 = e.getX() - armX[0];
            double dy2 = e.getY() - armY[0];
            double dthet1 = atan2(dy2,dx2) - armT[0];
            armT[0] = armT[0] + dthet1;
            armT[1] = 0; 
        }
        
        armX[1] = armX[0] + cos(armT[0]) * segL;
        armY[1] = armY[0] + sin(armT[0]) * segL;
        armX[2] = armX[1] + cos(armT[0] + armT[1]) * segL;
        armY[2] = armY[1] + sin(armT[0] + armT[1]) * segL;
        armX[3] = armX[2] + cos(armT[0] + armT[1] + armT[2]) * segL;
        armY[3] = armY[2] + sin(armT[0] + armT[1] + armT[2]) * segL;
        
        armJoint1.setCenterX(armX[1]);
        armJoint1.setCenterY(armY[1]);
        armJoint2.setCenterX(armX[2]);
        armJoint2.setCenterY(armY[2]);
        armJoint3.setCenterX(armX[3]);
        armJoint3.setCenterY(armY[3]);
        lineSeg1.setEndX(armX[1]);
        lineSeg1.setEndY(armY[1]);
        lineSeg2.setStartX(armX[1]);
        lineSeg2.setStartY(armY[1]);
        lineSeg2.setEndX(armX[2]);
        lineSeg2.setEndY(armY[2]);
        lineSeg3.setStartX(armX[2]);
        lineSeg3.setStartY(armY[2]);
        lineSeg3.setEndX(armX[3]);
        lineSeg3.setEndY(armY[3]);
        
    }
    
    /**
     * Event handler for when the gripper joint is dragged
     * @param e 
     */    
    public void updateArmSeg3 (MouseEvent e) {
        // First calculate angle of last segment required for alignment
        double reqx3 = e.getX();
        double reqy3 = e.getY();
        double dx3 = reqx3 - armX[2];
        double dy3 = reqy3 - armY[2];
        double gam = atan2(dy3,dx3);
        // Calculate the required position of the lower two segments
        double reqx2 = reqx3 - segL*cos(gam);
        double reqy2 = reqy3 - segL*sin(gam);
        
        // requested position might be outside two segment circle
        if ((reqx2 - armX[0])*(reqx2 - armX[0]) + 
            (reqy2 - armY[0])*(reqy2 - armY[0])
                < 4*segL*segL) { // can go to exact position
            armX[2] = reqx2;
            armY[2] = reqy2;
            double lX = armX[2] - armX[0];
            double lY = armY[2] - armY[0];
            double ct2 = ((lX*lX + lY*lY)-2*segL*segL)/(2*segL*segL);
            double wang3 = atan2((reqy3 - armY[0]),(reqx3 - armX[0]));
            double wang2 = atan2((reqy2 - armY[0]),(reqx2 - armX[0]));
            if (armT[1] > 0) { // previously was elbow down
                if (wang3-wang2 > 0) { // want elbow still down
                    armT[1] = acos(ct2);
                }
                else { // want elbow up if possible
                    if (armT[1] < max_ea) { // elbow angle small enough to flip
                        armT[1] = -acos(ct2);
                    }
                    else { // elbow angle change would be too large, keep elbow down
                        armT[1] = acos(ct2);
                    }
                }
            }
            else { // previously was elbow up
                if (wang3-wang2 < 0) { // want elbow still up
                    armT[1] = -acos(ct2);
                }
                else { // want elbow down if possible
                    if (armT[1] > -max_ea) { // elbow angle small enough to flip
                        armT[1] = acos(ct2);
                    }
                    else { // elbow angle change would be too large, keep elbow up
                        armT[1] = -acos(ct2);
                    }
                }
            }
            double st2 = sin(armT[1]);
            double A = segL + segL*ct2;
            double B = segL*st2;
            double AB2 = A*A + B*B;
            double ct1 = (lX*A + lY*B)/AB2;
            double st1 = (lY*A - lX*B)/AB2;
            if (ct1 > 0) {
                armT[0] = asin(st1);
            }
            else {
                armT[0] = PI - asin(st1);
            }
        } 
        else { // can't reach, follow angle only, with both segments straight
            double dx2 = reqx2 - armX[0];
            double dy2 = reqy2 - armY[0];
            double dthet1 = atan2(dy2,dx2) - armT[0];
            armT[0] = armT[0] + dthet1;
            armT[1] = 0; 
        }
        armT[2] = gam - armT[1] - armT[0];
        
        armX[1] = armX[0] + cos(armT[0]) * segL;
        armY[1] = armY[0] + sin(armT[0]) * segL;
        armX[2] = armX[1] + cos(armT[0] + armT[1]) * segL;
        armY[2] = armY[1] + sin(armT[0] + armT[1]) * segL;
        armX[3] = armX[2] + cos(armT[0] + armT[1] + armT[2]) * segL;
        armY[3] = armY[2] + sin(armT[0] + armT[1] + armT[2]) * segL;
        
        armJoint1.setCenterX(armX[1]);
        armJoint1.setCenterY(armY[1]);
        armJoint2.setCenterX(armX[2]);
        armJoint2.setCenterY(armY[2]);
        armJoint3.setCenterX(armX[3]);
        armJoint3.setCenterY(armY[3]);
        lineSeg1.setEndX(armX[1]);
        lineSeg1.setEndY(armY[1]);
        lineSeg2.setStartX(armX[1]);
        lineSeg2.setStartY(armY[1]);
        lineSeg2.setEndX(armX[2]);
        lineSeg2.setEndY(armY[2]);
        lineSeg3.setStartX(armX[2]);
        lineSeg3.setStartY(armY[2]);
        lineSeg3.setEndX(armX[3]);
        lineSeg3.setEndY(armY[3]);
    }
    
    /**
     * Perform inverse kinematics on 2-rotation planar manipulator based on 
     * 3R manipulator setting.
     * @param reqx3 - required x position of end of final segment (3R)
     * @param reqy3 - required y position of end of final segment (3R)
     * @param reqx2 - required x position of end of second segment
     * @param reqy2 - required y position of end of second segment
     * @return - Array containing base angle and elbow angle in radians
     */
    private double[] inverse_kinematics_2R(double reqx3, double reqy3, double reqx2, double reqy2) {
        double lX2 = reqx2 - armX[0];
        double lY2 = reqy2 - armY[0];
        double lX3 = reqx3 - armX[0];
        double lY3 = reqy3 - armY[0];
        double[] res_angs = new double[2];
        
        if (lX2*lX2 + lY2*lY2 < 4*segL*segL) { // can go to exact position
            double ct2 = ((lX2*lX2 + lY2*lY2)-2*segL*segL)/(2*segL*segL);
            double wang3 = atan2(lY3,lX3);
            double wang2 = atan2(lY2,lX2);
            if (armT[1] > 0) { // previously was elbow down
                if (wang3-wang2 > 0) { // want elbow still down
                    res_angs[1] = acos(ct2);
                }
                else { // want elbow up if possible
                    if (armT[1] < max_ea) { // elbow angle small enough to flip
                        res_angs[1] = -acos(ct2);
                    }
                    else { // elbow angle change would be too large, keep elbow down
                        res_angs[1] = acos(ct2);
                    }
                }
            }
            else { // previously was elbow up
                if (wang3-wang2 < 0) { // want elbow still up
                    res_angs[1] = -acos(ct2);
                }
                else { // want elbow down if possible
                    if (armT[1] > -max_ea) { // elbow angle small enough to flip
                        res_angs[1] = acos(ct2);
                    }
                    else { // elbow angle change would be too large, keep elbow up
                        res_angs[1] = -acos(ct2);
                    }
                }
            }
            double st2 = sin(res_angs[1]);
            double A = segL + segL*ct2;
            double B = segL*st2;
            double AB2 = A*A + B*B;
            double ct1 = (lX2*A + lY2*B)/AB2;
            double st1 = (lY2*A - lX2*B)/AB2;
            if (ct1 > 0) {
                res_angs[0] = asin(st1);
            }
            else {
                res_angs[0] = PI - asin(st1);
            }
        } 
        else { // can't reach, follow angle only, with both segments straight
            double dthet1 = atan2(lY2,lX2) - armT[0];
            res_angs[0] = armT[0] + dthet1;
            res_angs[1] = 0; 
        }
        return res_angs;
    }
    
    private void createVideoScreen(final SwingNode swingNode) {
        gstPipeline = "tcpclientsrc host=192.168.4.1 port=5564 ! gdpdepay ! rtph264depay ! avdec_h264 ! videoconvert ! capsfilter caps=video/x-raw,width=640,height=400";
        SimpleVideoComponent vc = new SimpleVideoComponent();
        vc.getElement().set("sync",false);
        Bin bin = Gst.parseBinFromDescription(gstPipeline, true);
        Pipeline pipe = new Pipeline();
        pipe.addMany(bin, vc.getElement());
        Pipeline.linkMany(bin,vc.getElement());
        SwingUtilities.invokeLater(new Runnable() {
            @Override
            public void run() {
                swingNode.setContent(vc);
            }
        });
        
        vc.setPreferredSize(new Dimension(640,400));      vc.setKeepAspect(true);
    }
    
}
