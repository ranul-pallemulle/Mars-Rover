/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package joystick;

import gnu.io.CommPortIdentifier;
import gnu.io.SerialPort;
import gnu.io.SerialPortEvent;
import gnu.io.SerialPortEventListener;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.util.Enumeration;

/**
 *
 * @author ranulpallemulle
 */
public class SerialGetData implements SerialPortEventListener{
    SerialPort serialport;
    private static final String PORT_NAMES[] = {
        "/dev/cu.usbmodem1421"/* Mac*/,"/dev/cu.usbmodem1411","/dev/ttyUSB0"/*Linux*/,"COM35"/*Windows*/
    };
    private BufferedReader input;
    private OutputStream output;
    private static final int TIME_OUT = 2000;
    private static final int DATA_RATE = 9600;
    String inputLine;
    
    public void initialize() {
        CommPortIdentifier portID = null;
        Enumeration portEnum = CommPortIdentifier.getPortIdentifiers();
        while (portEnum.hasMoreElements()) {
            CommPortIdentifier currPortId = (CommPortIdentifier) portEnum.nextElement();
            for (String portName : PORT_NAMES){
                if (currPortId.getName().equals(portName)){
                    portID = currPortId;
                    break;
                }
            }
        }
        if (portID==null){
            System.out.println("Could not find COM port");
            return;
        }
        try {
            serialport = (SerialPort) portID.open(this.getClass().getName(),TIME_OUT);
            serialport.setSerialPortParams(DATA_RATE,
                    serialport.DATABITS_8,
                    serialport.STOPBITS_1,
                    serialport.PARITY_NONE);
            input = new BufferedReader (new InputStreamReader(serialport.getInputStream()));
            output = serialport.getOutputStream();
            
            serialport.addEventListener(this);
            serialport.notifyOnDataAvailable(true);
        } catch(Exception e){
            System.err.println(e.toString());
        }
    }
    
    public synchronized void close() {
        if (serialport != null) {
            serialport.removeEventListener();
            serialport.close();
        }
    }
    
    public synchronized void serialEvent(SerialPortEvent oEvent) {
        if (oEvent.getEventType() == SerialPortEvent.DATA_AVAILABLE) {
            try {
                inputLine=null;
                if (input.ready()){
                    inputLine = input.readLine();
                    //inputLine is the data read
                    //System.out.println(inputLine);
                }
            } catch (Exception e){
                System.err.println(e.toString());
            }
        }
    }
    public String getInputLine(){
        return inputLine;
    }
    
    
}
