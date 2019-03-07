/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package joystick; 

//used for the physical joystick

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 *
 * @author ranulpallemulle
 */
public class InputDataProcessor {
    SerialGetData data;
    boolean firstrun=true;
    List<Double> prevdoubleitems;
    public InputDataProcessor(SerialGetData _data){
        this.data=_data;
    }
    public List<Double> giveResult(){
        String rawdata=data.getInputLine(); //data comes in as "switch,xval,yval"
        //System.out.println("giveResult: "+rawdata);
        List<Double> doubleitems;
        if (rawdata!=null){
            List<String> items = Arrays.asList(rawdata.split("\\s*,\\s*"));
            doubleitems= new ArrayList<>();
            for (String i : items){
                doubleitems.add(items.indexOf(i),Double.parseDouble(i));
            }
        }
        else{
             if(firstrun){
                doubleitems=Arrays.asList(1.0,127.0,127.0);
                firstrun=false;
             }
             else{
                 doubleitems=prevdoubleitems;
             }
        }
        if(doubleitems.size()<3){
            doubleitems=prevdoubleitems; 
        }
        
        prevdoubleitems=doubleitems;
        //MAKE SURE TO FIX THE OVERSHOOT OF JOYSTICK VALUES ON ARDUINO, TO SAVE COMPUTER PROCESSOR LOAD
        return doubleitems;
    }
    public void beginSerial(){
        data.initialize();
    }
    public void stopSerial(){
        data.close();
    }
    
}
