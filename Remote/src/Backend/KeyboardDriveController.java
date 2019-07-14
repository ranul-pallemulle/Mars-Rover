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
