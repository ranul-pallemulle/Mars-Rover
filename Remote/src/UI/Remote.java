/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package UI;

import javafx.application.Application;
import javafx.event.EventHandler;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;
import javafx.stage.WindowEvent;
import org.freedesktop.gstreamer.Gst;

/**
 *
 * @author Ranul Pallemulle
 */
public class Remote extends Application{
    
    public static void main(String[] args) {
        Gst.init("Remote",args);
        launch(args);
    }

    @Override
    public void start(Stage primaryStage) throws Exception {
        final FXMLLoader loader = new FXMLLoader(getClass().getResource("MainFxml.fxml"));
        final Parent root = (Parent) loader.load();
        final MainFxmlController controller = loader.<MainFxmlController>getController();   
        
        Scene scene = new Scene(root);
        primaryStage.setTitle("ICSS Rover");
        primaryStage.setScene(scene);
        primaryStage.setResizable(true);
        controller.setCurrentStage(primaryStage);
        
        // primaryStage.setOnCloseRequest(e->handleExit(controller));
        
        // primaryStage.setFullScreen(true);
        primaryStage.setOnShown(new EventHandler<WindowEvent>() {
            @Override
            public void handle(WindowEvent event) {
                controller.runAfterInit();
            }
            
        });
        primaryStage.show();
    }
    
}
