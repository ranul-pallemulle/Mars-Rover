/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package UI;

import javafx.application.Application;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;
import Backend.*;
import javafx.application.Platform;
import javafx.geometry.Rectangle2D;
import javafx.stage.Screen;
import org.freedesktop.gstreamer.Gst;

/**
 *
 * @author JustinLiu
 */
public class Main extends Application {
    
    @Override
    public void start(Stage primaryStage) throws Exception{
        final FXMLLoader loader = new FXMLLoader(getClass().getResource("FXML.fxml"));
        final Parent root = (Parent) loader.load();
        final FXMLController controller = loader.<FXMLController>getController();
        controller.setStage(primaryStage);
        root.getStylesheets().add("UI/style.css");
        //root.getChildren().add(btn);
        
        Scene scene = new Scene(root, 500, 600);
        
        primaryStage.setTitle("Rover");
        primaryStage.setScene(scene);
        primaryStage.setResizable(false);
        
        Rectangle2D primaryScreenBounds = Screen.getPrimary().getVisualBounds();
        primaryStage.setX(primaryScreenBounds.getMinX() + primaryScreenBounds.getWidth()/2 - 500);
        primaryStage.setY(primaryScreenBounds.getMinY() + primaryScreenBounds.getHeight()/2 - 250);
        
        primaryStage.setOnCloseRequest(e->handleExit(controller));
        
        primaryStage.show();
    }
    
    private void handleExit(FXMLController controller)
    {
        controller.clean_up();
        Platform.exit();
        System.exit(0);
    }

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        Gst.init("GUI", args);
        launch(args);
    }
    
}
