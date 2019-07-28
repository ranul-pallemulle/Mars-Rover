/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package Backend;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;
import javafx.animation.AnimationTimer;
import javafx.event.EventHandler;
import javafx.scene.Scene;
import javafx.scene.input.KeyEvent;

/**
 *
 * @author ranul
 */
public class KeyboardDriveController extends AnimationTimer {
    private Scene scene;
    private ArrayList<Integer> values;
    private EventHandler<KeyEvent> pressHandler;
    private EventHandler<KeyEvent> releaseHandler;
    private Consumer<ArrayList<Integer>> user;
    
    public KeyboardDriveController (Scene _scene, Consumer<ArrayList<Integer>> _user) {
        scene = _scene;
        user = _user;
        values = new ArrayList<>(2);
        values.add(0);
        values.add(0);
        
        pressHandler = new EventHandler <KeyEvent>() {
            @Override
            public void handle (KeyEvent event) {
                System.out.println("GOT PRESS EVENT");
                switch (event.getCode()) {
                    case W: values.set(0, 1); break;
                    case A: values.set(1, 1); break;
                    case S: values.set(0, 1); break;
                    case D: values.set(1, 1); break;
                }
            }
        };
        
        releaseHandler = new EventHandler <KeyEvent>() {
            @Override
            public void handle (KeyEvent event) {
                System.out.println("GOT RELEASED EVENT");
                switch (event.getCode()) {
                    case W: values.set(0, 0); break;
                    case A: values.set(1, 0); break;
                    case S: values.set(0, 0); break;
                    case D: values.set(1, 0); break;
                }
            }
        };
        
        scene.setOnKeyPressed(pressHandler);
        scene.setOnKeyReleased(releaseHandler);
    }

    @Override
    public void handle(long now) {
        user.accept(values);
    }
    
    
    
}

// Usage

//kbdConsumer = new Consumer<ArrayList<Integer>>() {
//@Override
//public void accept(ArrayList<Integer> t) {
//        // get distance between click and drag
//        double drag_delx = t.get(1);// - joyBackCircle.getCenterX();
//        double drag_dely = t.get(0);// - joyBackCircle.getCenterY();
//
//        // get new position of joystick
//        double joy_newx = joyBackCircle.getCenterX() + drag_delx;
//        double joy_newy = joyBackCircle.getCenterY() + drag_dely;
//
//        // calculate radial displacement
//        double rad2 = joy_newx * joy_newx +
//                     joy_newy * joy_newy;
//        double maxrad = joyBackCircle.getRadius() - joyFrontCircle.getRadius();
//        if (rad2 < maxrad * maxrad) {
//            joyFrontCircle.setCenterX(joy_newx);
//            joyFrontCircle.setCenterY(joy_newy);
//        }
//        else {
//            double angle = atan2(joy_newy,joy_newx);
//            joy_newx = joyBackCircle.getCenterX() + maxrad * cos(angle);
//            joy_newy = joyBackCircle.getCenterY() + maxrad * sin(angle);
//            joyFrontCircle.setCenterX(joy_newx);
//            joyFrontCircle.setCenterY(joy_newy);
//
//        }
//
//        dispJoyX.setText(String.format("%.1f",joy_newx));
//        dispJoyY.setText(String.format("%.1f",-joy_newy));
//            }
//        };
//runAfterInitList.add(new Runnable() {
//    @Override
//    public void run() {
//        kbdController = new KeyboardDriveController(primaryStage.getScene(),kbdConsumer);
//        //kbdController.start();
//    }
//});