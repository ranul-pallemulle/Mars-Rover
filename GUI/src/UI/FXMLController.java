/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package UI;

import java.io.IOException;
import static java.lang.Math.atan;
import static java.lang.Math.cos;
import static java.lang.Math.sin;
import javafx.scene.input.MouseEvent;
import java.net.URL;
import java.util.ResourceBundle;
import java.util.logging.Level;
import java.util.logging.Logger;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.fxml.Initializable;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.shape.Circle;
import javafx.scene.text.Text;
import javafx.stage.Stage;


/**
 * FXML Controller class
 *
 * @author JustinLiu
 */
public class FXMLController implements Initializable {
    
    @FXML private Circle Joy;
    @FXML private Stage stage;
    @FXML private Text DispJoyX;
    @FXML private Text DispJoyY;
    @FXML private Circle buttonArm;
    
    public double deltx = 0;
    public double delty = 0; //location relative to center
    String dispx, dispy;
    
    public void setStage(Stage stage)
    {
        this.stage = stage;
    }
    /**
     * Initializes the controller class.
     */
    @FXML
    public void updatelocation(MouseEvent e) {
        double joyx = e.getX();
        double joyy = e.getY();
        deltx = joyx - 250;
        delty = 250 - joyy;
        if(deltx * deltx + delty * delty < 10000){
            Joy.setCenterX(joyx);
            Joy.setCenterY(joyy);
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
            Joy.setCenterX(joyx);
            Joy.setCenterY(joyy);
        }
        dispx = String.format ("%.1f", deltx);
        dispy = String.format ("%.1f", delty);
        System.out.println(dispx + "," + dispy);
        DispJoyX.setText(dispx);
        DispJoyY.setText(dispy);
    }
    public void snapback(MouseEvent e) {
        Joy.setCenterX(250);
        Joy.setCenterY(250);
        deltx = 0;
        delty = 0;
        dispx = String.format ("%.1f", deltx);
        dispy = String.format ("%.1f", delty);
        System.out.println("itworked");
        DispJoyX.setText(dispx);
        DispJoyY.setText(dispy);
    }
    public void openArm(MouseEvent e){
//        System.out.println("Opening Arm Window");
//        try {
//        FXMLLoader fxmlLoader = new FXMLLoader();
//        fxmlLoader.setLocation(getClass().getResource("Arm.fxml"));
//        /* 
//         * if "fx:controller" is not set in fxml
//         * fxmlLoader.setController(NewWindowController);
//         */
//        Scene scene = new Scene(fxmlLoader.load(), 500, 500);
//        Stage armStage = new Stage();
//        armStage.setTitle("Your arms");
//        armStage.setResizable(false);
//        armStage.setScene(scene);
//        armStage.show();
//        } catch (IOException a) {
//            Logger logger = Logger.getLogger(getClass().getName());
//            logger.log(Level.SEVERE, "Failed to create new Window.", a);
//        }
        try {
            final FXMLLoader loader = new FXMLLoader(getClass().getResource("Arm.fxml"));
            final Parent root = (Parent) loader.load();
            Stage armStage = new Stage();
            root.getStylesheets().add("UI/style.css");
            //root.getChildren().add(btn);

            Scene scene = new Scene(root, 500, 500);

            armStage.setTitle("Rover");
            armStage.setScene(scene);
            armStage.setResizable(false);
            armStage.show();
//            //ResourceBundle resources = null;
//            root = FXMLLoader.load(getClass().getClassLoader().getResource("Arm.fxml"));
//            root.getStylesheets().add("UI/style.css");
//            Stage armStage = new Stage();
//            armStage.setTitle("Arm!");
//            armStage.setScene(new Scene(root, 500, 500));
//            armStage.setResizable(false);
//            armStage.show();
        }
        catch (IOException a) {
        }
    }
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        // TODO
    }    
    
}
