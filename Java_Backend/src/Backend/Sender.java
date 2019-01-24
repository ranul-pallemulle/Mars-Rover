/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package Backend;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author Matthew Shen
 */
public class Sender {
    Socket ClientSock;
    BufferedReader input;
    DataOutputStream output;
    String IP;
    int port;
    boolean SuccessInit;
    
    public Sender(String _IP, int _port){
        this.IP = _IP;
        this.port = _port;
        this.SuccessInit=false;
    }
    
    public void initialise() throws UnknownHostException, IOException{//throws delcares exceptions, tried the clause and then catches
        ClientSock = new Socket(IP,port);
        input = new BufferedReader(new InputStreamReader(ClientSock.getInputStream()));
        output = new DataOutputStream(ClientSock.getOutputStream());
        SuccessInit = true;
    }
    
    public void close() throws IOException{
        output.write("KILL\n".getBytes());
        output.close();
        input.close();
        ClientSock.close();
        SuccessInit = false;
    }
    
    public void sendData(double trynum){ //used as a test send
        try{
            String sendingstr = Double.toString(trynum);
            byte[] sendingByte= sendingstr.getBytes();
            if(SuccessInit){
                output.write(sendingByte);
                System.out.println("Sent");
                String response;
                if((response = input.readLine())!=null) {                
                    System.out.println(response);
                    System.out.println(this.IP);
                }
            }
        }
        catch(IOException ex){
            Logger.getLogger(Sender.class.getName()).log(Level.SEVERE, null, ex);   
        }
    }
    
    public void sendData(double x_vel, double y_vel){  //used to send controls to motor speeds
        try{
            String sendingstr = Double.toString(x_vel) + "," + Double.toString(y_vel);
            byte[] sendingByte= sendingstr.getBytes();
            if(SuccessInit){
                output.write(sendingByte);
                System.out.println("Sent");
                String response;
                if((response = input.readLine())!=null) {
                    System.out.println(response);
                    System.out.println(this.IP);
                }
            }
        }
        catch(IOException ex){
            Logger.getLogger(Sender.class.getName()).log(Level.SEVERE, null, ex);   
        }
    }
    
    public void sendData(double base_angle, double joint_angle, double arm_angle){  //used to send controls to motor speeds
        try{
            String sendingstr = Double.toString(base_angle) + "," + Double.toString(joint_angle) + "," + Double.toString(arm_angle);
            byte[] sendingByte= sendingstr.getBytes();
            if(SuccessInit){
                output.write(sendingByte);
                System.out.println("Sent");
                String response;
                if((response = input.readLine())!=null) {
                    System.out.println(response);
                    System.out.println(this.IP);
                }
            }
        }
        catch(IOException ex){
            Logger.getLogger(Sender.class.getName()).log(Level.SEVERE, null, ex);   
        }
    }
    
    public void startPiApp(String Application, int port_num){
        try{
            String sendingstr = "START_" + String.Application + " " + Integer.toString(port_num);
            byte[] sendingByte= sendingstr.getBytes();
            if(SuccessInit){
                output.write(sendingByte);
                System.out.println("Sent");
                String response;
                if((response = input.readLine())!=null) {
                    System.out.println(response);
                    System.out.println(this.IP);
                }
            }
            
        }
        catch(IOException ex){
            Logger.getLogger(SendDataToRover.class.getName()).log(Level.SEVERE, null, ex);   
        }
    }
    
    
    public boolean isInitialised(){
        return SuccessInit;
    }
    
    
}
