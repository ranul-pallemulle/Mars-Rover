/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package Backend;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.logging.Level;
import java.util.logging.Logger;
import javafx.application.Platform;
import javafx.scene.control.TextArea;

/**
 *
 * @author Ranul Pallemulle
 */
public class DiagnosticReceiver implements Runnable {
    Socket ClientSock;
    BufferedReader input;
    String IP;
    int port;
    String data;
    boolean running;
    TextArea txt;
    
    public DiagnosticReceiver() {
        this.IP = null;
        this.port = 0;
    }
    
    public void initialise(String _IP, int _port) throws UnknownHostException, IOException{//throws delcares exceptions, tried the clause and then catches
        this.IP = _IP;
        this.port = _port;
        ClientSock = new Socket(IP,port);
        input = new BufferedReader(new InputStreamReader(ClientSock.getInputStream()));
    }
    
    public void close_socket() {
        try {
            ClientSock.close();
        } catch (IOException ex) {
            Logger.getLogger(DiagnosticReceiver.class.getName()).log(Level.SEVERE, null, ex);
        }
        running = false;
    }
    
    public boolean is_running() {
        return running;
    }
    
    public void pass_text_box(TextArea ta) {
        this.txt = ta;
    }
    
    @Override
    public void run() {
        running = true;
        String spaces = "                    ";
        while (true) {
            if (!running)
                break;
            try {
                data = input.readLine();
            } catch (IOException ex) {
                Logger.getLogger(DiagnosticReceiver.class.getName()).log(Level.SEVERE, null, ex);
            }
            if (data != null && txt != null) {
                //System.out.println(data);
                    //txt.setText(spaces+"*** Output from rover ***\n\n"+spaces+data);
                //txt.setText(data+"\n");
                Platform.runLater(()->txt.appendText(spaces+data+"\n"));
            }
        }
    }
    
    
}
