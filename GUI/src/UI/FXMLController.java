/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package UI;


import java.io.IOException;
import static java.lang.Math.acos;
import static java.lang.Math.atan;
import static java.lang.Math.atan2;
import static java.lang.Math.cos;
import static java.lang.Math.sin;
import static java.lang.Math.sqrt;
import javafx.scene.input.MouseEvent;
import java.net.URL;
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
    double[] armx = {250,300,350,400};
    double[] army = {250,250,250,250};
    int flip = 1;
    double prevang = 0.0;
    boolean enablearm = false;
    boolean enablevid = false;
    boolean enablerover = false;
    boolean controlend = true;
    boolean controlfreearm = true;
    int[] a = new int[4];
    double segLength = 50;
    
    public void setStage(Stage stage)
    {
        this.stage = stage;
        
    }
    /**
     * Initializes the controller class.
     */
    @FXML
    public void updatelocation(MouseEvent e) {
        if(enablerover){
            double joyx = e.getX();
            double joyy = e.getY();
            deltx = joyx - 250;
            delty = 250 - joyy;
            if(deltx * deltx + delty * delty < 10000){
                JoyButton.setCenterX(joyx);
                JoyButton.setCenterY(joyy);
            }else{
                double joyangle = atan(delty / deltx);
                if(deltx >= 0){
                    joyx = 250 + 100 * cos(joyangle);
                    joyy = 250 - 100 * sin(joyangle);
                }else{
                    joyx = 250 - 100 * cos(joyangle);
                    joyy = 250 + 100 * sin(joyangle);
                }
                deltx = joyx - 250;
                delty = 250 - joyy;
                JoyButton.setCenterX(joyx);
                JoyButton.setCenterY(joyy);            
            }
            dispx = String.format ("%.1f", deltx);
            dispy = String.format ("%.1f", delty);
            System.out.println(dispx + "," + dispy);
            DispJoyX.setText(dispx);
            DispJoyY.setText(dispy);
        }
    }
    
    public void snapback(MouseEvent e) {
        if(enablerover){
            JoyButton.setCenterX(250);
            JoyButton.setCenterY(250);
            deltx = 0;
            delty = 0;
            dispx = String.format ("%.1f", deltx);
            dispy = String.format ("%.1f", delty);
            System.out.println("itworked");
            DispJoyX.setText(dispx);
            DispJoyY.setText(dispy);
        }
    }
    
    public void arm3down(MouseEvent e) {
        if(enablearm){
            if(controlend == true){
                controlend = false;
                buttonarm3.setFill(Color.web("#00FF00"));
            }else{
                controlend = true;
                buttonarm3.setFill(Color.web("#FF0000"));
            }   
        }
    }
    
    public void armStart(MouseEvent e) {
        if(enablearm == false){
            enablearm = true;
            ButtonArmStart.setFill(Color.web("#00FF00"));
            blocker.setFill(Color.web("#00000000"));
            System.out.println("CONNECTING TO ARM");
        }else{
            enablearm = false;
            ButtonArmStart.setFill(Color.web("#FF0000"));
            blocker.setFill(Color.web("#FF000055"));
            System.out.println("DISCONNECTING FROM ARM");
        }   
    }
    
    public void freearm(MouseEvent e) {
        if(enablearm){
            if(controlfreearm == true){
                controlfreearm = false;
                freearm.setFill(Color.web("#FF0000"));
            }else{
                controlfreearm = true;
                freearm.setFill(Color.web("#00FF00"));
            }   
        }
    }
    
    public void updatearmseg1(MouseEvent e) {
        if(enablearm){
            double dx1 = e.getX() - armx[0];
            double dy1 = e.getY() - army[0];
            double newangp1 = atan2(dy1, dx1);
            double xangp1 = atan2(army[1]-army[0], armx[1]-armx[0]);
            double changeang = newangp1 - xangp1;
            double xangp2 = atan2((army[2] - army[1]),(armx[2] - armx[1]));
            double xangp3 = atan2((army[3] - army[2]),(armx[3] - armx[2]));
            //if(-180 * newangp1 / PI <= 130 && -180 * newangp1 / PI >= -130){
            armx[1] = armx[0] + cos(newangp1) * segLength;
            army[1] = army[0] + sin(newangp1) * segLength;
            armx[2] = armx[1] + cos(xangp2 + changeang) * segLength;
            army[2] = army[1] + sin(xangp2 + changeang) * segLength;
            armx[3] = armx[2] + cos(xangp3 + changeang) * segLength;
            army[3] = army[2] + sin(xangp3 + changeang) * segLength;
            if(controlend){
                armx[3] = armx[2] + cos(xangp3 + changeang) * segLength;
                army[3] = army[2] + sin(xangp3 + changeang) * segLength;
            }else{
                armx[3] = armx[2];
                army[3] = army[2] + segLength;
            }
            armseg1.setCenterX(armx[1]);
            armseg1.setCenterY(army[1]);
            armseg2.setCenterX(armx[2]);
            armseg2.setCenterY(army[2]);
            armseg3.setCenterX(armx[3]);
            armseg3.setCenterY(army[3]);
            lineseg1.setEndX(armx[1]);
            lineseg1.setEndY(army[1]);
            lineseg2.setStartX(armx[1]);
            lineseg2.setStartY(army[1]);
            lineseg2.setEndX(armx[2]);
            lineseg2.setEndY(army[2]);
            lineseg3.setStartX(armx[2]);
            lineseg3.setStartY(army[2]);
            lineseg3.setEndX(armx[3]);
            lineseg3.setEndY(army[3]);
        }
    }
    
    public void updatearmseg2(MouseEvent e) {
        if(enablearm){
            if(controlfreearm){
                if((e.getX() - 250)*(e.getX() - 250) + (e.getY() - 250)*(e.getY() - 250) < (4 * segLength * segLength)){
                    double dy2 = army[2] - army[0];
                    double dx2 = armx[2] - armx[0];
                    double dx = e.getX() - armx[0];
                    double dy = e.getY() - army[0];
                    double angle1 = atan2(dy, dx);  
                    double angle2 = atan2(dy2, dx2); 
                    double angseg1 = flip * acos(sqrt(dx * dx + dy * dy) / (2 * segLength));
                    //change
                    double square = sqrt(dx2 * dx2 + dy2 * dy2);
                    if(square > 100){
                        square = 100;
                    }
                    double angseg2 = flip * acos(square / (2 * segLength));
                    double changeang = angseg2 - angseg1 + angle1 - angle2;
                    //text(changeang*-180/PI, 100, 45);
                    double xangp3 = atan2((army[3] - army[2]),(armx[3] - armx[2]));
                    //print(y[3] + " " + y[2] + " : " + x[3] + " " + x[2] + " : " + xangp3 + " | ");
                    armx[1] = armx[0] + cos(angseg1+angle1) * segLength;
                    army[1] = army[0] + sin(angseg1+angle1) * segLength;
                    armx[2] = e.getX();
                    army[2] = e.getY();
                    if(controlend){
                        armx[3] = armx[2] + cos(xangp3 + changeang) * segLength;
                        army[3] = army[2] + sin(xangp3 + changeang) * segLength;
                    }else{
                        armx[3] = armx[2];
                        army[3] = army[2] + segLength;
                    }
                }else{
                    double dx = e.getX() - armx[0];
                    double dy = e.getY() - army[0];
                    double newangp2 = atan2(dy, dx);
                    double xangp2 = atan2(army[2]-army[1], armx[2]-armx[1]);
                    double changeang = newangp2 - xangp2;
                    double xangp3 = atan2((army[3] - army[2]),(armx[3] - armx[2]));
                    armx[1] = armx[0]+segLength*cos(newangp2);
                    army[1] = army[0]+segLength*sin(newangp2);
                    armx[2] = armx[1]+segLength*cos(newangp2);
                    army[2] = army[1]+segLength*sin(newangp2);
                    if(controlend){
                        armx[3] = armx[2] + cos(xangp3 + changeang) * segLength;
                        army[3] = army[2] + sin(xangp3 + changeang) * segLength;
                    }else{
                        armx[3] = armx[2];
                        army[3] = army[2] + segLength;
                    }
                    if(newangp2 < prevang){
                        flip = 1;
                    }else if(newangp2 > prevang){
                        flip = -1;
                    }
                    prevang = newangp2;
                }
            }else{
                double dx2 = e.getX() - armx[1];
                double dy2 = e.getY() - army[1];
                double newangp2 = atan2(dy2, dx2);
                double xangp2 = atan2((army[2] - army[1]),(armx[2] - armx[1]));
                double changeang = newangp2 - xangp2;
                double xangp3 = atan2((army[3] - army[2]),(armx[3] - armx[2]));
                armx[2] = armx[1]+segLength*cos(xangp2 + changeang);
                army[2] = army[1]+segLength*sin(xangp2 + changeang);
                if(controlend){
                    armx[3] = armx[2] + cos(xangp3 + changeang) * segLength;
                    army[3] = army[2] + sin(xangp3 + changeang) * segLength;
                }else{
                    armx[3] = armx[2];
                    army[3] = army[2] + segLength;
                }
            }
            armseg1.setCenterX(armx[1]);
            armseg1.setCenterY(army[1]);
            armseg2.setCenterX(armx[2]);
            armseg2.setCenterY(army[2]);
            armseg3.setCenterX(armx[3]);
            armseg3.setCenterY(army[3]);
            lineseg1.setEndX(armx[1]);
            lineseg1.setEndY(army[1]);
            lineseg2.setStartX(armx[1]);
            lineseg2.setStartY(army[1]);
            lineseg2.setEndX(armx[2]);
            lineseg2.setEndY(army[2]);
            lineseg3.setStartX(armx[2]);
            lineseg3.setStartY(army[2]);
            lineseg3.setEndX(armx[3]);
            lineseg3.setEndY(army[3]);
        }
    }
    
    public void updatearmseg3(MouseEvent e) {
        if(enablearm){
            if(controlend){
                double dxp3 = e.getX() - armx[2];
                double dyp3 = e.getY() - army[2];
                double angp3 = atan2(dyp3, dxp3);
                armx[3] = armx[2] + cos(angp3) * segLength;
                army[3] = army[2] + sin(angp3) * segLength;
            }else{
                armx[3] = armx[2];
                army[3] = army[2] + segLength;
            }
            armseg1.setCenterX(armx[1]);
            armseg1.setCenterY(army[1]);
            armseg2.setCenterX(armx[2]);
            armseg2.setCenterY(army[2]);
            armseg3.setCenterX(armx[3]);
            armseg3.setCenterY(army[3]);
            lineseg1.setEndX(armx[1]);
            lineseg1.setEndY(army[1]);
            lineseg2.setStartX(armx[1]);
            lineseg2.setStartY(army[1]);
            lineseg2.setEndX(armx[2]);
            lineseg2.setEndY(army[2]);
            lineseg3.setStartX(armx[2]);
            lineseg3.setStartY(army[2]);
            lineseg3.setEndX(armx[3]);
            lineseg3.setEndY(army[3]);
        }
    }
    
    public void connectrover(MouseEvent e){
        if(enablerover == false){
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
    
    public void openArm(MouseEvent e){
        try {
            final FXMLLoader armloader = new FXMLLoader(getClass().getResource("Arm.fxml"));
            final Parent armroot = (Parent) armloader.load();
            Stage armStage = new Stage();
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
