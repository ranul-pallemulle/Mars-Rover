/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package Backend;

import Exceptions.FormatException;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import static java.lang.Math.PI;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 *
 * @author ranul
 */
public class ArmDataController {
    
    private File file;
    private BufferedReader bReader;
    private BufferedWriter bWriter;
    private List<String> lines;
    
    public ArmDataController () {
        lines = new ArrayList<>();
    }
    
    public void importFile(File _file) throws IOException, FormatException {
        if (file != null) {
            closeFile();
        }
        file = _file;
        bReader = new BufferedReader(new FileReader(file));
        bWriter = new BufferedWriter(new FileWriter(file, true)); // open in append mode
        // Read data in to the member list
        String line;
        List<String> backupList = new ArrayList<>(lines); // restore later if needed
        lines.clear();
        while ((line = bReader.readLine()) != null) {
            lines.add(line);
        }
        // Check that new data is of the right format
        String error;
        if ((error = invalidData(lines)) != null) {
            lines = backupList;
            throw new FormatException (error);
        }
        // Check that the new data contains settings for DROP1, DROP2, WATCH and PICK
        if (!containsData(lines,"DROP1") || !containsData(lines,"DROP2") ||
            !containsData(lines,"WATCH") || !containsData(lines,"PICK")) {
                lines = backupList;
                throw new FormatException("Data file does not contain required "
                        + "settings for DROP1,DROP2,WATCH and PICK.");
        }
        
    }
    
    public void editDataItem(String data) throws IOException {
        if (file == null) {
            throw new FileNotOpenException;
        }
        int colonIdx = data.indexOf(":");
        if (colonIdx == -1) {
            return; // TODO
        }
        String dataName = data.substring(0, colonIdx);
        for (int i = 0; i < lines.size(); ++i) { // loop over all lines
            if (lines.get(i).equals(data)) { // data already exists
                return; // nothing to do
            }
            if (lines.get(i).contains(dataName)) { // different data of same name exists
                lines.set(i, data); // edit 
                updateFileWithList();
                return;
            }
        }
        // data does not exist, add it
        lines.add(data);
        bWriter.newLine();
        bWriter.write(data);
        bWriter.flush();
    }
    
    
    public void removeDataItem(String data) throws IOException {
        int delIdx = lines.indexOf(data);
        if (delIdx == -1) {
            return;
        }
        lines.remove(data);
        updateFileWithList();
    }
    
    public void closeFile () throws IOException {
        bReader.close();
        bWriter.close();
    }
    
    public List<String> getAllItems() {
        return lines;
    }
    
    public double[] parseData(String data) {
        int colonIdx = data.indexOf(":");
        String subdat = data.substring(colonIdx+1);
        String[] angstr = subdat.split(",");
        if (angstr.length != 4) {
            
        }
        double[] ang = new double[4];
        for (int i = 0; i < 4; ++i) {
            ang[i] = -Double.parseDouble(angstr[i])*PI/180;
        }
        return ang;
    }
    
    public boolean haveFile () {
        return (file != null);
    }
    
    private void updateFileWithList () throws IOException {
        bWriter.close(); // close while in append mode
        bWriter = new BufferedWriter(new FileWriter(file, false)); // reopen in overwrite mode
        if (lines.size() > 0) {
            bWriter.write(lines.get(0)); // write first line
        }
        bWriter.flush();
        bWriter.close(); // close while in overwrite mode
        bWriter = new BufferedWriter(new FileWriter(file, true)); // reopen in append mode
        for (int i = 1; i < lines.size(); ++i) { // append rest of lines
            bWriter.newLine();
            bWriter.write(lines.get(i));
        }
        bWriter.flush();
        bReader = new BufferedReader(new FileReader(file));
    }
    
    /**
     * Checks a list of Strings for whether a data item of a given name is 
     * present and returns true if it is. If the List of Strings is of the 
     * wrong format, throws a FormatException.
     * @param data
     * @param name
     * @return 
     */
    private boolean containsData (List<String> data, String name) throws FormatException {
        boolean found = false;
        for (String line : data) {
            int colonIdx = line.indexOf(":");
            if (colonIdx == -1) {
                throw new FormatException("Line does not contain colon.");
            }
            String dataName = line.substring(0,colonIdx);
            if (dataName.equals(name)) {
                if (found) {
                    throw new FormatException("Duplicate data name found.");
                }
                found = true;
            }
        }
        if (found) {
            return true;
        }
        else {
            return false;
        }
        
    }
    
    private String invalidData(List<String> data) throws FormatException {
        // regex for pattern like "name:12,172,0,1" or "other:12,-50,-1,2"
        String regex = "\\w+:-?[0-9]{1,3},-?[0-9]{1,3},-?[0-9]{1,3},-?[0-9]{1,3}"; 
        Pattern pattern = Pattern.compile(regex);
        Matcher m; 
        for (String line : data) {
            m = pattern.matcher(line);
            if (!m.matches()) {
                return "Line in data has an invalid format";
            }
        }
        return null;
    }
    
    private int findOccurrences(String expr, String pattern) {
        int idx = 0;
        int count = 0;
        while (idx != -1) {
            idx = expr.indexOf(pattern,idx);
            if (idx != -1) {
                count++;
                idx += pattern.length();
            }
        }
        return count;
    }
}
