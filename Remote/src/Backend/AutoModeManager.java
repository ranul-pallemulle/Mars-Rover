/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package Backend;

import java.util.ArrayList;
import java.util.HashMap;

/**
 *
 * @author Ranul Pallemulle
 */
public class AutoModeManager {
    private HashMap<String,String> goalStatuses;
    private Connection connection;
    
    public AutoModeManager(Connection conn) {
        goalStatuses = new HashMap<>();
        goalStatuses.put("Samples","Disabled");
        connection = conn;
    }
    
    public void enableGoal(String goal) {
        String status = goalStatuses.get(goal);
        boolean allDisabled = true; // all goals are currently disabled
        
        for (String key : goalStatuses.keySet()) {
            String stat = goalStatuses.get(key);
            if (stat.equals("Enabled")) {
                allDisabled = false; // at least one goal is enabled
            }
        }
        if (status == null) { // Bad key
            return; // TODO
        }
        if (status.equals("Disabled")) {
            goalStatuses.put(goal, "Enabled");
            if (connection.isActive()) {
                if (allDisabled) {
                    connection.sendWithDelay("START AUTO", 1);
                }
                connection.send("AUTO -> Goal "+goal+" start");
            }
        }
        else {
            // TODO - status either "Enabled" or something else
        }
    }
    
    public void disableGoal(String goal) {
        String status = goalStatuses.get(goal);
        if (status == null) { // Bad key
            return; // TODO
        }
        if (status.equals("Enabled")) {
            goalStatuses.put(goal, "Disabled");
            if (connection.isActive()) {
                connection.send("AUTO -> Goal "+goal+" stop");
            }
        }
        else {
            // TODO - status either "Disabled" or something else
        }
    }
    
    public void disableAllGoals() {
        for (String key : goalStatuses.keySet()) {
            String status = goalStatuses.get(key);
            if (status == null) {
                continue;
            }
            if (status.equals("Enabled")) {
                goalStatuses.put(key, "Disabled");
            }
        }
        
        if (connection.isActive()) {
            connection.sendWithDelay("STOP AUTO", 1);
        }
    }
    
    public ArrayList<String> getNames() {
        ArrayList<String> list = new ArrayList<>();
        for (String key : goalStatuses.keySet()) {
            list.add(key);
        }
        return list;
    }
    
    public String getGoalStatu(String goal) {
        if (goal == null) {
            return null;
        }
        String status = goalStatuses.get(goal);
        return status;
    }
}
