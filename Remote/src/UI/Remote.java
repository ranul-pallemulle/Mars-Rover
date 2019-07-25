/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package UI;

import javafx.application.Application;
import javafx.application.Platform;
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
    
    private static Stage stage; // main stage
    private static Stage depCamStage; // stage for deployable camera
    
    public static void main(String[] args) {
        Gst.init("Remote",args);
        launch(args);
    }
    
    public static Stage getStage() {
        return stage;
    }
    
    public static Stage getDepCamStage() {
        return depCamStage;
    }

    @Override
    public void start(Stage primaryStage) throws Exception {
        // initialise main stage
        stage = primaryStage;
        final FXMLLoader loader = new FXMLLoader(getClass().getResource("MainFxml.fxml"));
        final Parent root = (Parent) loader.load();
        final MainFxmlController controller = loader.<MainFxmlController>getController();   
        
        Scene scene = new Scene(root);
        stage.setTitle("ICSS Rover");
        stage.setScene(scene);
        stage.setResizable(true);
        
        stage.setOnCloseRequest(e->handleExit(controller));
        
        stage.setFullScreen(true);
        stage.setOnShown((e) -> {
            controller.runAfterInit();
        });
        
        // initialise deployable camera stage
        depCamStage = new Stage();
        final FXMLLoader depcam_loader = new FXMLLoader(getClass().getResource("DepCamFxml.fxml"));
        final Parent depcam_root = (Parent) depcam_loader.load();
        final DepCamFxmlController depcam_controller = depcam_loader.<DepCamFxmlController>getController();
        
        Scene depcam_scene = new Scene(depcam_root);
        depCamStage.setTitle("Deployable Camera");
        depCamStage.setScene(depcam_scene);
        depCamStage.setResizable(true);
        depCamStage.setFullScreen(true);
        
        depCamStage.setOnShowing((e) -> { // opening
            controller.onDepCamStageShowing();
            depcam_controller.onStageShowing();
        });
        
        
        depCamStage.setOnHiding((e) -> { // closing
            controller.onDepCamStageHiding();
            depcam_controller.onStageHiding();
        });
        
        // show main stage
        stage.show();
    }
    
    public void handleExit(MainFxmlController controller) {
        if (controller.getConnection().isActive()) {
            // controller.getConnection().close();
        }
        Platform.exit();
        System.exit(0);
    }
    
}
