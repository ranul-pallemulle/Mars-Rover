/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package UI;

import Backend.JoystickController;
import Backend.ArmDataController;
import Backend.Connection;
import Backend.Diagnostics;
import Backend.RoboticArmController;
import Exceptions.BadDeleteException;
import Exceptions.FormatException;
import Exceptions.NotFoundException;
import java.awt.Dimension;
import java.io.File;
import java.io.IOException;
import static java.lang.Math.PI;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.Queue;
import java.util.ResourceBundle;
import java.util.function.Consumer;
import javafx.application.Platform;
import javax.swing.SwingUtilities;
import javafx.embed.swing.SwingNode;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.Alert;
import javafx.scene.control.Alert.AlertType;
import javafx.scene.control.Button;
import javafx.scene.control.ButtonBar;
import javafx.scene.control.ButtonType;
import javafx.scene.control.ComboBox;
import javafx.scene.control.Spinner;
import javafx.scene.control.SpinnerValueFactory;
import javafx.scene.control.TextArea;
import javafx.scene.control.TextField;
import javafx.scene.control.ToggleButton;
import javafx.scene.input.MouseEvent;
import javafx.scene.paint.Color;
import javafx.scene.shape.Circle;
import javafx.scene.shape.Line;
import javafx.scene.text.Text;
import javafx.stage.FileChooser;
import javafx.stage.FileChooser.ExtensionFilter;
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
    @FXML private ToggleButton autoGoalEnableButton;
    @FXML private Button autoGoalDisableAllButton;
    @FXML private ToggleButton limitsButton;
    @FXML private ToggleButton sumLimitsButton;
    @FXML private Button gripperButton;
    @FXML private TextField dataFileTextField;
    @FXML private ComboBox<String> positionEditor;
    @FXML private ComboBox<String> positionSelector;
    @FXML private ToggleButton seg3DownButton;
    @FXML private Spinner<Integer> seg3DownOffsetPicker;
    @FXML private TextArea diagnosticsTextArea;
    @FXML private ToggleButton diagnosticsConnectButton;
    
    private JoystickController joyController; // logic for joystick
    private RoboticArmController armController; // logic for robotic arm
    private ArmDataController armDataController; // logic for data file handling
    private ArrayList<Runnable> runAfterInitList; // run after UI initialisation
    private Connection connection; // connection to rover
    private Diagnostics diagnostics; // receive diagnostic messages
    
    
    /**
     * Initializes the controller class.
     * @param url
     * @param rb
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        // methods on this list are run after the UI is done initialising
        runAfterInitList = new ArrayList<>();

        // initialise joystick connect button
        joyConnectButton.setDisable(true);
        
        // initialise arm control buttons
        armConnectButton.setDisable(true);
        limitsButton.setSelected(true); // limits should be active by default
        sumLimitsButton.setSelected(true);
        runAfterInitList.add((Runnable) () -> {
            limitsButtonPressed();
            sumLimitsButtonPressed();
        } // simulate limits button presses
        );
        seg3DownOffsetPicker.setValueFactory(
                new SpinnerValueFactory.IntegerSpinnerValueFactory(-15,15,0));
        seg3DownOffsetPicker.setDisable(true);
        positionEditor.getEditor().setText(":0.0,0.0,0.0,0.0");
        
        // initialise arm data controller and try to open the default file
        armDataController = new ArmDataController();
        String default_file = "example_data.dat";
        try {
            armDataController.importFile(new File(default_file)); 
            dataFileTextField.setText(default_file);
            List<String> list = armDataController.getAllItems();
            for (String item : list) {
                positionSelector.getItems().add(item);
                positionEditor.getItems().add(item);
            } 
        } catch (IOException | FormatException ex) {
            runAfterInitList.add((Runnable) () -> {
                Alert alert = new Alert(AlertType.ERROR, ex.getMessage());
                alert.setHeaderText("Cannot Load Data File.");
                alert.showAndWait();
            });  
        }
        
        // initialise ipSelector
        ipSelector.getItems().setAll("WiFi","Ethernet","Local");
               
        // initialise video connect button and screen
        vidConnectButton.setDisable(true); // cannot activate until connected
        createVideoScreen(videoScreen);
        
        // initialise auto mode buttons and selector
        autoGoalEnableButton.setDisable(true);
        autoGoalDisableAllButton.setDisable(true);
        autoGoalSelector.getItems().setAll(
                "Collect Samples","Stream Object Detection");
        autoGoalSelector.setDisable(true);
        
        // initialise joystick controller
        double max_rad = joyBackCircle.getRadius() - joyFrontCircle.getRadius();
        joyController = new JoystickController(max_rad);
        joyController.initialiseConnection((Consumer<Exception>)(e)->{
            Platform.runLater(()->{
                onJoyDisconnected(e);
            });
        });
        
        // initialise robotic arm controller
        double[] armX = {250,300,350,400}; // initial coordinates for arm
        double[] armY = {250,250,250,250};
        double[] armT = {0,0,0}; // angles
        armController = new RoboticArmController(armX,armY,armT);
        armController.initialiseConnection((Consumer<Exception>)(e)->{
            Platform.runLater(()->{
                onArmDisconnected(e);
            });
        });
        
        // initialise diagnostics
        diagnostics = new Diagnostics((Consumer<Queue>)(q)->{
            Platform.runLater(()->{
                onDiagnosticMessageReceived(q);
            });
        });
        diagnosticsTextArea.setText(""); // else null pointer when trying to appendText
        
        // initialise main connection
        connection = new Connection((Consumer<Exception>)(e)->{
            Platform.runLater(()->{
                onRoverDisconnected(e);
            });
        });
    }
    
    
    /**
     * Event handler for when connectRoverButton is pressed.
     */
    public void connectRoverButtonPressed () {
        if (connectRoverButton.isSelected()) {
            String selectedIpAddress = ipSelector.getValue();
            if (selectedIpAddress == null) { // nothing selected
                Alert alert = new Alert(AlertType.ERROR, 
                        "Invalid IP address selected.");
                alert.setHeaderText("Cannot connect.");
                alert.show();
                connectRoverButton.setSelected(false);
                return;
            }
            ButtonType cancelButton = new ButtonType(
                    "Cancel", ButtonBar.ButtonData.YES);
            Alert alert = new Alert(AlertType.INFORMATION, 
                            "Please wait until a connection is established "
                          + "with the rover.", cancelButton);
            alert.setHeaderText("Connecting...");
            // Connect in a new thread, allow user to cancel in main thread
            new Thread(()-> {
                try {
                    connection.open("localhost", 5560, 2, true); // 2 second timeout
                    Platform.runLater(()->{
                        setButtonsOnConnectionActivated();
                        if (alert.isShowing()) {
                            alert.close();
                        }
                    });
                    connection.startPing();
                    
                } catch (IOException ex) {
                    Platform.runLater(()->{
                        if (alert.isShowing()) {
                            alert.close();
                        }
                        if (!(alert.getResult()==cancelButton)) {
                            // error isn't cancellation of connection opening
                            Alert conn_alert = new Alert(AlertType.ERROR, 
                                                         ex.getMessage());
                            conn_alert.setHeaderText("Cannot connect.");
                            conn_alert.show();
                        }
                        connectRoverButton.setSelected(false);
                    });
                }
            }).start();
            // user may cancel connection using the alert
            alert.showAndWait().ifPresent(response -> {
                if (response == cancelButton) {
                    connection.close();
                }
            });
        }
        else { // connectRoverButton deselected
            Alert alert = new Alert(AlertType.INFORMATION,
                            "Please wait until the rover is disconnected.");
            alert.setHeaderText("Disconnecting...");
            new Thread(()->{
                connection.close();
                Platform.runLater(()->{
                    if (alert.isShowing()) {
                        alert.close();
                    }
                    setButtonsOnConnectionDeactivated();
                });
            }).start();
            alert.showAndWait();
        }
    }
    
    
    /**
     * Event handler for when diagnosticsConnectButton is pressed
     */
    public void diagnosticsConnectButtonPressed() {
        if (diagnosticsConnectButton.isSelected()) {
            try {
                diagnostics.initialiseConnection((Consumer<Exception>)(e)->{
                    diagnostics.getConnection().close();
                });
                diagnostics.getConnection().open("localhost", 5570, 2, false); // no read timeout
                diagnostics.begin();
            } catch (IOException ex) {
                Alert alert = new Alert(AlertType.ERROR, ex.getMessage());
                alert.setHeaderText("Cannot Enable Diagnostics.");
                alert.show();
                diagnosticsConnectButton.setSelected(false);
            }
        }
        else {
            diagnostics.getConnection().close();
        }
    }
    
    
    /**
     * Event handler for when joyConnectButton is pressed
     */
    public void joyConnectButtonPressed () {
        if (joyConnectButton.isSelected()) {
            try {
                connection.sendWithDelay("START JOYSTICK 5562",1);
                joyController.getConnection().open("localhost", 5562, 2, true);
            } catch (IOException ex) {
                connection.sendWithDelay("STOP JOYSTICK",1);
                Alert alert = new Alert(AlertType.ERROR, ex.getMessage());
                alert.setHeaderText("Cannot Enable Joystick.");
                alert.show();
                joyConnectButton.setSelected(false);
            }
        }
        else {
            joyController.getConnection().close();
        }
    }
    
    
    /**
     * Event handler for when armConnectButton is pressed
     */
    public void armConnectButtonPressed () {
        if (armConnectButton.isSelected()) {
            try {
                connection.sendWithDelay("START ROBOTICARM 5563",1);
                armController.getConnection().open("localhost", 5563, 2, true);
            } catch (IOException ex) {
                connection.sendWithDelay("STOP ROBOTICARM", 1);
                Alert alert = new Alert(AlertType.ERROR, ex.getMessage());
                alert.setHeaderText("Cannot Enable Robotic Arm.");
                alert.show();
                armConnectButton.setSelected(false);
            }
        }
        else {
            armController.getConnection().close();
        }
    }
    
    
    /**
     * Event handler for when vidConnectButton is pressed
     */
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
    
    
    /**
     * Event handler for when autoGoalEnableButton is pressed
     */
    public void autoGoalEnableButtonPressed () {
        
    }
    
    
    /**
     * Event handler for when autoGoalDisableButton is pressed
     */
    public void autoGoalDisableButtonPressed () {
        
    }
    
    
    /**
     * Event handler for when autoGoalDisableAllButton is pressed
     */
    public void autoGoalDisableAllButtonPressed () {
        
    }
    
    
    /**
     * Event handler for mouse press on joystick.
     * @param e 
     */
    public void pressCoordsJoystick (MouseEvent e) {
        joyController.setMouseclickPosition(e.getX(), e.getY());
    }
    
    
    /**
     * Event handler for when mouse is released after dragging joystick.
     * @param e
     */
    public void snapBackJoystick (MouseEvent e) {
        joyController.returnToCenter();
        double newx = joyBackCircle.getCenterX() + joyController.getX();
        double newy = joyBackCircle.getCenterY() + joyController.getY();
        joyFrontCircle.setCenterX(newx);
        joyFrontCircle.setCenterY(newy);
        dispJoyX.setText(String.format("%.1f", newx));
        dispJoyY.setText(String.format("%.1f", newy));
    }
    
    
    /**
     * Event handler for when mouse is dragged on joystick.
     * @param e
     */
    public void updateJoystick (MouseEvent e) {
        joyController.update(e.getX(), e.getY());
        double newx = joyBackCircle.getCenterX() + joyController.getX();
        double newy = joyBackCircle.getCenterY() + joyController.getY();
        joyFrontCircle.setCenterX(newx);
        joyFrontCircle.setCenterY(newy);
        dispJoyX.setText(String.format("%.1f",newx));
        dispJoyY.setText(String.format("%.1f",-newy));
    }
    
    
    /**
     * Event handler for when the gripper slider is moved
     * @param e 
     */
    public void updateGripper (MouseEvent e) {
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
        armController.moveGripper(90*(sliderX-startX)/(endX-startX));
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
        armController.moveGripper(90*(toSetX-startX)/(endX-startX));
        setArmGui();
    }
    
    
    /**
     * Event handler for when the first arm joint is dragged
     * @param e 
     */
    public void updateArmSeg1 (MouseEvent e) {
        if (armController.moveFirstJoint(e.getX(), e.getY())) {
            setArmGui();
        }
        else {
            setArmLimitColours(true);
        }
    }
    
    
    /**
     * Event handler for when the second arm joint is dragged
     * @param e 
     */    
    public void updateArmSeg2 (MouseEvent e) {
        if (armController.moveSecondJoint(e.getX(), e.getY())) {
            setArmGui();
        }
        else {
            setArmLimitColours(true);
        }
    }
    
    
    /**
     * Event handler for when the final joint is dragged
     * @param e 
     */    
    public void updateArmSeg3 (MouseEvent e) {
        if (armController.moveThirdJoint(e.getX(), e.getY())) {
            setArmGui();
        }
        else {
            setArmLimitColours(true);
        }
    }
    
    
    /**
     * Event handler for when limitsButton is pressed.
     */
    public void limitsButtonPressed() {
        if (limitsButton.isSelected()) {
            armController.enableLimits(true);
            sumLimitsButton.setDisable(false);
        }
        else {
            armController.enableLimits(false);
            armController.enableSumLimit(false);
            sumLimitsButton.setSelected(false);
            sumLimitsButton.setDisable(true);
        }
    }
    
    
    /**
     * Event handler for when sumLimitsButton is pressed.
     */
    public void sumLimitsButtonPressed() {
        if (sumLimitsButton.isSelected()) {
            armController.enableSumLimit(true);
        }
        else {
            armController.enableSumLimit(false);
        }
    }
    
    
    /**
     * Event handler for when positionSaveButton is pressed.
     */
    public void positionSaveButtonPressed () {
        String data = positionEditor.getValue();
        try {
            boolean changed = armDataController.editDataItem(data);
            if (changed) {
                positionSelector.getItems().clear();
                positionEditor.getItems().clear();
                List<String> list = armDataController.getAllItems();
                for (String item : list) {
                    positionSelector.getItems().add(item);
                    positionEditor.getItems().add(item);
                }
            }
            
        } catch (IOException | FormatException ex) {
            Alert alert = new Alert(AlertType.ERROR, ex.getMessage());
            alert.setHeaderText("Cannot Save.");
            alert.showAndWait();
        }
    }
    
    
    /**
     * Event handler for when positionRemoveButton is pressed.
     */
    public void positionRemoveButtonPressed () {
        String data = positionEditor.getValue();
        try {
            armDataController.removeDataItem(data);
            positionSelector.getItems().clear();
            positionEditor.getItems().clear();
            List<String> list = armDataController.getAllItems();
            for (String item : list) {
                positionSelector.getItems().add(item);
                positionEditor.getItems().add(item);
            }
        } catch (IOException | NotFoundException | BadDeleteException ex) {
            Alert alert = new Alert(AlertType.ERROR, ex.getMessage());
            alert.setHeaderText("Cannot Delete Data.");
            alert.showAndWait();
        }
        
    }
    
    
    /**
     * Event handler for when positionSetButton is pressed.
     */
    public void positionSetButtonPressed () {
        String value;
        if ((value = positionSelector.getValue()) != null) {
            try {
                double[] angles = armDataController.parseData(value);
                boolean possible = armController.moveByServoAngles(
                        angles[0],angles[1],angles[2], angles[3]);
                if (!possible) {
                    Alert alert = new Alert(AlertType.WARNING,
                            "This arm setting is not possible with the current "
                          + "angle limits. Disable limits to enable this "
                          + "setting (not recommended).");
                    alert.setHeaderText("Cannot Set Arm.");
                    alert.show();
                }
                else {
                    setArmGui();
                }
            } catch (FormatException ex) {
                Alert alert = new Alert(AlertType.ERROR, ex.getMessage());
                alert.setHeaderText("Cannot Set Arm.");
                alert.showAndWait();
            }
        }
    }
    
    
    /**
     * Event handler for when drop1PositionButton is pressed.
     */
    public void drop1PositionButtonPressed () {
        setAnglesByName("DROP1");
    }
    
    
    /**
     * Event handler for when drop2PositionButton is pressed.
     */
    public void drop2PositionButtonPressed () {
        setAnglesByName("DROP2");
    }
    
    
    /**
     * Event handler for when watchPositionButton is pressed.
     */
    public void watchPositionButtonPressed () {
        setAnglesByName("WATCH");
    }
    
    
    /**
     * Event handler for when pickPositionButton is pressed.
     */
    public void pickPositionButtonPressed () {
        setAnglesByName("PICK");
    }
    
    
    /**
     * Event handler for when seg3DownButton is pressed.
     */
    public void seg3DownButtonPressed () {
        if (seg3DownButton.isSelected()) {
            if (!armController.enableSeg3Down(true)) {
                Alert alert = new Alert(AlertType.WARNING, 
                        "Enabling seg3Down in the current arm position would "
                      + "violate the angle limits. Disable angle limits to "
                      + "ignore this warning.");
                alert.setHeaderText("Cannot Set Arm.");
                alert.showAndWait();
                seg3DownButton.setSelected(false);
            }
            else {
                seg3DownOffsetPicker.setDisable(false);
                setArmGui();
            }
        }
        else {
            armController.enableSeg3Down(false);
            seg3DownOffsetPicker.setDisable(true);
        }
    }
    
    
    /**
     * Event handler for when seg3DownOffsetPicker is clicked.
     */
    public void seg3DownOffsetPickerClicked () {
        int value = seg3DownOffsetPicker.getValue();
        int backup = (int) 
                ( 180/PI * (armController.getSeg3DownAngle() - PI/2) );
        double new_angle = (90 + value)*PI/180;
        if (!armController.setSeg3DownAngle(new_angle)) {
            seg3DownOffsetPicker.getValueFactory().setValue(backup);
            Alert alert = new Alert(AlertType.WARNING, 
                        "Changing the seg3down angle in the current arm "
                      + "position would violate the angle limits. Disable "
                      + "angle limits to ignore this warning.");
            alert.setHeaderText("Cannot Set Arm.");
            alert.show();
        }
        else {
            setArmGui();
        }
        
    }
    
    
    /**
     * Event handler for when dataFileOpenButton is pressed.
     */
    public void dataFileOpenButtonPressed () {
        FileChooser chooser = new FileChooser();
        chooser.setTitle("Open Data File");
        chooser.setInitialDirectory(new File(System.getProperty("user.dir")));
        chooser.getExtensionFilters().add(new ExtensionFilter("Data files",
                                                              "*.dat"));
        File file = chooser.showOpenDialog(Remote.getStage());
        if (file != null) {
            String filename = file.getName();
            dataFileTextField.setText(filename);
            try {
                armDataController.importFile(file);
                
            } catch (IOException | FormatException ex) {
                dataFileTextField.setText("");
                Alert alert = new Alert(AlertType.ERROR, ex.getMessage());
                alert.setHeaderText("Invalid Data File.");
                alert.showAndWait();
                
            }
            List<String> list = armDataController.getAllItems();                
            positionSelector.getItems().clear();
            positionEditor.getItems().clear();
            for (String item : list) {
                positionSelector.getItems().add(item);
                positionEditor.getItems().add(item);
            } 
        }
    }
    
    /// public methods ///
    
    /**
     * Run all methods in runAfterInitList. This method is to be called by the 
     * main function when the stage is showing.
     */
    public void runAfterInit() {
        for (Runnable method : runAfterInitList) {
            method.run();
        }
    }
    
    public Connection getConnection() {
        return connection;
    }
    
    
    /// private methods ///
    
    
    /**
     * Set arm position in the GUI based on x,y coordinates in armX and armY.
     * Also set the angles in the positionEditor for easy saving.
     */
    private void setArmGui() {
        double[] arm_x = armController.getXCoords();
        double[] arm_y = armController.getYCoords();
        double[] arm_T = armController.getServoAngles();
        armJoint1.setCenterX(arm_x[1]);
        armJoint1.setCenterY(arm_y[1]);
        armJoint2.setCenterX(arm_x[2]);
        armJoint2.setCenterY(arm_y[2]);
        armJoint3.setCenterX(arm_x[3]);
        armJoint3.setCenterY(arm_y[3]);
        lineSeg1.setEndX(arm_x[1]);
        lineSeg1.setEndY(arm_y[1]);
        lineSeg2.setStartX(arm_x[1]);
        lineSeg2.setStartY(arm_y[1]);
        lineSeg2.setEndX(arm_x[2]);
        lineSeg2.setEndY(arm_y[2]);
        lineSeg3.setStartX(arm_x[2]);
        lineSeg3.setStartY(arm_y[2]);
        lineSeg3.setEndX(arm_x[3]);
        lineSeg3.setEndY(arm_y[3]);
        
        double gripper_val = armController.getGripperValue();
        double endX = sliderLine.getEndX();
        double startX = sliderLine.getStartX();
        sliderBall.setCenterX((gripper_val/90)*(endX-startX) + startX);
        
        setArmLimitColours(false);
        
        String armT0Str = String.format("%.1f",-arm_T[0]*180/PI);
        String armT1Str = String.format("%.1f",-arm_T[1]*180/PI);
        String armT2Str = String.format("%.1f",-arm_T[2]*180/PI);
        String gripperStr = String.format("%.1f",gripper_val);
        
        positionEditor.getEditor().setText(
                ":"+armT0Str+","+armT1Str+","+armT2Str+","+gripperStr);
    }
    
    
    /**
     * Set the GUI arm based on named configurations found in the data file.
     * @param name 
     */
    private void setAnglesByName(String name) {
        try {
            double[] angles = armDataController.getAnglesByName(name);
            boolean possible = armController.moveByServoAngles(
                    angles[0],angles[1],angles[2], angles[3]);
                if (!possible) {
                    Alert alert = new Alert(AlertType.WARNING,
                            "This arm setting is not possible with the current "
                          + "angle limits. Disable limits to enable this "
                          + "setting (not recommended).");
                    alert.setHeaderText("Cannot Set Arm.");
                    alert.show();
                }
                else {
                    setArmGui();
                }
        }
        catch (FormatException | NotFoundException ex) {
            Alert alert = new Alert(AlertType.ERROR, ex.getMessage());
            alert.setHeaderText("Cannot Set Arm.");
            alert.showAndWait();
        }
    }
    
    
    /**
     * Change the color of the GUI arm joints if the arm limits are preventing 
     * it from moving to the requested location.
     * @param yes - 
     */
    private void setArmLimitColours(boolean yes) {
        if (yes) {
            armJoint1.setFill(Color.web("#FF0000"));
            armJoint2.setFill(Color.web("#FF0000"));
            armJoint3.setFill(Color.web("#FF0000"));
        }
        else {
            armJoint1.setFill(Color.web("#FFAA55"));
            armJoint2.setFill(Color.web("#FFAA55"));
            armJoint3.setFill(Color.web("#FFAA55"));
        }
    }
    
    
    /**
     * Enable/Disable buttons when connection to rover is activated
     */
    private void setButtonsOnConnectionActivated() {
        joyConnectButton.setDisable(false);
        armConnectButton.setDisable(false);
        vidConnectButton.setDisable(false);
        autoGoalEnableButton.setDisable(false);
        autoGoalDisableAllButton.setDisable(true); // initially disabled
        autoGoalSelector.setDisable(false);
        ipSelector.setDisable(true);
    }
    
    
    /**
     * Enable/Disable buttons when connection to rover is deactivated. Also set
     * selected to false.
     */
    private void setButtonsOnConnectionDeactivated() {
        joyConnectButton.setDisable(true);
        joyConnectButton.setSelected(false);
        armConnectButton.setDisable(true);
        armConnectButton.setSelected(false);
        vidConnectButton.setDisable(true);
        vidConnectButton.setSelected(false);
        autoGoalEnableButton.setDisable(true);
        autoGoalEnableButton.setSelected(false);
        autoGoalDisableAllButton.setDisable(true);
        autoGoalSelector.setDisable(true);
        autoGoalSelector.getSelectionModel().clearSelection();
        ipSelector.setDisable(false);
    }
    
    
    private void onRoverDisconnected(Exception e) {
        if (!connectRoverButton.isSelected()) {
            return; // no error, we chose to disconnect
        }
        setButtonsOnConnectionDeactivated();
        connectRoverButton.setSelected(false);
        Alert conn_alert = new Alert(AlertType.ERROR, e.getMessage());
        conn_alert.setHeaderText("Disconnected");
        conn_alert.showAndWait();
    }
    
    private void onJoyDisconnected(Exception e) {
    
    }
    
    private void onArmDisconnected(Exception e) {
    
    }
    
    private void onDiagnosticMessageReceived(Queue<String> q) {
        diagnosticsTextArea.setText("");
        for (String msg : q) {
            diagnosticsTextArea.appendText(msg+"\n");
        }
    }
    
    
    /**
     * Initialize video screen using a GStreamer pipeline and set its 
     * dimensions.
     * @param swingNode - container to display video on
     */
    private void createVideoScreen(final SwingNode swingNode) {
        String gstPipeline;
        gstPipeline = "tcpclientsrc host=192.168.4.1 port=5564 ! gdpdepay ! "
                + "rtph264depay ! avdec_h264 ! videoconvert ! capsfilter "
                + "caps=video/x-raw,width=640,height=400";
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
        
        vc.setPreferredSize(new Dimension(640,400));
        vc.setKeepAspect(true);
    }
    
    
}
