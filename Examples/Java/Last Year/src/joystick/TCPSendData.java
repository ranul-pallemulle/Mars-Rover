/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package joystick;

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
 * @author ranulpallemulle
 */
public class TCPSendData { 
    Socket ClientSock; //Socket object
    BufferedReader input; //input stream (buffered reader works here)
    DataOutputStream output; //output stream
    String ip;
    int port;
    boolean successInit=false;
    
    public TCPSendData(String _ip,int _port) {
        this.ip=_ip;
        this.port=_port;
    }
    public void initialise() throws UnknownHostException, IOException{ //taking socket and breaking down its input and output into useful obejcts
        ClientSock = new Socket(ip,port); //choose port as 5560 to match raspi
        input = new BufferedReader(new InputStreamReader(ClientSock.getInputStream())); //bufferedreader takes inputstreamreader, which needs a inputstream of a socket
        output= new DataOutputStream(ClientSock.getOutputStream()); //same for output
        successInit=true;
    }
    public void close() throws IOException { //runs to close the program
        output.write("KILL".getBytes());
        output.close(); //close outputstream
        input.close(); //close inputstream
        ClientSock.close(); //close socket
        successInit=false;
    }
    public void sendData(double data1,double data2) {//why not use throws here?
        //sends the string and if there is a response, writes it to command line
        try {       
            //Double[] arr = new Double[2];
            //arr[0]=data1;
            //arr[1]=data2;
            String str=Double.toString(data1)+","+Double.toString(data2); //encoding data
            //System.out.println(str);
            byte[] strbytes=str.getBytes(); //convert into byte strings (in hexadecimal)
            if (successInit){
                output.write(strbytes); //sending data
                String response;
                if((response = input.readLine())!=null) { //checking is a response is received
                    //System.out.println(response);
                }
            }
            //this.close(); //close after every transfer
        } catch (IOException ex) {
                Logger.getLogger(TCPSendData.class.getName()).log(Level.SEVERE, null, ex);
        }
        
    }
    public void sendAll(double xval, double yval, int bogieval, double scoopval){ //same as senddata
        //Double[] arr = new Double[4];
        //arr[0] = xval;
        //arr[1] = yval;
        //arr[3] = (double) bogieval;
        //arr[4] = scoopval;
        try{
            String str = Double.toString(xval)+","+Double.toString(yval)+","
                        +Integer.toString(bogieval)+","+Double.toString(scoopval);
            
            byte[] strbytes = str.getBytes();
            
            if(successInit){
                output.write(strbytes);
                String response;
                if((response = input.readLine())!=null) {
                    //System.out.println(response);
                }
            }
            
        } catch(IOException ex){
                Logger.getLogger(TCPSendData.class.getName()).log(Level.SEVERE, null, ex);
        }
        
        
    }
    
    
    public boolean isInitialised(){
        return successInit;
    }
}
