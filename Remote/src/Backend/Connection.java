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
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author Ranul Pallemulle
 */
public class Connection {
    
    private Socket socket;
    private BufferedReader input;
    private DataOutputStream output;
    private Consumer<Exception> onConnectionLoss;
    private boolean active;
    
    public Connection(Consumer<Exception> run_on_connection_loss) {
        onConnectionLoss = run_on_connection_loss;
        active = false;
    }
    
    public void open(String IP, int port, int timeout) throws IOException {
        try {
            socket = new Socket();
            socket.setSoTimeout(timeout*1000); // timeout on read operations
            socket.connect(new InetSocketAddress(IP,port),timeout*1000);
            input = new BufferedReader(
                    new InputStreamReader(socket.getInputStream()));
            output = new DataOutputStream(socket.getOutputStream());
            active = true;
        }
        catch (IOException e) {
            active = false;
            throw e;
        }
        
    }
    
    public void close() {
        if (socket != null) {
            try {
                socket.close();
            } catch (IOException ex) {
                // ignore
            } finally {
                active = false;
            }
        }
    }
    
    public boolean send(String data) {
        try {
            byte[] bytes = data.getBytes();
            output.write(bytes);
            return (input.readLine() != null);
        }
        catch (IOException e) {
            active = false;
            onConnectionLoss.accept(e);
        }
        return false;
    }
    
    public boolean sendWithDelay(String data, int timeout) {
        try {
            byte[] bytes = data.getBytes();
            output.write(bytes);
            input.readLine();
            TimeUnit.SECONDS.sleep(timeout);
            return true;
        }
        catch (IOException e) {
            active = false;
            onConnectionLoss.accept(e);
        } catch (InterruptedException ex) {
            Logger.getLogger(Connection.class.getName()).log(Level.SEVERE, null, ex);
        }
        return false;
    }
    
    public void startPing() {
        new Thread(() -> {
            try {
                while (true) {
                    output.write("PING".getBytes());
                    input.readLine();
                    TimeUnit.SECONDS.sleep(1);
                }
            } catch (IOException ex) { // connection error or read timeout
                active = false;
                onConnectionLoss.accept(ex);
            } catch (InterruptedException ex) {
                active = false;
                Logger.getLogger(Connection.class.getName()).log(Level.SEVERE, null, ex);
            }
        }).start();
    }
    
    public boolean isActive() {
        return active;
    }
}
