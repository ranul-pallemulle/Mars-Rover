/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package Backend;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import static java.lang.Math.PI;
import java.util.ArrayList;
import java.util.List;

/**
 *
 * @author ranul
 */
public class ArmDataFileController {
    
    private File file;
    private FileReader fReader;
    private FileWriter fWriter;
    private BufferedReader bReader;
    private BufferedWriter bWriter;
    private List<String> lines;
    
    public ArmDataFileController () {
        lines = new ArrayList<>();
    }
    
    public void importFile(File _file) throws IOException {
        file = _file;
        fWriter = new FileWriter(file,true);
        fReader = new FileReader(file);
        bReader = new BufferedReader(fReader);
        bWriter = new BufferedWriter(fWriter);
        String line;
        lines.clear();
        while ((line = bReader.readLine()) != null) {
            lines.add(line);
        }
    }
    
    public void editDataItem(String data) throws IOException {
        int colonIdx = data.indexOf(":");
        if (colonIdx == -1) {
            return;
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
        fReader.close();
        fWriter.close();
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
        fWriter.close(); // close while in append mode
        fWriter = new FileWriter(file, false); // reopen in overwrite mode
        bWriter = new BufferedWriter(fWriter);
        if (lines.size() > 0) {
            bWriter.write(lines.get(0)); // write first line
        }
        bWriter.flush();
        fWriter.close(); // close while in overwrite mode
        fWriter = new FileWriter(file,true); // reopen in append mode
        bWriter = new BufferedWriter(fWriter);
        for (int i = 1; i < lines.size(); ++i) { // append rest of lines
            bWriter.newLine();
            bWriter.write(lines.get(i));
        }
        bWriter.flush();
        
        fReader = new FileReader(file);
        bReader = new BufferedReader(fReader);
    }
}
