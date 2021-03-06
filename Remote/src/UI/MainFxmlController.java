/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package UI;

import Backend.JoystickController;
import Backend.ArmDataController;
import Backend.AutoModeManager;
import Backend.Connection;
import Backend.DepCameraController;
import Backend.Diagnostics;
import Backend.IPAddressManager;
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
import java.util.NoSuchElementException;
import java.util.Queue;
import java.util.ResourceBundle;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import java.util.logging.Level;
import java.util.logging.Logger;
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
import javafx.scene.control.ScrollBar;
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
import org.freedesktop.gstreamer.State;

/**
 * FXML Controller class
 *
 * @author Ranul Pallemulle
 */
public class MainFxmlController implements Initializable {
    
    // Main Connection
    @FXML private ToggleButton connectRoverButton;
    @FXML private ComboBox<String> ipSelector;
    // Joystick
    @FXML private Circle joyBackCircle;
    @FXML private Circle joyFrontCircle;
    @FXML private Text dispJoyX;
    @FXML private Text dispJoyY;
    @FXML private ToggleButton joyConnectButton;
    // Robotic Arm
    @FXML private Circle armJoint1;
    @FXML private Circle armJoint2;
    @FXML private Circle armJoint3;
    @FXML private Line lineSeg1;
    @FXML private Line lineSeg2;
    @FXML private Line lineSeg3;
    @FXML private Circle sliderBall;
    @FXML private Line sliderLine;
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
    @FXML private ToggleButton freeArmButton;
    @FXML private ToggleButton armConnectButton;
    // Messages
    @FXML private TextArea diagnosticsTextArea;
    @FXML private ToggleButton diagnosticsConnectButton;
    // Video Feed
    @FXML private SwingNode videoScreen;
    @FXML private ToggleButton vidConnectButton;
    // Deployable Camera
    @FXML private SwingNode depCamVideoScreen;
    @FXML private ComboBox<String> depPositionEditor;
    @FXML private ComboBox<String> depPositionSelector;
    @FXML private Circle depTopBall;
    @FXML private Line depTopLine;
    @FXML private Circle depMiddleBall;
    @FXML private Line depMiddleLine;
    @FXML private Circle depBottomBall;
    @FXML private Line depBottomLine;
    @FXML private ToggleButton depCameraEnableButton;
    
    private JoystickController joyController; // logic for joystick
    private RoboticArmController armController; // logic for robotic arm
    private ArmDataController armDataController; // logic for data file handling
    private ArrayList<Runnable> runAfterInitList; // run after UI initialisation
    private Connection connection; // connection to rover
    private Diagnostics diagnostics; // receive diagnostic messages
    private IPAddressManager ipAddressManager; // hold IP addresses and names
    private AutoModeManager autoModeManager; // hold auto goal on/off statuses
    private Pipeline pipe; // gstreamer pipeline for camera feed
    private Pipeline depCamPipe; // gstreamer pipeline for deployable camera feed
    private DepCameraController depCameraController; // logic for deployable camera
    private ArmDataController depArmDataController; // logic for data file handling

    public MainFxmlController() {
    }
    
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
        freeArmButton.setSelected(true);
        runAfterInitList.add((Runnable) () -> {
            limitsButtonPressed();
            sumLimitsButtonPressed();
            freeArmButtonPressed();
        } // simulate button presses
        );
        seg3DownOffsetPicker.setValueFactory(
                new SpinnerValueFactory.IntegerSpinnerValueFactory(-45,45,0));
        seg3DownOffsetPicker.setDisable(true);
        positionEditor.getEditor().setText(":0.0,0.0,0.0,0.0");
        
        // initialise arm data controller and try to open the default file
        armDataController = new ArmDataController(4);
        depArmDataController = new ArmDataController(3);
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
                alert.initOwner(Remote.getStage());
                alert.setHeaderText("Cannot Load Data File.");
                alert.showAndWait();
            });  
        }
        
        String default_deparm_file = "example_deparm.dat";
        try {
            depArmDataController.importFile(new File(default_deparm_file)); 
            List<String> list = depArmDataController.getAllItems();
            for (String item : list) {
                depPositionSelector.getItems().add(item);
                depPositionEditor.getItems().add(item);
            } 
        } catch (IOException | FormatException ex) {
            runAfterInitList.add((Runnable) () -> {
                Alert alert = new Alert(AlertType.ERROR, ex.getMessage());
                alert.initOwner(Remote.getStage());
                alert.setHeaderText("Cannot Load Deployable arm Data File.");
                alert.showAndWait();
            });  
        }
        
        // initialise IPAddressManager and ipSelector
        ipAddressManager = new IPAddressManager();
        List<String> names = ipAddressManager.getNames();
        for (String name : names) {
            ipSelector.getItems().add(name);
        }
               
        // initialise video connect button and screen
        vidConnectButton.setDisable(true); // cannot activate until connected
        createEmptyVideoScreen(videoScreen);
        createEmptyVideoScreen(depCamVideoScreen);
        
        // initialise deployable camera button and selectors
        depCameraEnableButton.setDisable(true);
        depPositionEditor.getEditor().setText(":0.0,0.0,0.0");
        
        // initialise deployable camera controller
        depCameraController = new DepCameraController();
        depCameraController.initialiseConnection((Consumer<Exception>)(e)->{
            Platform.runLater(()->{
                onDepCameraDisconnected(e);
            });
        });
 
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
        diagnostics.initialiseConnection((Consumer<Exception>)(e)->{
            // do nothing
        });
        diagnosticsTextArea.setWrapText(true);
        diagnosticsTextArea.setText(""); // else null pointer when trying to appendText
        runAfterInitList.add((Runnable) () -> {
            ScrollBar vertScroll = (ScrollBar) diagnosticsTextArea.lookup(".scroll-bar:vertical");
            vertScroll.setDisable(true);
        });
        
        // initialise main connection
        connection = new Connection((Consumer<Exception>)(e)->{
            Platform.runLater(()->{
                onRoverDisconnected(e);
            });
        });
        
        // initialise AutoModeManager
        autoModeManager = new AutoModeManager(connection);
        
        // initialise auto mode buttons and selector
        List<String> goals = autoModeManager.getNames();
        autoGoalEnableButton.setDisable(true);
        autoGoalDisableAllButton.setDisable(true);
         for (String name : goals) {
            autoGoalSelector.getItems().add(name);
        }
        autoGoalSelector.setDisable(true);
    }
    
    
    /**
     * Event handler for when connectRoverButton is pressed.
     */
    public void connectRoverButtonPressed () {
        if (connectRoverButton.isSelected()) {
            String selectedIpAddress = ipAddressManager.getIpFromKey(ipSelector.getValue());
            ipAddressManager.setCurrentIP(selectedIpAddress);
            if (selectedIpAddress == null) { // nothing selected
                Alert alert = new Alert(AlertType.ERROR, 
                        "Invalid IP address selected.");
                alert.initOwner(Remote.getStage());
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
            alert.initOwner(Remote.getStage());
            alert.setHeaderText("Connecting...");
            // Connect in a new thread, allow user to cancel in main thread
            new Thread(()-> {
                try {
                    connection.open(selectedIpAddress, 5560, 10, true); // 10 second timeout
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
                            conn_alert.initOwner(Remote.getStage());
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
            if (connection.isActive() && !diagnosticsConnectButton.isSelected()) {
                diagnosticsConnectButton.setSelected(true);
                diagnosticsConnectButtonPressed(); // simulate press
            }
        }
        else { // connectRoverButton deselected
            Alert alert = new Alert(AlertType.INFORMATION,
                            "Please wait until the rover is disconnected.");
            alert.initOwner(Remote.getStage());
            alert.setHeaderText("Disconnecting...");
            new Thread(()->{
                Platform.runLater(()->{
                    if (vidConnectButton.isSelected()) {
                        vidConnectButton.setSelected(false);
                        vidConnectButtonPressed(); // simulate press
                    }
                    if (depCameraEnableButton.isSelected()) {
                        depCameraEnableButton.setSelected(false);
                        depCameraEnableButtonPressed(); // simulate press
                    }
                    connection.close(); // run in application thread to guarantee order
                });
                
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
     * Event handler for when scanButton is pressed
     */
    public void scanButtonPressed() {
        ButtonType cancelButton = new ButtonType(
                    "Cancel", ButtonBar.ButtonData.YES);
        Alert alert = new Alert(AlertType.INFORMATION, 
                            "Please wait until the rover is located", cancelButton);
        alert.initOwner(Remote.getStage());
        alert.setHeaderText("Finding rover...");
        new Thread(()->{
            String ip = ipAddressManager.locateRaspberryPi();
            if (ip != null) {
                Platform.runLater(()->{
                    ipSelector.getItems().clear();
                    List<String> names = ipAddressManager.getNames();
                    for (String name : names) {
                        ipSelector.getItems().add(name);
                    }
                    if (alert.isShowing()) {
                        alert.close();
                    }
                });  
            }
            else {
                Platform.runLater(()->{
                    if (alert.isShowing()) {
                        alert.close();
                    }
                    Alert conn_alert = new Alert(AlertType.ERROR, 
                        "Search for 'raspberrypi.local' returned no results.");
                    conn_alert.initOwner(Remote.getStage());
                    conn_alert.setHeaderText("Could not locate rover.");
                    conn_alert.show();
                });
            }
        }).start();
        alert.showAndWait();
    }
    
    
    /**
     * Event handler for when diagnosticsConnectButton is pressed
     */
    public void diagnosticsConnectButtonPressed() {
        if (diagnosticsConnectButton.isSelected()) {
            try {
                
                diagnostics.getConnection().open(ipAddressManager.getCurrentIP(), 5570, 10, false); // no read timeout
                diagnostics.begin();
            } catch (IOException | IllegalArgumentException ex) {
                Alert alert = new Alert(AlertType.ERROR, ex.getMessage());
                alert.initOwner(Remote.getStage());
                alert.setHeaderText("Cannot Enable Diagnostics.");
                alert.show();
                diagnosticsConnectButton.setSelected(false);
            }
        }
        else {
            diagnostics.getConnection().close();
            while(diagnostics.getConnection().isActive()) {
                // wait
            }
            diagnosticsTextArea.clear();
        }
    }
    
    
    /**
     * Event handler for when joyConnectButton is pressed
     */
    public void joyConnectButtonPressed () {
        if (joyConnectButton.isSelected()) {
            try {
                connection.sendWithDelay("START JOYSTICK 5562",1);
                joyController.getConnection().open(ipAddressManager.getCurrentIP(), 5562, 10, true);
            } catch (IOException ex) {
                connection.sendWithDelay("STOP JOYSTICK",1);
                Alert alert = new Alert(AlertType.ERROR, ex.getMessage());
                alert.initOwner(Remote.getStage());
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
                armController.getConnection().open(ipAddressManager.getCurrentIP(), 5563, 10, true);
            } catch (IOException ex) {
                connection.sendWithDelay("STOP ROBOTICARM", 1);
                Alert alert = new Alert(AlertType.ERROR, ex.getMessage());
                alert.initOwner(Remote.getStage());
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
            connection.sendWithDelay("START STREAM", 1);
            startVideo(videoScreen);
        }
        else {
            connection.sendWithDelay("STOP STREAM", 1);
            if (pipe != null) {
                pipe.setState(State.NULL);
                pipe.dispose();
            }
            createEmptyVideoScreen(videoScreen);
        }
    }
    
    
    /**
     * Event handler for when autoGoalEnableButton is pressed
     */
    public void autoGoalEnableButtonPressed () {
        if (autoGoalEnableButton.isSelected()) {
            String selectedGoal= autoGoalSelector.getValue();
            autoModeManager.enableGoal(selectedGoal);
        }
        else {
            String selectedGoal = autoGoalSelector.getValue();
            autoModeManager.disableGoal(selectedGoal);
        }
    }
    
    
    /**
     * Event handler for when autoGoalDisableAllButton is pressed
     */
    public void autoGoalDisableAllButtonPressed () {
        autoModeManager.disableAllGoals();
        autoGoalEnableButton.setSelected(false);
    }
    
    
    /**
     * Event handler for when depCameraEnableButton is pressed
     */
    public void depCameraEnableButtonPressed () {
        if (depCameraEnableButton.isSelected()) {
            connection.sendWithDelay("START DepCamera_OFFLOAD pizero 5581", 1);
            try {
                depCameraController.getConnection().open(IPAddressManager.getCurrentIP(), 5581, 10, true);
//                TimeUnit.SECONDS.sleep(3);
                startVideoDepCam(depCamVideoScreen);
            } catch (IOException ex) {
                connection.sendWithDelay("STOP DepCamera_OFFLOAD", 1);
                Alert alert = new Alert(AlertType.ERROR, ex.getMessage());
                alert.initOwner(Remote.getStage());
                alert.setHeaderText("Cannot Enable Deployable Camera.");
                alert.show();
                depCameraEnableButton.setSelected(false);
            }
//             catch (InterruptedException ex) {
//                Logger.getLogger(MainFxmlController.class.getName()).log(Level.SEVERE, null, ex);
//            }
        }
        else {
            connection.sendWithDelay("STOP DepCamera_OFFLOAD", 1);
            if (depCamPipe != null) {
                depCamPipe.setState(State.NULL);
                depCamPipe.dispose();
            }
            createEmptyVideoScreen(depCamVideoScreen);
            // depCameraController.getConnection().close(); // already closed
        }
    }
    
    
    /**
     * Event handler for when autoGoalSelector's value is changed
     */
    public void autoGoalSelectorSelectionChanged () {
        String current = autoGoalSelector.getValue();
        if (current.equals("Enabled")) {
            autoGoalEnableButton.setSelected(true);
        }
        else if (current.equals("Disabled")) {
            autoGoalEnableButton.setSelected(false);
        }
        else { // probably null - not allowed
            Logger.getLogger(MainFxmlController.class.getName()).log(
                    Level.SEVERE, "Unexpected value present in autoGoalSelector");
        }
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
            alert.initOwner(Remote.getStage());
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
            alert.initOwner(Remote.getStage());
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
                    alert.initOwner(Remote.getStage());
                    alert.setHeaderText("Cannot Set Arm.");
                    alert.show();
                }
                else {
                    setArmGui();
                }
            } catch (FormatException ex) {
                Alert alert = new Alert(AlertType.ERROR, ex.getMessage());
                alert.initOwner(Remote.getStage());
                alert.setHeaderText("Cannot Set Arm.");
                alert.showAndWait();
            }
        }
    }
    
    
        /**
     * Event handler for when depPositionSaveButton is pressed.
     */
    public void depPositionSaveButtonPressed () {
        String data = depPositionEditor.getValue();
        try {
            boolean changed = depArmDataController.editDataItem(data);
            if (changed) {
                depPositionSelector.getItems().clear();
                depPositionEditor.getItems().clear();
                List<String> list = depArmDataController.getAllItems();
                for (String item : list) {
                    depPositionSelector.getItems().add(item);
                    depPositionEditor.getItems().add(item);
                }
            }
            
        } catch (IOException | FormatException ex) {
            Alert alert = new Alert(AlertType.ERROR, ex.getMessage());
            alert.initOwner(Remote.getStage());
            alert.setHeaderText("Cannot Save.");
            alert.showAndWait();
        }
    }
    
    
        /**
     * Event handler for when positionRemoveButton is pressed.
     */
    public void depPositionRemoveButtonPressed () {
        String data = depPositionEditor.getValue();
        try {
            depArmDataController.removeDataItem(data);
            depPositionSelector.getItems().clear();
            depPositionEditor.getItems().clear();
            List<String> list = depArmDataController.getAllItems();
            for (String item : list) {
                depPositionSelector.getItems().add(item);
                depPositionEditor.getItems().add(item);
            }
        } catch (IOException | NotFoundException | BadDeleteException ex) {
            Alert alert = new Alert(AlertType.ERROR, ex.getMessage());
            alert.initOwner(Remote.getStage());
            alert.setHeaderText("Cannot Delete Data.");
            alert.showAndWait();
        }
        
    }
    
    
        /**
     * Event handler for when positionSetButton is pressed.
     */
    public void depPositionSetButtonPressed () {
        String value;
        if ((value = depPositionSelector.getValue()) != null) {
            try {
                double[] angles = depArmDataController.parseDataDegrees(value);
                boolean possible = depCameraController.moveByServoAngles(
                        angles[0],angles[1],angles[2]);
                if (!possible) {
                    Alert alert = new Alert(AlertType.WARNING,
                            "This arm setting is not possible with the current "
                          + "angle limits. Disable limits to enable this "
                          + "setting (not recommended).");
                    alert.initOwner(Remote.getStage());
                    alert.setHeaderText("Cannot Set Deployable Arm.");
                    alert.show();
                }
                else {
                    String top = String.format("%.1f", depCameraController.getTopAngle());
                    String middle = String.format("%.1f", depCameraController.getMiddleAngle());
                    String bottom = String.format("%.1f", depCameraController.getBottomAngle());
                    depPositionEditor.getEditor().setText(":"+top+","+middle+","
                                                 +bottom);
                    double startX = depBottomLine.getStartX() + depBottomBall.getRadius();
                    double endX = depBottomLine.getEndX() - depBottomBall.getRadius();
                    double val = depCameraController.getBottomAngle();
                    depBottomBall.setCenterX(((val+120)/240)*(endX-startX) + startX);
                    startX = depMiddleLine.getStartX() + depMiddleBall.getRadius();
                    endX = depMiddleLine.getEndX() - depMiddleBall.getRadius();
                    val = depCameraController.getMiddleAngle();
                    depMiddleBall.setCenterX(((val+120)/240)*(endX-startX) + startX);
                    startX = depTopLine.getStartX() + depTopBall.getRadius();
                    endX = depTopLine.getEndX() - depTopBall.getRadius();
                    val = depCameraController.getTopAngle();
                    depTopBall.setCenterX(((val+120)/240)*(endX-startX) + startX);
                    
                    
                }
            } catch (FormatException ex) {
                Alert alert = new Alert(AlertType.ERROR, ex.getMessage());
                alert.initOwner(Remote.getStage());
                alert.setHeaderText("Cannot Set Deployable Arm.");
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
                alert.initOwner(Remote.getStage());
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
            alert.initOwner(Remote.getStage());
            alert.setHeaderText("Cannot Set Arm.");
            alert.show();
        }
        else {
            setArmGui();
        }
        
    }
    
    
    /**
     * Event handler for when freeArmButton is pressed.
     */
    public void freeArmButtonPressed() {
        if (freeArmButton.isSelected()) {
            armController.enableFreeArm(true);
        }
        else {
            armController.enableFreeArm(false);
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
                armDataController.checkRoboticArmDefaultData();
                
            } catch (IOException | FormatException ex) {
                dataFileTextField.setText("");
                Alert alert = new Alert(AlertType.ERROR, ex.getMessage());
                alert.initOwner(Remote.getStage());
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
    
    /**
     * Event handler for when the depcam top slider is dragged.
     * @param e 
     */
    public void depTopBallDragged (MouseEvent e) {
        double sliderX = e.getX();
        double startX = depTopLine.getStartX() + depTopBall.getRadius();
        double endX = depTopLine.getEndX() - depTopBall.getRadius();
        if (sliderX >= endX) {
            sliderX = endX;
        }
        else if (sliderX <= startX) {
            sliderX = startX;
        }
        double new_pos = 240*(sliderX-startX)/(endX-startX) - 120;
        depCameraController.moveTop(new_pos);
        depTopBall.setCenterX(sliderX);
        
        String top = String.format("%.1f", depCameraController.getTopAngle());
        String middle = String.format("%.1f", depCameraController.getMiddleAngle());
        String bottom = String.format("%.1f", depCameraController.getBottomAngle());
        depPositionEditor.getEditor().setText(":"+top+","+middle+","
                                                 +bottom);
    }
    
    /**
     * Event handler for when the depcam middle slider is dragged.
     * @param e 
     */
    public void depMiddleBallDragged (MouseEvent e) {
        double sliderX = e.getX();
        double startX = depMiddleLine.getStartX() + depMiddleBall.getRadius();;
        double endX = depMiddleLine.getEndX() - depMiddleBall.getRadius();;
        if (sliderX >= endX) {
            sliderX = endX;
        }
        else if (sliderX <= startX) {
            sliderX = startX;
        }
        double new_pos = 240*(sliderX-startX)/(endX-startX) - 120;
        depCameraController.moveMiddle(new_pos);
        depMiddleBall.setCenterX(sliderX);
        
        String top = String.format("%.1f", depCameraController.getTopAngle());
        String middle = String.format("%.1f", depCameraController.getMiddleAngle());
        String bottom = String.format("%.1f", depCameraController.getBottomAngle());
        depPositionEditor.getEditor().setText(":"+top+","+middle+","
                                                 +bottom);
    }
    
    /**
     * Event handler for when the depcam bottom slider is dragged.
     * @param e 
     */
    public void depBottomBallDragged (MouseEvent e) {
        double sliderX = e.getX();
        double startX = depBottomLine.getStartX() + depBottomBall.getRadius();;
        double endX = depBottomLine.getEndX() - depBottomBall.getRadius();;
        if (sliderX >= endX) {
            sliderX = endX;
        }
        else if (sliderX <= startX) {
            sliderX = startX;
        }
        double new_pos = 240*(sliderX-startX)/(endX-startX) - 120;
        depCameraController.moveBottom(new_pos);
        depBottomBall.setCenterX(sliderX);
        
        String top = String.format("%.1f", depCameraController.getTopAngle());
        String middle = String.format("%.1f", depCameraController.getMiddleAngle());
        String bottom = String.format("%.1f", depCameraController.getBottomAngle());
        depPositionEditor.getEditor().setText(":"+top+","+middle+","
                                                 +bottom);
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
    
    public void handleExit() {
        Platform.runLater(()->{
            if (connection.isActive()) {
                connectRoverButton.setSelected(false);
                connectRoverButtonPressed(); // simulate press
            }
        });
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
                    alert.initOwner(Remote.getStage());
                    alert.setHeaderText("Cannot Set Arm.");
                    alert.show();
                }
                else {
                    setArmGui();
                }
        }
        catch (FormatException | NotFoundException ex) {
            Alert alert = new Alert(AlertType.ERROR, ex.getMessage());
            alert.initOwner(Remote.getStage());
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
        depCameraEnableButton.setDisable(false);
        autoGoalEnableButton.setDisable(false);
        autoGoalDisableAllButton.setDisable(false);
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
        depCameraEnableButton.setDisable(true);
        depCameraEnableButton.setSelected(false);
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
        conn_alert.initOwner(Remote.getStage());
        conn_alert.setHeaderText("Disconnected");
        conn_alert.showAndWait();
    }
    
    private void onJoyDisconnected(Exception e) {
    
    }
    
    private void onArmDisconnected(Exception e) {
    
    }
    
    private void onDepCameraDisconnected(Exception e) {
        
    }
    
    private void onDiagnosticMessageReceived(Queue<String> q) {
        diagnosticsTextArea.setText("");
        try {
            for (String msg : q) {
                diagnosticsTextArea.appendText(msg+"\n");
            }
        } catch (NoSuchElementException e) {
            // ignore
        }
        diagnosticsTextArea.setScrollTop(Double.MAX_VALUE);
    }
    
    
    private void createEmptyVideoScreen(final SwingNode swingNode) {
        SimpleVideoComponent vc = new SimpleVideoComponent();
        SwingUtilities.invokeLater(()->{
            swingNode.setContent(vc);
        });
        vc.setPreferredSize(new Dimension(640,400));
//        swingNode.setVisible(true);
        vc.setKeepAspect(true);
    }
    
    
    private void startVideo(final SwingNode swingNode) {
        pipe = new Pipeline();
        String ip = ipAddressManager.getCurrentIP();
        if (ip == null) {
            return;
        }
        // ! videoflip video-direction=2 !
        String gst_str = "tcpclientsrc host="+ip+" port=5564 ! gdpdepay ! "
                + "rtph264depay ! avdec_h264 ! videoconvert ! capsfilter "
                + "caps=video/x-raw,width=640,height=400";
        SimpleVideoComponent vc = new SimpleVideoComponent();
        vc.getElement().set("sync", false);
        Bin bin = Gst.parseBinFromDescription(gst_str, true);
        pipe.addMany(bin, vc.getElement());
        Pipeline.linkMany(bin,vc.getElement());
        SwingUtilities.invokeLater(() -> {
            swingNode.setContent(vc);
        });
        vc.setPreferredSize(new Dimension(640,400));
//        vc.setKeepAspect(true);
        State old = State.NULL;
        while (old != State.PLAYING) {
            pipe.play();
            old = pipe.getState();
        }
        swingNode.setVisible(true);
    }
    
    private void startVideoDepCam(final SwingNode swingNode) {
        depCamPipe = new Pipeline();
        String ip = ipAddressManager.getCurrentIP();
        if (ip == null) {
            return;
        }
        String gst_str = "tcpclientsrc host="+ip+" port=5520 ! gdpdepay ! "
                + "rtph264depay ! avdec_h264 ! videoconvert ! "
                + "videoflip video-direction=2";
        SimpleVideoComponent vc = new SimpleVideoComponent();
        vc.getElement().set("sync", false);
        Bin bin = Gst.parseBinFromDescription(gst_str, true);
        depCamPipe.addMany(bin, vc.getElement());
        Pipeline.linkMany(bin, vc.getElement());
        SwingUtilities.invokeLater(() -> {
            swingNode.setContent(vc);
        });
        vc.setPreferredSize(new Dimension(640,400));
        State old = State.NULL;
        while (old != State.PLAYING) {
            depCamPipe.play();
            old = depCamPipe.getState();
        }
        swingNode.setVisible(true);
    }
    
}
