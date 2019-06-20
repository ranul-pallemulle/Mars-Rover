/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package UI;


import Backend.Sender;
import java.io.IOException;
import static java.lang.Math.acos;
import static java.lang.Math.atan2;
import static java.lang.Math.cos;
import static java.lang.Math.sin;
import static java.lang.Math.sqrt;
import javafx.scene.input.MouseEvent;
import java.net.URL;
import java.net.UnknownHostException;
import java.util.ResourceBundle;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.fxml.Initializable;
import javafx.scene.Parent;
import javafx.scene.shape.Circle;
import javafx.scene.text.Text;
import javafx.scene.Scene; 
import javafx.scene.paint.Color;
import javafx.scene.shape.Line;
import javafx.scene.shape.Rectangle;
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
            
    public double deltx = 0;
    public double delty = 0; //location relative to center
    String dispx, dispy;
    boolean enableTEST = false;
    boolean enablevid = false;
    boolean enablerover = false;
    boolean enablejoystick = false;
    boolean firstjoyclick = true;
    double initialoffsetx = 0;
    double initialoffsety = 0;    
    boolean test = true;
    String IPADDRESS = "172.24.1.1";
    
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
    

    
    public void connectjoystick(MouseEvent e){
        if(enablejoystick == false){
            enablejoystick = true;
            ButtonJoystickStart.setFill(Color.web("#00FF00"));
            System.out.println("CONNECTING TO JOYSTICK");
            if(!test){
                command_sender.startPiApp("JOYSTICK", 5562);
                joystick_sender = new Sender(IPADDRESS, 5562);
                try{
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
        }else{
            if(!test){
                joystick_sender.sendData(0, 0);
                command_sender.stopPiApp("JOYSTICK");
            }
            enablejoystick = false;
            ButtonJoystickStart.setFill(Color.web("#FF0000"));
            System.out.println("DISCONNECTING FROM JOYSTICK");
        }
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
            Controller.pass_main_sender(command_sender);
            Stage armStage = new Stage();
//            Controller.setStage(armStage);
            armroot.getStylesheets().add("UI/style.css");

            Scene armscene = new Scene(armroot, 500, 500);

            armStage.setTitle("ARM");
            armStage.setScene(armscene);
            armStage.setResizable(false);
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
            }
        }
        catch (Exception a) {
        }
    }
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        // TODO
    }    
}
