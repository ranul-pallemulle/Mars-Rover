/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package Backend;

import java.util.function.Consumer;

/**
 *
 * @author ranul
 */
public class DepCameraController {
    private double angle_top;

    
    private double angle_middle;
    private double angle_bottom;
    
    private Connection connection;
    
    public DepCameraController() {
        angle_top = 0.0;
        angle_middle = 0.0;
        angle_bottom = 0.0;
    }
    
    public void initialiseConnection(Consumer<Exception> e) {
        connection = new Connection(e);
    }
    
    public Connection getConnection() {
        return connection;
    }
    
    public void moveTop(double value) {
        angle_top = value;
        if (connection.isActive()) {
            String data = String.format("%d,%d,%d", (int)angle_top,
                                        -(int)angle_middle,-(int)angle_bottom);
            boolean res = connection.send(data);
//            System.out.println(res);
        }
    }
    
    public void moveMiddle(double value) {
        angle_middle = value;
        if (connection.isActive()) {
            String data = String.format("%d,%d,%d", (int)angle_top,
                                        -(int)angle_middle,-(int)angle_bottom);
            connection.send(data);
        }
    }
    
    public void moveBottom(double value) {
        angle_bottom = value;
        if (connection.isActive()) {
            String data = String.format("%d,%d,%d", (int)angle_top,
                                        -(int)angle_middle,-(int)angle_bottom);
            connection.send(data);
        }
    }
    
    public double getTopAngle() {
        return angle_top;
    }

    public double getMiddleAngle() {
        return angle_middle;
    }

    public double getBottomAngle() {
        return angle_bottom;
    }
    
    public void increaseTopAngle() {
        angle_top += 5;
        // System.out.println(angle_top);
        if (connection.isActive()) {
            String data = String.format("%d,%d,%d", (int)angle_top, 
                                        (int)angle_middle, (int)angle_bottom);
            connection.send(data);
        }
    }
    
    public void decreaseTopAngle() {
        angle_top -= 5;
        // System.out.println(angle_top);
        if (connection.isActive()) {
            String data = String.format("%d,%d,%d", (int)angle_top, 
                                        (int)angle_middle, (int)angle_bottom);
            connection.send(data);
        }
    }
    
    public void increaseMiddleAngle() {
        angle_middle += 5;
        // System.out.println(angle_middle);
        if (connection.isActive()) {
            String data = String.format("%d,%d,%d", (int)angle_top, 
                                        (int)angle_middle, (int)angle_bottom);
            connection.send(data);
        }
    }
    
    public void decreaseMiddleAngle() {
        angle_middle -= 5;
        // System.out.println(angle_middle);
        if (connection.isActive()) {
            String data = String.format("%d,%d,%d", (int)angle_top, 
                                        (int)angle_middle, (int)angle_bottom);
            connection.send(data);
        }
    }
    
    public void increaseBottomAngle() {
        angle_bottom += 5;
        // System.out.println(angle_bottom);
        if (connection.isActive()) {
            String data = String.format("%d,%d,%d", (int)angle_top, 
                                        (int)angle_middle, (int)angle_bottom);
            connection.send(data);
        }
    }
    
    public void decreaseBottomAngle() {
        angle_bottom -= 5;
        // System.out.println(angle_bottom);
        if (connection.isActive()) {
            String data = String.format("%d,%d,%d", (int)angle_top, 
                                        (int)angle_middle, (int)angle_bottom);
            connection.send(data);
        }
    }
}
