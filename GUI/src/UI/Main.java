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
import javafx.scene.control.Button;
import javafx.scene.layout.StackPane;
import javafx.stage.Stage;
import Backend.*;

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
        
        Scene scene = new Scene(root, 500, 500);
        
        primaryStage.setTitle("Rover");
        primaryStage.setScene(scene);
        primaryStage.setResizable(false);
        primaryStage.show();
    }

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        launch(args);
    }
    
}
