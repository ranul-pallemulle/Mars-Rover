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
    @FXML private Circle buttonarm3;
    @FXML private Circle freearm;
    @FXML private Rectangle ButtonArmStart;
    @FXML private Rectangle TEST;
    @FXML private Rectangle ButtonJoystickStart;
    @FXML private Rectangle ButtonMain;
    @FXML private Rectangle ButtonVidStart;
    @FXML private Line lineseg1;
    @FXML private Line lineseg2;
    @FXML private Line lineseg3;
    @FXML private Circle armseg1;
    @FXML private Circle armseg2;
    @FXML private Circle armseg3;
    @FXML private Rectangle blocker;
            
    public double deltx = 0;
    public double delty = 0; //location relative to center
    String dispx, dispy;
    String joint0ang, joint1ang, joint2ang;
    double[] armx = {250,300,350,400};
    double[] army = {250,250,250,250};
    double[] armang = {0,0,0};
    double mousexp2, mouseyp2;
    int flip = 1;
    double prevang = 0.0;
    boolean enablearm = false;
    boolean enableTEST = false;
    boolean enablevid = false;
    boolean enablerover = false;
    boolean enablejoystick = false;
    boolean controlend = true;
    boolean controlfreearm = true;
    boolean firstjoyclick = true;
    int[] a = new int[4];
    double segLength = 50;
    double initialoffsetx = 0;
    double initialoffsety = 0;    
    
    Sender command_sender = new Sender("172.24.1.1",5560);
    Sender joystick_sender;
    Sender arm_sender;
    Sender test_sender;
    
    public void setStage(Stage stage)
    {
        this.stage = stage;
        
    }
    
    double servoangle(double x3, double x2, double x1, double y3, double y2, double y1){
        double retangle = -180 * (atan2((y3 - y2),(x3 - x2)) - atan2((y2 - y1),(x2 - x1))) / Math.PI;
        if(retangle >= 180){
            retangle = retangle - 360;
        }else if(retangle < -180){
            retangle = retangle + 360;
        }
        return retangle;
    }
    
    void setarmlocation(double xjoint1, double xjoint2, double xjoint3, double yjoint1, double yjoint2, double yjoint3){
        armseg1.setCenterX(xjoint1);
        armseg1.setCenterY(yjoint1);
        armseg2.setCenterX(xjoint2);
        armseg2.setCenterY(yjoint2);
        armseg3.setCenterX(xjoint3);
        armseg3.setCenterY(yjoint3);
        lineseg1.setEndX(xjoint1);
        lineseg1.setEndY(yjoint1);
        lineseg2.setStartX(xjoint1);
        lineseg2.setStartY(yjoint1);
        lineseg2.setEndX(xjoint2);
        lineseg2.setEndY(yjoint2);
        lineseg3.setStartX(xjoint2);
        lineseg3.setStartY(yjoint2);
        lineseg3.setEndX(xjoint3);
        lineseg3.setEndY(yjoint3);
    }
    
    /**
     * Initializes the controller class.
     */
    @FXML
    public void updatelocation(MouseEvent e) {
        if(enablejoystick){
//            if(firstjoyclick){
//                initialoffsetx = e.getX() - 250;
//                initialoffsety = e.getY() - 250;
//                firstjoyclick = false;
//            }
            double joyx = e.getX(); // - initialoffsetx;
            double joyy = e.getY(); // - initialoffsety;
            deltx = joyx - 250;
            delty = 250 - joyy;
            if((deltx) * (deltx) + (delty) * (delty) < 10000){
                //when the joy circle reaches the edge, add offset, 
                //wait for mouse to reach edge before making joy circle on edge
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
//                initialoffsetx = 0;
//                initialoffsety = 0;
            }
//            Integer.decode(Double.toString(deltx));
//            Integer.decode(Double.toString(delty));
            joystick_sender.sendData((int)deltx, (int)delty);
//            dispx = String.format ("%.1f", deltx);
//            dispy = String.format ("%.1f", delty);
//            System.out.println(dispx + "," + dispy);
//            DispJoyX.setText(dispx);
//            DispJoyY.setText(dispy);
        }
    }
    
    public void snapback(MouseEvent e) {
        if(enablejoystick){
            JoyButton.setCenterX(250);
            JoyButton.setCenterY(250);
            deltx = 0;
            delty = 0;
//            dispx = String.format ("%.1f", deltx);
//            dispy = String.format ("%.1f", delty);
//            firstjoyclick = true;
//            System.out.println("itworked");
//            DispJoyX.setText(dispx);
//            DispJoyY.setText(dispy);
            joystick_sender.sendData(0, 0);
            joystick_sender.sendData(0, 0);
            joystick_sender.sendData(0, 0);
        }
    }
    

    
    public void connectjoystick(MouseEvent e){
        if(enablejoystick == false){
            enablejoystick = true;
            ButtonJoystickStart.setFill(Color.web("#00FF00"));
            System.out.println("CONNECTING TO JOYSTICK");
            command_sender.startPiApp("JOYSTICK", 5562);
            joystick_sender = new Sender("172.24.1.1", 5562);
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
        }else{
            joystick_sender.sendData(0, 0);
            command_sender.stopPiApp("JOYSTICK");
            enablejoystick = false;
            ButtonJoystickStart.setFill(Color.web("#FF0000"));
            System.out.println("DISCONNECTING FROM JOYSTICK");
        }
    }
    
    public void connecttest(MouseEvent e){
        if(enableTEST == false){
            enableTEST = true;
            TEST.setFill(Color.web("#00FF00"));
            System.out.println("CONNECTING TO TEST");
            command_sender.startPiApp("ARM", 5564);
//            System.out.println("returned 0");
            test_sender = new Sender("172.24.1.1", 5564);
            try{
            test_sender.initialise();
            } catch(UnknownHostException ex) {
                System.out.println("unknown host");
                return;
            }
            catch(IOException ex) {
                System.out.println("io exception");
                return;
            }
            //System.out.println("returned 1");
        }else{
            test_sender.stopPiApp("ARM");
            enableTEST = false;
            TEST.setFill(Color.web("#FF0000"));
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
//        final FXMLLoader armloader = new FXMLLoader(getClass().getResource("Arm.fxml"));
//        final Parent armroot = (Parent) armloader.load();
////        final ARMController controller = armloader.<ARMController>getController();
//        Stage armStage = new Stage();
////        controller.setStage(armStage);
//        armroot.getStylesheets().add("UI/style.css");
//        //root.getChildren().add(btn);
//        
//        Scene scene = new Scene(armroot, 500, 500);
//        
//        armStage.setTitle("ARM");
//        armStage.setScene(scene);
//        armStage.setResizable(false);
//        armStage.show();
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
            final FXMLLoader vidloader = new FXMLLoader(getClass().getResource("Vid.fxml"));
            final Parent vidroot = (Parent) vidloader.load();
            Stage vidStage = new Stage();
            vidroot.getStylesheets().add("UI/style.css");

            Scene vidscene = new Scene(vidroot, 600, 400);

            vidStage.setTitle("VIDEO");
            vidStage.setScene(vidscene);
            vidStage.setResizable(false);
            vidStage.show();
        }
        catch (IOException a) {
        }
    }
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        // TODO
    }    
}
