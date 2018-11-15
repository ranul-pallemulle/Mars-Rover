/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package mars.rover.remote.control;

import java.net.URL;
import java.util.ResourceBundle;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.Button;
import javafx.stage.Stage;

/**
 *
 * @author Ranul Pallemulle
 */
public class MainViewController implements Initializable {
    
    private Stage stage;
    @FXML private Button connectButton;
        
    public void setStage(Stage stage)
    {
        this.stage = stage;
    }
    
    @FXML
    public void handleConnectButtonPress(ActionEvent e) {
        System.out.println("Hello");
    }
    
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        // TODO
    }    
    
}
