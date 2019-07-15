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
import java.net.InetSocketAddress;
import java.net.Socket;

/**
 *
 * @author Ranul Pallemulle
 */
public class Connection {
    
    private Socket socket;
    private BufferedReader input;
    private DataOutputStream output;
    
    public void open(String IP, int port) throws IOException {
        socket = new Socket();
        socket.connect(new InetSocketAddress(IP,port),5000); // 5 second timeout
        input = new BufferedReader(
                new InputStreamReader(socket.getInputStream()));
        output = new DataOutputStream(socket.getOutputStream());
    }
    
    public void close() throws IOException {
        if (output != null) {
            output.close();
        }
        if (input != null) {
            input.close();
        }
        if (socket != null) {
            socket.close();
        }
    }
    
    public boolean send(String data) throws IOException {
        byte[] bytes = data.getBytes();
        output.write(bytes);
        return input.readLine() != null;
    }
}
