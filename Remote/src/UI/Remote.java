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
    
    private static Stage stage;
    
    public static void main(String[] args) {
        Gst.init("Remote",args);
        launch(args);
    }
    
    public static Stage getStage() {
        return stage;
    }

    @Override
    public void start(Stage primaryStage) throws Exception {
        stage = primaryStage;
        final FXMLLoader loader = new FXMLLoader(getClass().getResource("MainFxml.fxml"));
        final Parent root = (Parent) loader.load();
        final MainFxmlController controller = loader.<MainFxmlController>getController();   
        
        Scene scene = new Scene(root);
        stage.setTitle("ICSS Rover");
        stage.setScene(scene);
        stage.setResizable(true);
        
        // stage.setOnCloseRequest(e->handleExit(controller));
        
        // stage.setFullScreen(true);
        stage.setOnShown(new EventHandler<WindowEvent>() {
            @Override
            public void handle(WindowEvent event) {
                controller.runAfterInit();
            }
        });
        
        stage.show();
    }
    
}
