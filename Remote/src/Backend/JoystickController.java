/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package Backend;

import static java.lang.Math.atan2;
import static java.lang.Math.cos;
import static java.lang.Math.sin;
import java.util.function.Consumer;

/**
 *
 * @author Ranul Pallemulle
 */
public class JoystickController {
    
    // current joystick position coordinates
    private double joy_x;
    private double joy_y;
    // coordinates of a mouse click to select the joystick
    private double click_x;
    private double click_y;
    // maximum radial displacement possible
    private double max_rad;
    
    private Connection connection;
    
    public JoystickController(double _max_rad) {
        joy_x = 0;
        joy_y = 0;
        max_rad = _max_rad;
        click_x = 0;
        click_y = 0;
    }
    
    public void initialiseConnection(Consumer<Exception> e) {
        connection = new Connection(e);
    }
    
    public void setMouseclickPosition(double x, double y) {
        click_x = x;
        click_y = y;
    }
    
    public void setMaxRadius(double r) {
        max_rad = r;
    }
    
    public void update(double x, double y) {
        // get resulting position of joystick
        double joy_newx = x - click_x;
        double joy_newy = y - click_y;
        
        // calculate radial displacement
        double rad2 = joy_newx * joy_newx +
                     joy_newy * joy_newy;
        
        if (rad2 > max_rad * max_rad) { // can't reach - follow angle only
            double angle = atan2(joy_newy,joy_newx);
            joy_newx = max_rad * cos(angle);
            joy_newy = max_rad * sin(angle);
        }
        
        // set to new position
        joy_x = joy_newx;
        joy_y = joy_newy;
            if (connection.isActive()) {
                String data = String.format("%d,%d", (int)joy_x, (int)joy_y);
                connection.send(data);
            }
    }
    
    public void returnToCenter() {
        joy_x = 0;
        joy_y = 0;
        if (connection.isActive()) {
            String data = String.format("%d,%d", (int)joy_x, (int)joy_y);
            connection.send(data);
        }
    }
    
    public double getX() {
        return joy_x;
    }
    
    public double getY() {
        return joy_y;
    }
    
    public Connection getConnection() {
        return connection;
    }
}
