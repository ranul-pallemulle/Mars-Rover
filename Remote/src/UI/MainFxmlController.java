/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package UI;

import Backend.ArmDataController;
import Backend.KeyboardDriveController;
import Exceptions.FormatException;
import java.awt.Dimension;
import java.io.File;
import java.io.IOException;
import static java.lang.Math.PI;
import static java.lang.Math.abs;
import static java.lang.Math.acos;
import static java.lang.Math.asin;
import static java.lang.Math.atan2;
import static java.lang.Math.cos;
import static java.lang.Math.sin;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.ResourceBundle;
import java.util.function.Consumer;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.swing.SwingUtilities;
import javafx.embed.swing.SwingNode;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.Alert;
import javafx.scene.control.Alert.AlertType;
import javafx.scene.control.Button;
import javafx.scene.control.ComboBox;
import javafx.scene.control.Spinner;
import javafx.scene.control.SpinnerValueFactory;
import javafx.scene.control.TextField;
import javafx.scene.control.ToggleButton;
import javafx.scene.input.MouseEvent;
import javafx.scene.shape.Circle;
import javafx.scene.shape.Line;
import javafx.scene.text.Text;
import javafx.stage.FileChooser;
import javafx.stage.FileChooser.ExtensionFilter;
import javafx.stage.Stage;
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
    @FXML private Circle sliderBall;
    @FXML private Line sliderLine;
    @FXML private ComboBox<String> ipSelector;
    @FXML private SwingNode videoScreen;
    @FXML private ToggleButton connectRoverButton;
    @FXML private ToggleButton joyConnectButton;
    @FXML private ToggleButton armConnectButton;
    @FXML private ToggleButton vidConnectButton;
    @FXML private ComboBox<String> autoGoalSelector;
    @FXML private Button autoGoalEnableButton;
    @FXML private Button autoGoalDisableButton;
    @FXML private Button autoGoalDisableAllButton;
    @FXML private ToggleButton limitsButton;
    @FXML private ToggleButton sumLimitsButton;
    @FXML private Button gripperButton;
    @FXML private TextField dataFileTextField;
    @FXML private ComboBox<String> positionEditor;
    @FXML private ComboBox<String> positionSelector;
    @FXML private ToggleButton seg3DownButton;
    @FXML private Spinner<Integer> seg3DownOffsetPicker;
    
    private double joy_mouse_x;
    private double joy_mouse_y;
    private double[] armX = {250,300,350,400};
    private double[] armY = {250,250,250,250};
    private double[] armT = {0,0,0};
    private double gripper_val = 0;
    private double lim_base = 100 * PI/180; // limit of base angle
    private double lim_elbow = 110 * PI/180; // limit of elbow angle
    private double lim_top = 110 * PI/180; // limit of top angle
    private double lim_sum_angles = 180 * PI/180; // limit of sum of top and elbow angles
    private boolean limits_active = false; // arm angle limits
    private boolean sum_limit_active = false; // arm sum of angles limit
    private boolean seg3down = false; // keep last segment down
    private final double seg3down_ang = 90 * PI/180;
    private final double segL = 50;
    private final double max_ea = 20 * PI/180; // max elbow angle at which flipping is allowed
    
    private String ipAddress;
    private String gstPipeline;
    private Stage primaryStage;
    private ArmDataController armDataController;
    private KeyboardDriveController kbdController;
    private ArrayList<Runnable> runAfterInitList;
    
    /**
     * Initializes the controller class.
     * @param url
     * @param rb
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        // initialise joystick connect button
        joyConnectButton.setDisable(true); // cannot activate until connected
        
        // initialise arm control buttons
        armConnectButton.setDisable(true); // cannot activate until connected
        limitsButton.setSelected(true); // limits should be active by default
        limitsButtonPressed();
        sumLimitsButton.setSelected(true);
        sumLimitsButtonPressed();
        seg3DownOffsetPicker.setValueFactory(
                new SpinnerValueFactory.IntegerSpinnerValueFactory(-10,10,0));
        
        // initialise ipSelector
        ipSelector.getItems().setAll("WiFi","Ethernet","Local");
        
        
        // initialise video connect button and screen
        vidConnectButton.setDisable(true); // cannot activate until connected
        createVideoScreen(videoScreen);
        
        // initialise auto mode buttons and selector
        autoGoalEnableButton.setDisable(true); // cannot enable goals until connected
        autoGoalDisableButton.setDisable(true);
        autoGoalDisableAllButton.setDisable(true);
        autoGoalSelector.getItems().setAll("Collect Samples","Stream Object Detection");
        autoGoalSelector.setDisable(true); // cannot select goal until connected
        
        // initialise combo boxes
        positionEditor.getEditor().setText(":0.0,0.0,0.0,0.0");
        
        // initialise other objects
        runAfterInitList = new ArrayList<>();
        armDataController = new ArmDataController();
        String default_file = "example_data_bad2.dat";
        try {
            armDataController.importFile(new File(default_file));  
            dataFileTextField.setText(default_file);
            List<String> list = armDataController.getAllItems();
            for (String item : list) {
                positionSelector.getItems().add(item);
                positionEditor.getItems().add(item);
            } 
        } catch (IOException | FormatException ex) {
            runAfterInitList.add(new Runnable() {
                @Override
                public void run() {
                    Alert alert = new Alert(AlertType.ERROR, ex.getMessage());
                    alert.setHeaderText("Invalid Data File.");
                    alert.showAndWait();
                }
            });
            
        } 
    }
    
    public void runAfterInit() {
        for (Runnable method : runAfterInitList) {
            method.run();
        }
    }
    
    public void connectRoverButtonPressed () {
        if (connectRoverButton.isSelected()) {
            String selectedIpAddress = ipSelector.getValue();
            if (selectedIpAddress == null) { // nothing selected
                Alert alert = new Alert(AlertType.ERROR, "Invalid IP address selected.");
                alert.setHeaderText("Cannot connect.");
                alert.show();
                connectRoverButton.setSelected(false);
                return;
            }
            Alert alert = new Alert(AlertType.INFORMATION, 
                            "Please wait until a connection is established with the rover.");
            alert.setHeaderText("Connecting...");
            alert.show();
            // Connecting ...
            // Connected
            if (alert.isShowing()) {
                alert.close();
            }            
            joyConnectButton.setDisable(false);
            armConnectButton.setDisable(false);
            vidConnectButton.setDisable(false);
            autoGoalEnableButton.setDisable(false);
            autoGoalDisableButton.setDisable(false);
            autoGoalDisableAllButton.setDisable(true); // no goals enabled initially
            autoGoalSelector.setDisable(false);
            ipSelector.setDisable(true);
        }
        else {
            Alert alert = new Alert(AlertType.INFORMATION,
                            "Please wait until the rover is disconnected.");
            alert.setHeaderText("Disconnecting...");
            alert.show();
            // Disconnecting ...
            // Disconnected
            if (alert.isShowing()) {
                alert.close();
            }
            joyConnectButton.setDisable(true);
            armConnectButton.setDisable(true);
            vidConnectButton.setDisable(true);
            autoGoalEnableButton.setDisable(true);
            autoGoalDisableButton.setDisable(true);
            autoGoalDisableAllButton.setDisable(true);
            autoGoalSelector.setDisable(true);
            autoGoalSelector.getSelectionModel().clearSelection(); // show prompt again
            ipSelector.setDisable(false);
        }
    }
    
    public void joyConnectButtonPressed () {
        if (joyConnectButton.isSelected()) {
            // Connecting joystick ...
            // Connected
        }
        else {
            // Disconnecting joystick ...
            // Disconnected
        }
    }
    
    public void armConnectButtonPressed () {
        if (armConnectButton.isSelected()) {
            // Connecting arm ...
            // Connected
        }
        else {
            // Disconnecting arm ...
            // Disconnected
        }
    }
    
    public void vidConnectButtonPressed () {
        if (vidConnectButton.isSelected()) {
            // Connecting video ...
            // Connected
        }
        else {
            // Disconnecting video ...
            // Disconnected
        }
    }
    
    public void autoGoalEnableButtonPressed () {
        
    }
    
    public void autoGoalDisableButtonPressed () {
        
    }
    
    public void autoGoalDisableAllButtonPressed () {
        
    }
    
    /**
     * Event handler for mouse press on joystick.
     * @param e 
     */
    public void pressCoordsJoystick (MouseEvent e) {
        joy_mouse_x = e.getX();
        joy_mouse_y = e.getY();
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
        dispJoyY.setText(String.format("%.1f",centery));
    }
    
    /**
     * Event handler for when mouse is dragged on joystick.
     * @param e
     */
    public void updateJoystick (MouseEvent e) {
        // get distance between click and drag
        double drag_delx = e.getX() - joy_mouse_x;
        double drag_dely = e.getY() - joy_mouse_y;
        
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
        double sliderX = e.getX();
        double startX = sliderLine.getStartX();
        double endX = sliderLine.getEndX();
        if (sliderX >= endX) {
            sliderX = endX;
        }
        else if (sliderX <= startX) {
            sliderX = startX;
        }
        gripperButton.setText("Close Gripper");
        gripper_val = 90*(sliderX-startX)/(endX-startX);
        setArmGui();
    }
    
    /**
     * Event handler for when gripperButton is pressed
     */
    public void gripperButtonPressed () {
        double toSetX;
        double startX = sliderLine.getStartX();
        double endX = sliderLine.getEndX();
        if (gripperButton.getText().equals("Close Gripper")) {
            gripperButton.setText("Open Gripper");
            toSetX = endX;
        }
        else { // "Open Gripper"
            gripperButton.setText("Close Gripper");
            toSetX = startX;
        }
        gripper_val = 90*(toSetX-startX)/(endX-startX);
        setArmGui();
    }
    
    /**
     * Event handler for when the first arm joint is dragged
     * @param e 
     */
    public void updateArmSeg1 (MouseEvent e) {
        // Find new base servo angle
        double dx1 = e.getX() - armX[0];
        double dy1 = e.getY() - armY[0];
        double base_ang = armT[0];
        double top_ang = armT[2];
        double dthet1 = atan2(dy1,dx1) - base_ang;
        base_ang = base_ang + dthet1;
        if (seg3down) {
            top_ang = seg3down_ang - armT[1] - base_ang;
        }
        setAngles(base_ang, armT[1], top_ang);
        forwardKinematics();
        setArmGui();
    }
    
    /**
     * Event handler for when the second arm joint is dragged
     * @param e 
     */    
    public void updateArmSeg2 (MouseEvent e) {
        if (!seg3down) {
            double [] angs = inverseKinematics2R(armX[3],armY[3],e.getX(),e.getY());
            double base_ang = angs[0];
            double elbow_ang = angs[1];
            setAngles(base_ang, elbow_ang, armT[2]);
        }
        else {
            double reqx3 = e.getX() + segL*cos(seg3down_ang);
            double reqy3 = e.getY() + segL*sin(seg3down_ang);
            double[] angs = inverseKinematics2R(reqx3,reqy3,e.getX(),e.getY());
            double base_ang = angs[0];
            double elbow_ang = angs[1];
            double top_ang = seg3down_ang - elbow_ang - base_ang;
            setAngles(base_ang, elbow_ang, top_ang);
        }
        
        forwardKinematics();
        setArmGui();
    }
    
    /**
     * Event handler for when the final joint is dragged
     * @param e 
     */    
    public void updateArmSeg3 (MouseEvent e) {
        // Find angle of last segment relative to ground
        double reqx3 = e.getX();
        double reqy3 = e.getY();
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
        
        setAngles(base_ang, elbow_ang, top_ang);
        forwardKinematics();
        setArmGui();
    }
    
    /**
     * Event handler for when limitsButton is pressed.
     */
    public void limitsButtonPressed() {
        if (limitsButton.isSelected()) {
            limits_active = true;
            sumLimitsButton.setDisable(false);
        }
        else {
            limits_active = false;
            sum_limit_active = false;
            sumLimitsButton.setSelected(false);
            sumLimitsButton.setDisable(true);
        }
    }
    
    public void sumLimitsButtonPressed() {
        if (sumLimitsButton.isSelected()) {
            sum_limit_active = true;
        }
        else {
            sum_limit_active = false;
        }
    }
    
    public void positionSaveButtonPressed () {
        if (armDataController.haveFile()) {
            String data = positionEditor.getValue();
            try {
                armDataController.editDataItem(data);
            } catch (IOException ex) {
                Logger.getLogger(MainFxmlController.class.getName()).log(Level.SEVERE, null, ex);
            }
            positionSelector.getItems().clear();
            positionEditor.getItems().clear();
            List<String> list = armDataController.getAllItems();
            for (String item : list) {
                positionSelector.getItems().add(item);
                positionEditor.getItems().add(item);
            }
        }
    }
    
    public void positionRemoveButtonPressed () {
        if (armDataController.haveFile()) {
            String data = positionEditor.getValue();
            try {
                armDataController.removeDataItem(data);
            } catch (IOException ex) {
                Logger.getLogger(MainFxmlController.class.getName()).log(Level.SEVERE, null, ex);
            }
            positionSelector.getItems().clear();
            positionEditor.getItems().clear();
            List<String> list = armDataController.getAllItems();
            for (String item : list) {
                positionSelector.getItems().add(item);
                positionEditor.getItems().add(item);
            }
        }
    }
    
    public void positionSetButtonPressed () {
        String value;
        if ((value = positionSelector.getValue()) != null) {
            double[] angles = armDataController.parseData(value);
            boolean possible = setAngles(angles[0],angles[1],angles[2]);
            if (!possible) {
                Alert alert = new Alert(AlertType.WARNING, 
                        "This arm setting is not possible with the current angle "
                      + "limits. Disable limits to enable this setting (not recommended).");
                alert.setHeaderText("Cannot Set Arm.");
                alert.show();
            }
            forwardKinematics();
            setArmGui();
        }
    }
    
    public void drop1PositionButtonPressed () {
        
    }
    
    public void drop2PositionButtonPressed () {
        
    }
    
    public void watchPositionButtonPressed () {
        
    }
    
    public void pickPositionButtonPressed () {
        
    }
    
    public void seg3DownButtonPressed () {
        if (seg3DownButton.isSelected()) {
            seg3down = true;
            double reqx3 = armX[2] + cos(seg3down_ang)*segL;
            double reqy3 = armY[2] + sin(seg3down_ang)*segL;
            double[] angs = inverseKinematics2R(reqx3,reqy3,armX[2],armY[2]);
            double base_ang = angs[0];
            double elbow_ang = angs[1];
            double top_ang = seg3down_ang - elbow_ang - base_ang;
            if (top_ang < -PI) {
                top_ang = 2*PI + top_ang;
            }
            else if (top_ang > PI) {
                top_ang = top_ang - 2*PI;
            }
        
            boolean possible = setAngles(base_ang, elbow_ang, top_ang);
            if (!possible) {
                Alert alert = new Alert(AlertType.WARNING, 
                        "Enabling seg3Down in the current arm position would "
                      + "violate the angle limits. Disable angle limits to ignore this warning.");
                alert.setHeaderText("Cannot Set Arm.");
                alert.show();
                seg3down = false;
                seg3DownButton.setSelected(false);
            }
            forwardKinematics();
            setArmGui();
        }
        else {
            seg3down = false;
        }
    }
    
    public void seg3DownOffsetPickerClicked () {
        
    }
    
    public void dataFileOpenButtonPressed () {
        FileChooser chooser = new FileChooser();
        chooser.setTitle("Open Data File");
        chooser.setInitialDirectory(new File(System.getProperty("user.dir")));
        chooser.getExtensionFilters().add(new ExtensionFilter("Data files","*.dat"));
        File file = chooser.showOpenDialog(primaryStage);
        if (file != null) {
            String filename = file.getName();
            try {
                armDataController.importFile(file);
                List<String> list = armDataController.getAllItems();                
                positionSelector.getItems().clear();
                positionEditor.getItems().clear();
                for (String item : list) {
                    positionSelector.getItems().add(item);
                    positionEditor.getItems().add(item);
                }
                dataFileTextField.setText(filename);
            } catch (IOException ex) {
                Logger.getLogger(MainFxmlController.class.getName()).log(Level.SEVERE, null, ex);
            } catch (FormatException ex) {
                Alert alert = new Alert(AlertType.ERROR, ex.getMessage());
                alert.setHeaderText("Invalid Data File.");
                alert.showAndWait();
            }
        }
    }
    
    public void setCurrentStage (Stage stage) {
        primaryStage = stage;
    }
    
    /**
     * Set armX and armY based on angles in armT
     */
    private void forwardKinematics() {
        armX[1] = armX[0] + cos(armT[0]) * segL;
        armY[1] = armY[0] + sin(armT[0]) * segL;
        armX[2] = armX[1] + cos(armT[0] + armT[1]) * segL;
        armY[2] = armY[1] + sin(armT[0] + armT[1]) * segL;
        armX[3] = armX[2] + cos(armT[0] + armT[1] + armT[2]) * segL;
        armY[3] = armY[2] + sin(armT[0] + armT[1] + armT[2]) * segL;
    }
    
    /**
     * Set arm position in the GUI based on x,y coordinates in armX and armY.
     * Also set the angles in the positionEditor for easy saving.
     */
    private void setArmGui() {
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
        
        double endX = sliderLine.getEndX();
        double startX = sliderLine.getStartX();
        sliderBall.setCenterX((gripper_val/90)*(endX-startX) + startX);
        String armT0Str = String.format("%.1f",-armT[0]*180/PI);
        String armT1Str = String.format("%.1f",-armT[1]*180/PI);
        String armT2Str = String.format("%.1f",-armT[2]*180/PI);
        String gripperStr = String.format("%.1f",gripper_val);
        positionEditor.getEditor().setText(":"+armT0Str+","+armT1Str+","+armT2Str+","+gripperStr);
    }
    
    /**
     * Perform inverse kinematics on 2-rotation planar manipulator based on 
     * 3R manipulator setting. Sets the base and elbow angles.
     * @param reqx3 - required x position of end of final segment (3R)
     * @param reqy3 - required y position of end of final segment (3R)
     * @param reqx2 - required x position of end of second segment
     * @param reqy2 - required y position of end of second segment
     * @return - new base and elbow angles to be set
     */
    private double[] inverseKinematics2R(double reqx3, double reqy3, 
                                       double reqx2, double reqy2) {
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
    
    private boolean setAngles(double base_ang, double elbow_ang, double top_ang) {
        
        if (limits_active) {
        
            if (abs(base_ang) > lim_base) {
                return false;
            }
            if (abs(elbow_ang) > lim_elbow) {
                return false;
            }
            if (abs(top_ang) > lim_top) {
                return false;
            }
            if (sum_limit_active && (abs(elbow_ang + top_ang) > lim_sum_angles)) {
                return false;
            }
        
        }
        
        armT[0] = base_ang;
        armT[1] = elbow_ang;
        armT[2] = top_ang;
        return true;
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
