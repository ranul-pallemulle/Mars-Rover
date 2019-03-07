/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package javafxapplication1;

/**
 *
 * @author Matthew Shen
 */

import javafxapplication1.SendDataToRover;
        
public class TestMain {
        public static void main(String[] args){
            
            double sendingnum = 0.122;
            
            SendDataToRover sender = new SendDataToRover("146.169.135.193", 5560);
            try{
            sender.initialise();
        
            } catch (Exception e){
                System.out.println("error");
            } 
            
            sender.sendData(sendingnum);
            sender.sendData(sendingnum+0.1);
            //System.out.println(sender.isInitialised());
            sendingnum+=0.001;
            
            try{
                //sender.close();
            }  catch (Exception e){
                System.out.println("error");   
            }
            
        }
}
