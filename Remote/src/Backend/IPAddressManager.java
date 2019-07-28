/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package Backend;

import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.HashMap;

/**
 *
 * @author Ranul Pallemulle
 */
public class IPAddressManager {
    private HashMap<String,String> ip_addresses;
    private static String currentIP;
    public IPAddressManager() {
        ip_addresses = new HashMap<>();
        ip_addresses.put("WiFi", "192.168.4.1");
        ip_addresses.put("Ethernet", "10.42.0.137");
        ip_addresses.put("Local","localhost");
    }
    
    public String locateRaspberryPi() {
        try {
            InetAddress ip = InetAddress.getByName("raspberrypi.local");
            String address = ip.getHostAddress();
            ip_addresses.put("Found Rover", address);
            return address;
        } catch (UnknownHostException ex) {
            return null;
        }
    }
    
    public ArrayList<String> getNames() {
        ArrayList<String> list = new ArrayList<>();
        for (String key : ip_addresses.keySet()) {
            list.add(key);
        }
        return list;
    }
    
    public String getIpFromKey(String name) {
        return ip_addresses.get(name);
    }
    
    public static void setCurrentIP(String ip) {
        currentIP = ip;
    }
    
    public static String getCurrentIP() {
        return currentIP;
    }
}
