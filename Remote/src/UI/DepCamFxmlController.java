/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package UI;

import Backend.DepCameraController;
import Backend.IPAddressManager;
import java.awt.Dimension;
import java.io.IOException;
import java.net.URL;
import java.util.ResourceBundle;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import java.util.logging.Level;
import java.util.logging.Logger;
import javafx.application.Platform;
import javafx.embed.swing.SwingNode;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.Button;
import javax.swing.SwingUtilities;
import org.freedesktop.gstreamer.Bin;
import org.freedesktop.gstreamer.Gst;
import org.freedesktop.gstreamer.Pipeline;

/**
 * FXML Controller class
 *
 * @author ranul
 */
public class DepCamFxmlController implements Initializable {
    
    @FXML private Button topIncreaseButton;
    @FXML private Button topDecreaseButton;
    @FXML private Button middleIncreaseButton;
    @FXML private Button middleDecreaseButton;
    @FXML private Button bottomIncreaseButton;
    @FXML private Button bottomDecreaseButton;
    @FXML private SwingNode videoScreen;
    
    private DepCameraController depCameraController;
    Pipeline pipe;

    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        createEmptyVideoScreen(videoScreen);
        
        depCameraController = new DepCameraController();
        depCameraController.initialiseConnection((Consumer<Exception>)(e)->{
            Platform.runLater(()->{
                // TODO
            });
        });
    }
    
    public void topIncreaseButtonPressed() {
        depCameraController.increaseTopAngle();
    }
    
    public void topDecreaseButtonPressed() {
        depCameraController.decreaseTopAngle();
    }
    
    public void middleIncreaseButtonPressed() {
        depCameraController.increaseMiddleAngle();
    }
    
    public void middleDecreaseButtonPressed() {
        depCameraController.decreaseMiddleAngle();
    }
    
    public void bottomIncreaseButtonPressed() {
        depCameraController.increaseBottomAngle();
    }
    
    public void bottomDecreaseButtonPressed() {
        depCameraController.decreaseBottomAngle();
    }
    
    
    
    /// public methods
    
    /**
     * This method is run when the stage controlled by this controller is showing.
     */
    public void onStageShowing() {
        try {
            // System.out.println("SHOWING");
            depCameraController.getConnection().open(IPAddressManager.getCurrentIP(), 5581, 10, true);
            TimeUnit.SECONDS.sleep(5);
            startVideo(videoScreen);
        } catch (IOException ex) {
            depCameraController.getConnection().close();
            Remote.getDepCamStage().close();
        } catch (InterruptedException ex) {
            Logger.getLogger(DepCamFxmlController.class.getName()).log(Level.SEVERE, null, ex);
        }
    }
    
    /**
     * This method is run when the stage controlled by this controller is closing.
     */
    public void onStageHiding() {
        // System.out.println("CLOSING");
        if (pipe != null) {
            pipe.dispose();
        }
    }
    
    
    /// private methods
    
    private void createEmptyVideoScreen(final SwingNode swingNode) {
        SimpleVideoComponent vc = new SimpleVideoComponent();
        SwingUtilities.invokeLater(()->{
            swingNode.setContent(vc);
        });
        vc.setKeepAspect(true);
    }
    
    private void startVideo(final SwingNode swingNode) {
        pipe = new Pipeline();
        String ip = IPAddressManager.getCurrentIP();
        if (ip == null) {
            return;
        }
        String gst_str = "tcpclientsrc host="+ip+" port=5520 ! gdpdepay ! "
                + "rtph264depay ! avdec_h264 ! videoconvert";
        SimpleVideoComponent vc = new SimpleVideoComponent();
        vc.getElement().set("sync", false);
        Bin bin = Gst.parseBinFromDescription(gst_str, true);
        pipe.addMany(bin, vc.getElement());
        Pipeline.linkMany(bin,vc.getElement());
        SwingUtilities.invokeLater(() -> {
            swingNode.setContent(vc);
        });
        vc.setPreferredSize(new Dimension(640,400));
        vc.setKeepAspect(true);
        pipe.play();
        swingNode.setVisible(true);
    }
    
}
