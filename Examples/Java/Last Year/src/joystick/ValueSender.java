/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package joystick;
//import com.jcraft.jsch.ChannelSftp;

import java.io.IOException;


/**
 *
 * @author ranulpallemulle
 */
public class ValueSender implements Runnable{
    TCPSendData tcp;
    double xval = 0;
    double yval = 0;
    int bogiesetting = 0; // 0==off,1==forward,2==reverse
    int doreset = 0;
    double scoopval = 0;
    double limcircradius;
    boolean wrongVals = false;
    
    public ValueSender(double _limcircradius,TCPSendData _tcp){
        limcircradius=_limcircradius;
        this.tcp = _tcp;
    }
    public void beginTCP(){
        try{
            tcp.initialise(); //from TCPSendData
        }
        catch (IOException e){
            System.err.print("beginTCP failed");
        }
            
    }
    
    //public void sendVals(double _xval,double _yval){
    //    xval=(_xval/limcircradius)*128; //map to -128<x<128
    //    yval=(_yval/limcircradius)*128;
    //    //System.out.println("_xval : "+_xval);
    //    //System.out.println("_yval : "+_yval);
    //    //System.out.println("actualrad : "+Math.sqrt((xval*xval)+(yval*yval)));
    //    //System.out.println("limicircradius : "+limcircradius);
    //    makeComm();
    //}
    
    public void setSpeedVals(double _xval,double _yval){
        xval = (_xval/limcircradius)*128;
        yval = (_yval/limcircradius)*128;
    }
    
    public void setScoopVal(double scpval){
        scoopval=scpval*127; //map to -128<scoopval<128
    }
    
    public void setBogieVal(int bogieval){
        bogiesetting = bogieval;
    }
    public void setMCUreset(int resetval){
        doreset = resetval;
    }
    
    public void run(){ // run in a separate thread
        while (tcpConnValid()){
            makeComm();
        }
    }
    
    private void makeComm(){ //checking everything is fine and then send
        
        //System.out.println("Hi! x: "+this.xval+" y: "+this.yval);
        double rad=Math.sqrt((xval*xval)+(yval*yval));
        if (rad>128){
            System.out.println("ERROR! : RADIUS IS "+rad+">128");
            wrongVals=true;
        }
        else{
            wrongVals=false;
        }
        if (Double.isNaN(xval)||Double.isNaN(yval)){
            System.out.println("Nan detected");
            wrongVals=true;
        }
        else{
            wrongVals=false;
        }
        if((bogiesetting ==0)||(bogiesetting==1)||(bogiesetting==2)){
            //System.out.println(bogiesetting);
            wrongVals=false;
        }
        else{
            System.out.println("Bogie setting value not valid");
            wrongVals=true;
        }
        if((scoopval>127)||(scoopval<-127)){
            wrongVals = true;
            //System.out.println("Scoop setting outside range");
        }
        else{
            //System.out.println(scoopval);
            wrongVals = false;
        }
        
        if (!this.isWrong()){
             tcp.sendAll(xval,yval,bogiesetting,scoopval);
        }
    }
    
    public boolean isWrong() {
        return wrongVals;
    }
    public void close() {
        try{
            tcp.close();
        }
        catch (IOException e){
            System.err.print("Failed to close");
        }
    }
    public boolean tcpConnValid(){
        return tcp.isInitialised();
    }
    
    
}
