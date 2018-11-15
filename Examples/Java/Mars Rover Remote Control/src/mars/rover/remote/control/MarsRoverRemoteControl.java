/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package mars.rover.remote.control;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;
/**
 *
 * @author Ranul Pallemulle
 */
public class MarsRoverRemoteControl extends Application {
    
    @Override
    public void start(Stage primaryStage) throws Exception {
        final FXMLLoader loader = new FXMLLoader(getClass().getResource("MainView.fxml"));
        final Parent root = (Parent) loader.load();
        final MainViewController controller = loader.<MainViewController>getController();
        controller.setStage(primaryStage);
        
        root.getStylesheets().add("style.css");
        
        Scene scene = new Scene(root,300,275);
        primaryStage.setTitle("ICSEDS Mars Rover Controller");
        primaryStage.setScene(scene);
        
        primaryStage.show();
    }

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        launch(args);
    }
    
}
