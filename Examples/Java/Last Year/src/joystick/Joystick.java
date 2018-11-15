/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package joystick;


import java.util.List;
import javafx.application.Application;
import javafx.event.EventHandler;
import javafx.geometry.Pos;
import javafx.scene.input.MouseEvent;
import javafx.stage.WindowEvent;
import javafx.application.Platform;
import javafx.beans.value.ChangeListener;
import javafx.beans.value.ObservableValue;
import javafx.event.ActionEvent;
import javafx.geometry.Orientation;
import javafx.stage.Stage;
import javafx.scene.Group;
import javafx.scene.Scene;
import javafx.scene.control.Alert;
import javafx.scene.control.Alert.AlertType;
import javafx.scene.control.Button;
import javafx.scene.control.Slider;
import javafx.scene.text.Font;
import javafx.scene.text.Text;
import javafx.scene.shape.Circle;
import javafx.scene.paint.Color;
import javafx.scene.control.Label;
import javafx.scene.control.RadioButton;
import javafx.scene.control.Separator;
import javafx.scene.control.ToggleButton;
import javafx.scene.control.ToggleGroup;


/**
 *
 * @author ranulpallemulle
 */
public class Joystick extends Application {
    
    Circle stickcircle, limitcircle, indiccircle, conncircle;
    ValueSender comms;
    InputDataProcessor serialin;
    double orgscenex, orgsceney;
    double newtranslatex,newtranslatey;
    double orgtranslatex,orgtranslatey;
    boolean virtualenabled=true;
    boolean roverconnectionmade=false;
    
    public static void main(String[] args) {
        launch(args);
    }
    
    
    @Override
    public void start(Stage primaryStage) throws Exception {
        
        /* USE CONCENTRIC CIRCLES AS JOYSTICK */
        limitcircle=new Circle(120.0f);
        limitcircle.setCenterX(200);
        limitcircle.setCenterY(200);
        
        comms = new ValueSender(limitcircle.getRadius(),new TCPSendData("192.168.4.1",5560)); //192.168.4.1 , 172.24.1.1 or 169.254.108.151
        serialin = new InputDataProcessor(new SerialGetData());
        
        stickcircle=new Circle(50.0f,Color.RED);
        stickcircle.setCenterX(200);
        stickcircle.setCenterY(200);
        stickcircle.setOnMousePressed(circleOnMousePressedEventHandler);
        stickcircle.setOnMouseDragged(circleOnMouseDraggedEventHandler);
        stickcircle.setOnMouseReleased(circleOnMouseReleasedEventHandler);
        
        indiccircle=new Circle(10.0f,Color.BLACK);
        indiccircle.setCenterX(350);
        indiccircle.setCenterY(350);
        
        conncircle=new Circle(7.0f,Color.BLACK);
        conncircle.setCenterX(120);
        conncircle.setCenterY(363);
        
        Label heading = new Label("ICSEDS LUNAR ROVER CONTROLLER");
        //heading.setAlignment(Pos.CENTER);
        heading.setLayoutX(50);
        heading.setFont(Font.font("Calibri",22));
        Separator separator = new Separator();
        separator.setOrientation(Orientation.VERTICAL);
        separator.setMaxWidth(40);
        separator.setLayoutY(30);
        
        /* SELECTION BUTTONS TO SELECT VIRTUAL/ARDUINO JOYSTICK */
        ToggleGroup toggroup = new ToggleGroup();
        RadioButton realoff = new RadioButton("Enable virtual joystick");
        realoff.setOnAction(realoffSelectedHandler);
        realoff.setLayoutX(135); realoff.setLayoutY(55);
        RadioButton realon = new RadioButton("Enable Arduino joystick");
        realon.setOnAction(realonSelectedHandler);
        realon.setLayoutX(135); realon.setLayoutY(30);
        toggroup.getToggles().addAll(realoff,realon);
        realoff.fire();
        
        /* SLIDER FOR SCOOP */
        Slider slider = new Slider(-1,1,0); //max=1,min=-1,default=0
        slider.setOrientation(Orientation.VERTICAL);
        slider.setLayoutX(375);
        slider.setLayoutY(135);
        slider.setDisable(!roverconnectionmade);
        slider.valueProperty().addListener(new ChangeListener(){
           @Override
           public void changed(ObservableValue arg0, Object arg1, Object arg2){
               double val2setscoop = slider.getValue();
               comms.setScoopVal(val2setscoop);
           }
        });
        Label armLbl = new Label("Set Scoop Speed");
        armLbl.setLayoutX(335);
        armLbl.setLayoutY(110);
        ToggleButton scpreset = new ToggleButton("Reset Scoop");
        scpreset.setOnAction(new EventHandler<ActionEvent>(){
            @Override
            public void handle(ActionEvent e){
                if (scpreset.isSelected()){
                    slider.setValue(0);
                    scpreset.setSelected(false);
                }
            }
        });
        scpreset.setLayoutX(340);
        scpreset.setLayoutY(280);
        scpreset.setDisable(!roverconnectionmade);
        
        /* Bogie setting*/
        Button bogierise = new Button("Rise");
        bogierise.setOnMousePressed((event)-> {
            comms.setBogieVal(1);
        });
        bogierise.setOnMouseReleased((event)->{
            comms.setBogieVal(0);
        });
        bogierise.setLayoutX(340);
        bogierise.setLayoutY(65);
        bogierise.setDisable(!roverconnectionmade);
        
        Button bogiefall = new Button("Drop");
        bogiefall.setOnMousePressed((event)->{
           comms.setBogieVal(2);
        });
        bogiefall.setOnMouseReleased((event)->{
           comms.setBogieVal(0); 
        });
        bogiefall.setLayoutX(390);
        bogiefall.setLayoutY(65);
        bogiefall.setDisable(!roverconnectionmade);
        Label bogielbl = new Label("Set Height");
        bogielbl.setLayoutX(355);
        bogielbl.setLayoutY(40);
        
        /* reset button */
        
        Button resetMCU = new Button ("Reset MCU");
        resetMCU.setOnMousePressed((event)->{
            comms.setMCUreset(1);            
        });
        resetMCU.setOnMouseReleased((event)->{
            comms.setMCUreset(0);
        });
        resetMCU.setLayoutX(20);
        resetMCU.setLayoutY(50);
        resetMCU.setDisable(!roverconnectionmade);
        /* BUTTON TO MAKE CONNECTION TO PI */
        ToggleButton togbutt = new ToggleButton("Connect to Rover");
        togbutt.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent e){
                if (togbutt.isSelected()){
                    try{
                        comms.beginTCP();
                        
                    } catch (Exception ex){
                        togbutt.setSelected(false);
                        Alert alert = new Alert(AlertType.INFORMATION);
                        alert.setTitle("Unable to Connect");
                        alert.setHeaderText(null);
                        alert.setContentText("Select joystick mode on rover first");
                        alert.showAndWait();
                    }
                    if (comms.tcpConnValid()){
                        roverconnectionmade=true;
                        (new Thread(comms)).start(); //do comms.run() starts in a new thread
                        conncircle.setFill(Color.GREEN);
                    }
                }
                else{
                    try {
                        comms.close();
                    } catch (Exception ex){
                        togbutt.setSelected(true);
                        Alert alert = new Alert(AlertType.INFORMATION);
                        alert.setTitle("Unable to Close");
                        alert.setHeaderText(null);
                        alert.setContentText("Unable to close connection at the moment");
                        alert.showAndWait();
                    }
                    if (!comms.tcpConnValid()){
                        roverconnectionmade=false;
                        conncircle.setFill(Color.BLACK);
                        slider.setValue(0); // reset
                    }
                }
                slider.setDisable(!roverconnectionmade);
                scpreset.setDisable(!roverconnectionmade);
                bogierise.setDisable(!roverconnectionmade);
                bogiefall.setDisable(!roverconnectionmade);
                resetMCU.setDisable(!roverconnectionmade);
            }
        });
        togbutt.setLayoutX(145);
        togbutt.setLayoutY(350);
        
        Text alertlab = new Text(335,330,"Alert");
        
       
        /* Add everything to GUI */
        Group root = new Group();
        root.getChildren().addAll(limitcircle,stickcircle,indiccircle,conncircle,heading,alertlab,realoff,realon,togbutt,slider,armLbl,scpreset,bogierise,bogiefall,bogielbl);
        root.getChildren().add(separator);
        primaryStage.setResizable(false);
        primaryStage.setScene(new Scene(root,450,400));
        
        primaryStage.setTitle("Joystick");
        primaryStage.setOnCloseRequest(new EventHandler<WindowEvent>() {
            @Override
            public void handle(WindowEvent t) {
                if(roverconnectionmade){
                    comms.close();
                }
                Platform.exit();
                System.exit(0);
            }
        });
        primaryStage.show();
        
    }
    
    EventHandler<ActionEvent> realoffSelectedHandler =
            new EventHandler<ActionEvent>() {
                @Override
                public void handle (ActionEvent t) {
                    virtualenabled=true;
                    //System.out.println("Virtual enabled");
                    serialin.stopSerial();
                }
            };
    EventHandler<ActionEvent> realonSelectedHandler = 
            new EventHandler<ActionEvent>() {
                @Override
                public void handle (ActionEvent t) {
                    virtualenabled=false;
                    //System.out.println("Virtual not enabled");
                    serialin.beginSerial();
                    useRealInputs();
                }
            };
    private void useRealInputs() {
        Thread refreshScreen = new Thread(){
                @Override
                public void run(){
                    while(!virtualenabled){
                        List<Double> resultArray=serialin.giveResult();
                        double sw = resultArray.get(0);
                        double joyx=resultArray.get(1);
                        double joyy=resultArray.get(2);
                        double limrad=limitcircle.getRadius();
                        //System.out.print("TO SET:");System.out.print(joyx);System.out.print(",");System.out.println(joyy);
                        double tosetx=((joyx-127)/127)*limrad;
                        double tosety=((joyy-127)/127)*limrad;
                        if (Math.abs(tosetx)<3){ //can do this on arduino 
                            tosetx=0;
                        }
                        if (Math.abs(tosety)<3){
                            tosety=0;
                        }
                        stickcircle.setTranslateX(tosetx);
                        stickcircle.setTranslateY(tosety);
                        comms.setSpeedVals(tosetx, -tosety);
                        try{
                            Thread.sleep(80);
                            
                        }
                        catch (InterruptedException e){
                            System.out.println("refreshScreen thread was interrupted");
                        }
                    }
                }
                    
            };
            refreshScreen.start();
    }
   
    EventHandler<MouseEvent> circleOnMousePressedEventHandler =
            new EventHandler<MouseEvent>() {
                @Override
                public void handle (MouseEvent t) {
                    if(virtualenabled && roverconnectionmade){
                        orgscenex=t.getSceneX(); //orgscenex and orgsceney record the coordinates where the user clicks the mouse (usually 200,200) when selecting the circle
                        orgsceney=t.getSceneY();
                        //System.out.print(orgscenex);
                        //System.out.println(" , ");
                        //System.out.println(orgsceney);
                    }
                }
            };
    EventHandler<MouseEvent> circleOnMouseDraggedEventHandler =
            new EventHandler<MouseEvent>() {
                @Override
                public void handle (MouseEvent t) {
                    if(virtualenabled && roverconnectionmade){
                        //newtranslate are coordinates of mouse relative to clicked position
                        newtranslatex = t.getSceneX() - orgscenex; //t.getSceneX() gets the x coordinate of the point where the mouse has been dragged to. 
                        newtranslatey = t.getSceneY() - orgsceney;
                        //System.out.print(t.getSceneX());
                        //System.out.print(" , ");
                        //System.out.println(t.getSceneY());
                        

                        double rad = Math.sqrt((newtranslatex*newtranslatex)+(newtranslatey*newtranslatey));
                        if(rad<limitcircle.getRadius()) { 
                            // t.getSource() gets the object that was dragged
                            ((Circle)(t.getSource())).setTranslateX(newtranslatex);
                            ((Circle)(t.getSource())).setTranslateY(newtranslatey);
                            //System.out.println("x "+newtranslatex);
                            //System.out.println("y "+(-newtranslatey));
                        }
                   
                        else{
                            /* Radius of movement is outside the limit. Use maximum radius and angle to position the circle */
                            double theta;
                            if((-newtranslatey)>=0 && newtranslatex>=0){
                                theta = Math.atan(-newtranslatey/newtranslatex);
                            }
                            else if ((-newtranslatey)<0 && newtranslatex>=0){
                                theta = Math.atan(-newtranslatey/newtranslatex);
                            }
                            else if ((-newtranslatey)>=0 && newtranslatex<0){
                                theta = 3.14159265358979/2 + Math.atan(-newtranslatex/-newtranslatey);
                            }
                            else{ //both <0
                                theta = -3.14159265358979/2 - Math.atan(-newtranslatex/newtranslatey);
                            }
                            //System.out.println("theta : "+theta*180/3.14159);
                            double circtransx = limitcircle.getRadius()*Math.cos(theta);
                            double circtransy = -limitcircle.getRadius()*Math.sin(theta);
                            ((Circle)(t.getSource())).setTranslateX(circtransx);
                            ((Circle)(t.getSource())).setTranslateY(circtransy);
                   
                        }
                        
                        orgtranslatex = ((Circle)(t.getSource())).getTranslateX(); //orgtranslatex and y record the displacement of the circle relative to the initial position (200,200) of the circle
                        orgtranslatey = ((Circle)(t.getSource())).getTranslateY();
                        
                        comms.setSpeedVals(orgtranslatex, -orgtranslatey);
                        if (comms.isWrong()){
                            indiccircle.setFill(Color.RED );
                        }
                        else {
                        indiccircle.setFill(Color.BLACK);
                        }
                    }
                }
            };
    EventHandler<MouseEvent> circleOnMouseReleasedEventHandler =
            new EventHandler<MouseEvent>() {
                @Override
                public void handle (MouseEvent t) {
                    if(virtualenabled && roverconnectionmade){
                        ((Circle)(t.getSource())).setTranslateX(0);
                        ((Circle)(t.getSource())).setTranslateY(0);
                        
                        orgtranslatex = ((Circle)(t.getSource())).getTranslateX(); //orgtranslatex and y record the displacement of the circle relative to the initial position (200,200) of the circle
                        orgtranslatey = ((Circle)(t.getSource())).getTranslateY();
                        
                        comms.setSpeedVals(orgtranslatex, -orgtranslatey);
                    }
                    
                }
            };
    

}