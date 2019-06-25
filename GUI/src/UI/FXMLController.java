/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package UI;


import Backend.Sender;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import static java.lang.Math.acos;
import static java.lang.Math.atan2;
import static java.lang.Math.cos;
import static java.lang.Math.sin;
import static java.lang.Math.sqrt;
import javafx.scene.input.MouseEvent;
import java.net.URL;
import java.net.UnknownHostException;
import java.util.Arrays;
import java.util.ResourceBundle;
import java.util.concurrent.TimeUnit;
import java.util.logging.Level;
import java.util.logging.Logger;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.fxml.Initializable;
import javafx.geometry.Rectangle2D;
import javafx.scene.Parent;
import javafx.scene.shape.Circle;
import javafx.scene.text.Text;
import javafx.scene.Scene; 
import javafx.scene.paint.Color;
import javafx.scene.shape.Line;
import javafx.scene.shape.Rectangle;
import javafx.stage.Screen;
import javafx.stage.Stage;



/**
 * FXML Controller class
 *
 * @author JustinLiu
 */
public class FXMLController implements Initializable {
    
    @FXML private Circle JoyButton;
    @FXML private Stage stage;
    @FXML private Text DispJoyX;
    @FXML private Text DispJoyY;
    @FXML private Circle ButtonArm;
    @FXML private Rectangle ButtonJoystickStart;
    @FXML private Rectangle ButtonMain;
    @FXML private Rectangle ButtonVidStart;
    @FXML private Circle ButtonAuto;
    
    private ARMController armController; // keep a reference to the arm controller
            
    public double deltx = 0;
    public double delty = 0; //location relative to center
    String dispx, dispy;
    boolean enableTEST = false;
    boolean enablevid = false;
    boolean enablerover = false;
    boolean enablejoystick = false;
    boolean enableauto = false;
    boolean firstjoyclick = true;
    double initialoffsetx = 0;
    double initialoffsety = 0;    
    
    //String IPADDRESS = "192.168.4.1";
    String IPADDRESS = "10.42.0.137";
    boolean test = false;
    
    Sender command_sender = new Sender(IPADDRESS,5560);
    Sender joystick_sender;
    Sender arm_sender;
    Sender test_sender;
    
    
    public void setStage(Stage stage)
    {
        this.stage = stage;
        
    }
    
    /**
     * Initializes the controller class.
     */
    @FXML
    public void updatelocation(MouseEvent e) {
        if(enablejoystick){
            if(firstjoyclick){
                initialoffsetx = e.getX() - 250;
                initialoffsety = e.getY() - 250;
                firstjoyclick = false;
            }
            double joyx = e.getX() - initialoffsetx;
            double joyy = e.getY() - initialoffsety;
            deltx = joyx - 250;
            delty = 250 - joyy;
            if((deltx) * (deltx) + (delty) * (delty) < 10000){
                JoyButton.setCenterX(joyx);
                JoyButton.setCenterY(joyy);
            }else{
                double joyangle = atan2(delty, deltx);
                joyx = 250 + 100 * cos(joyangle);
                joyy = 250 - 100 * sin(joyangle);
                deltx = joyx - 250;
                delty = 250 - joyy;
                JoyButton.setCenterX(joyx);
                JoyButton.setCenterY(joyy);
            }
            if(test){
                dispx = String.format ("%.1f", deltx);
                dispy = String.format ("%.1f", delty);
                System.out.println(dispx + "," + dispy);
                DispJoyX.setText(dispx);
                DispJoyY.setText(dispy);
            }else{
                joystick_sender.sendData((int)deltx, (int)delty);
            }
        }
    }
    
    public void snapback(MouseEvent e) {
        if(enablejoystick){
            JoyButton.setCenterX(250);
            JoyButton.setCenterY(250);
            deltx = 0;
            delty = 0;
            firstjoyclick = true;
            
            if(test){   
                dispx = String.format ("%.1f", deltx);
                dispy = String.format ("%.1f", delty);
                System.out.println("itworked");
                DispJoyX.setText(dispx);
                DispJoyY.setText(dispy);
            }else{
                joystick_sender.sendData(0, 0);
                joystick_sender.sendData(0, 0);
                joystick_sender.sendData(0, 0);
                joystick_sender.sendData(0, 0);
                joystick_sender.sendData(0, 0);
                joystick_sender.sendData(0, 0);
                joystick_sender.sendData(0, 0);
                joystick_sender.sendData(0, 0);
                joystick_sender.sendData(0, 0);
            }
        }
    }
    
    public void togglejoystick_private() {
        if(enablejoystick == false){
            enablejoystick = true;
            ButtonJoystickStart.setFill(Color.web("#00FF00"));
            System.out.println("CONNECTING TO JOYSTICK");
            if(!test){
                if (!enableauto) {
                    command_sender.startPiApp("JOYSTICK", 5562);
                    joystick_sender = new Sender(IPADDRESS, 5562);
                    try {
                        TimeUnit.SECONDS.sleep(1);
                    } catch (InterruptedException ex) {
                        Logger.getLogger(ARMController.class.getName()).log(Level.SEVERE, null, ex);
                    }		
                    try {
                        joystick_sender.initialise();
                    } catch(UnknownHostException ex) {
                        System.out.println("unknown host");
                        return;
                    }
                    catch(IOException ex) {
                        System.out.println("io exception");
                        return;
                    }
                    //System.out.println("returned 1");
                }
                else {
                    command_sender.sendString("AUTO -> Goal Samples -> Override Joystick");
                }
            }
        }else{
            if(!test){
                if (!enableauto) {
                    joystick_sender.sendData(0, 0);
                    command_sender.stopPiApp("JOYSTICK");
                }
                else {
                    command_sender.sendString("AUTO -> Goal Samples -> Release Override Joystick");
                }
            }
            enablejoystick = false;
            ButtonJoystickStart.setFill(Color.web("#FF0000"));
            System.out.println("DISCONNECTING FROM JOYSTICK");
        }
    }
    
    public void connectjoystick(MouseEvent e){
        togglejoystick_private();
    }

    public void connectrover(MouseEvent e){
        if(enablerover == false){
            try{
            command_sender.initialise();
            } catch(UnknownHostException ex) {
                System.out.println("unknown host");
                return;
            }
            catch(IOException ex) {
                System.out.println("io exception");
                return;
            }
            
            enablerover = true;
            ButtonMain.setFill(Color.web("#00FF00"));
            System.out.println("CONNECTING TO ROVER");
        }else{
            
            enablerover = false;
            ButtonMain.setFill(Color.web("#FF0000"));
            System.out.println("DISCONNECTING FROM ROVER");
        }
    }
    
    public void connectvid(MouseEvent e){
        if(enablevid == false){
            enablevid = true;
            ButtonVidStart.setFill(Color.web("#00FF00"));
            System.out.println("CONNECTING TO VIDEO");
        }else{
            enablevid = false;
            ButtonVidStart.setFill(Color.web("#FF0000"));
            System.out.println("DISCONNECTING FROM VIDEO");
        }
    }
    
    public void openArm(MouseEvent e) throws IOException{
        try {
            final FXMLLoader armloader = new FXMLLoader(getClass().getResource("Arm.fxml"));
            final Parent armroot = (Parent) armloader.load();
            final ARMController Controller = armloader.<ARMController>getController();
            armController = Controller; // store 
            Controller.pass_main_sender(command_sender);
            Controller.pass_fxmlcontroller(this);
            Stage armStage = new Stage();
//            Controller.setStage(armStage);
            armroot.getStylesheets().add("UI/style.css");

            Scene armscene = new Scene(armroot, 500, 500);

            armStage.setTitle("ARM");
            armStage.setScene(armscene);
            armStage.setResizable(false);
            Rectangle2D primaryScreenBounds = Screen.getPrimary().getVisualBounds();
            armStage.setX(primaryScreenBounds.getMinX() + primaryScreenBounds.getWidth()/2);
            armStage.setY(primaryScreenBounds.getMinY() + primaryScreenBounds.getHeight()/2 - 250);
            armStage.show();
        }
        catch (IOException a) {
            
        }
    }
    
    // TODO    
    public void openVid(MouseEvent e){
        try {
//            final FXMLLoader vidloader = new FXMLLoader(getClass().getResource("Vid.fxml"));
//            final Parent vidroot = (Parent) vidloader.load();
//            Stage vidStage = new Stage();
//            vidroot.getStylesheets().add("UI/style.css");
//
//            Scene vidscene = new Scene(vidroot, 600, 400);
//
//            vidStage.setTitle("VIDEO");
//            vidStage.setScene(vidscene);
//            vidStage.setResizable(false);
//            vidStage.show();
            if(!test){
                command_sender.startPiApp("STREAM");
                TimeUnit.SECONDS.sleep(5);
                Runtime rt = Runtime.getRuntime();
                Process proc = rt.exec("gst-launch-1.0 tcpclientsrc host=192.168.4.1 port=5564 ! gdpdepay ! rtph264depay ! avdec_h264 ! videoconvert ! autovideosink sync=false");
                InputStream stdin = proc.getInputStream();
                InputStreamReader isr = new InputStreamReader(stdin);
                BufferedReader br = new BufferedReader(isr);
                String line = null;
                System.out.println("<OUTPUT>");
                while ( (line = br.readLine()) != null)
                    System.out.println(line);
                System.out.println("</OUTPUT>");
                int exitVal = proc.waitFor();            
                System.out.println("Process exitValue: " + exitVal);
            }
        }
        catch (Exception a) {
        }
    }
    
    public void toggleAuto(MouseEvent e){
        
        if (!enableauto) {
            ButtonAuto.setFill(Color.web("#00FF00"));
            if (enablejoystick) { // if joystick mode is on, switch it off
                togglejoystick_private();
            }
            if (armController != null && armController.isEnabled()) { // if arm mode is on, switch it off
                armController.togglearm_private();
            }
            if (!test) {
                command_sender.startPiApp("AUTO");
                try {
                    TimeUnit.SECONDS.sleep(1);
                } catch (InterruptedException ex) {
                    Logger.getLogger(FXMLController.class.getName()).log(Level.SEVERE, null, ex);
                }
                command_sender.sendString("AUTO -> Goal Samples start");
            }
            enableauto = true;
        }
        else {
            ButtonAuto.setFill(Color.web("#FF0000"));
            if (enablejoystick) { // if manual override is on, switch it off
                togglejoystick_private();
            }
            if (armController != null && armController.isEnabled()) { // if manual override is on, switch it off
                armController.togglearm_private();
            }
            if (!test) {
                command_sender.stopPiApp("AUTO");
            }
            enableauto = false;
        }
    }
    
    public boolean autoEnabled() {
        return enableauto;
    }
    
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        // TODO
    }    
}
