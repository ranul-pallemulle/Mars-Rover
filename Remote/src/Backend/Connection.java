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
import java.util.concurrent.Semaphore;
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
    private Semaphore mutex;
    private boolean active;
    
    public Connection(Consumer<Exception> run_on_connection_loss) {
        mutex = new Semaphore(1);
        onConnectionLoss = run_on_connection_loss;
        active = false;
    }
    
    
    /**
     * Attempt a connection to the specified address.
     * @param IP - IP address to connect to
     * @param port - port to connect to
     * @param timeout - maximum time to wait for successful connection
     * @param timeout_on_read - if true, reads will have a timeout (=timeout)
     * @throws IOException - if connection attempt fails
     */
    public void open(String IP, int port, int timeout, boolean timeout_on_read) 
            throws IOException {
        try {
            socket = new Socket();
            if (timeout_on_read) {
                socket.setSoTimeout(timeout*1000); // timeout on read operations
            }
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
    
    
    /**
     * If a connection is active, close it. Does not throw exceptions.
     */
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
    
    
    /**
     * Read a line from the active connection. Blocks until something is 
     * received. If an exception occurs, send it to this.onConnectionLoss. Does 
     * not throw exceptions.
     * @return 
     */
    public String receive() {
        try{
            mutex.acquire();
            String data = input.readLine();
            return data;
        } catch (IOException | NullPointerException e) {
            active = false;
            onConnectionLoss.accept(e);
        } catch (InterruptedException ex) {
            Logger.getLogger(Connection.class.getName()).log(Level.SEVERE, null, ex);
        }
        finally {
            mutex.release();
        }
        return null;
    }
    
    
    /**
     * Send a string on the active connection. Expects a reply and blocks on 
     * read. The read will timeout based on whether the connection has timeouts 
     * enabled on reads or not. If an exception occurs, send it to 
     * this.onConnectionLoss. Does not throw exceptions.
     * @param data - string to send.
     * @return - true if a valid reply was received. false if an exception 
     * occurs.
     */
    public boolean send(String data) {
        try {
            mutex.acquire();
            byte[] bytes = data.getBytes();
            output.write(bytes);
            return (input.readLine() != null);
        }
        catch (IOException e) {
            active = false;
            onConnectionLoss.accept(e);
        } catch (InterruptedException ex) {
            Logger.getLogger(Connection.class.getName()).log(Level.SEVERE, null, ex);
        }
        finally {
            mutex.release();
        }
        return false;
    }
    
    
    /**
     * Same as send() but with after sending the string and receiving a reply, 
     * the thread sleeps for a specified duration. Does not throw exceptions.
     * @param data
     * @param timeout
     * @return - true if the delay completes successfully. false if an 
     * exception occurs.
     */
    public boolean sendWithDelay(String data, int timeout) {
        try {
            mutex.acquire();
            byte[] bytes = data.getBytes();
            output.write(bytes);
            input.readLine();
            TimeUnit.SECONDS.sleep(timeout);
            return true;
        }
        catch (IOException e) {
            active = false;
            onConnectionLoss.accept(e);
        } 
        catch (InterruptedException ex) {
            Logger.getLogger(Connection.class.getName()).log(Level.SEVERE, null, ex);
        }
        finally {
            mutex.release();
        }
        return false;
    }
    
    public boolean sendWithDelayMicroseconds(String data, int timeout) {
        try {
            mutex.acquire();
            byte[] bytes = data.getBytes();
            output.write(bytes);
            input.readLine();
            TimeUnit.MICROSECONDS.sleep(timeout);
            return true;
        }
        catch (IOException e) {
            active = false;
            onConnectionLoss.accept(e);
        } 
        catch (InterruptedException ex) {
            Logger.getLogger(Connection.class.getName()).log(Level.SEVERE, null, ex);
        }
        finally {
            mutex.release();
        }
        return false;
    }
    
    /**
     * Continuously write the string "PING" and expect a reply. A delay of 1 
     * second follows the reply. Spawn a new thread for this. Does not throw 
     * exceptions.
     */
    public void startPing() {
        new Thread(() -> {
            try {
                while (true) {
                    mutex.acquire();
                    output.write("PING".getBytes());
                    input.readLine();
                    mutex.release();
                    TimeUnit.SECONDS.sleep(1);
                }
            } catch (IOException ex) { // connection error or read timeout
                active = false;
                onConnectionLoss.accept(ex);
            } catch (InterruptedException ex) {
                // active = false;
                Logger.getLogger(Connection.class.getName()).log(Level.SEVERE, null, ex);
            } finally {
                mutex.release();
            }
        }).start();
    }
    
    
    /**
     * Get the value of the this.active field. If the value is true, the 
     * connection is active.
     * @return - the current connection status.
     */
    public boolean isActive() {
        return active;
    }
}
