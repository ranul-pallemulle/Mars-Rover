/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package Backend;

import java.util.Queue;
import org.apache.commons.collections4.queue.CircularFifoQueue;
import java.util.function.Consumer;

/**
 *
 * @author Ranul Pallemulle
 */
public class Diagnostics {
    Consumer<Queue> print;
    Connection connection;
    Queue<String> buffer;
    
    public Diagnostics(Consumer<Queue> print_method) {
        print = print_method;
        buffer = new CircularFifoQueue<String>(9);
    }
    
    public void initialiseConnection(Consumer<Exception> e) {
        connection = new Connection(e);
    }
    
    public Connection getConnection() {
        return connection;
    }
    
    public void begin() {
        new Thread(()->{
            while (true) {
                String message = connection.receive();
                if (message != null) {
                    buffer.add(message);
                    print.accept(buffer);
                }
            }
        }).start();
    }
}
