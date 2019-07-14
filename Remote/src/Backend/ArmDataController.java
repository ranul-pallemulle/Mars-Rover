/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package Backend;

import Exceptions.BadDeleteException;
import Exceptions.FormatException;
import Exceptions.NotFoundException;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import static java.lang.Math.PI;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Control reading and writing of robotic arm servo angle settings to/from a 
 * data file.
 * @author Ranul Pallemulle
 */
public class ArmDataController {
    
    private File file; // data file containing angle settings
    private BufferedReader bReader;
    private BufferedWriter bWriter;
    private List<String> lines; // named angle settings read from data file
    
    public ArmDataController () {
        lines = new ArrayList<>();
    }
    
    /**
     * Attempt to open a data file. If a file was previously open, close it.
     * @param _file
     * @throws IOException - if file cannot be opened for read and write
     * @throws FormatException - if the file data is of the wrong format
     */
    public void importFile(File _file) throws IOException, FormatException {
        if (file != null) {
            closeFile(); // close previously open file
        }
        file = _file;
        try {
            bReader = new BufferedReader(new FileReader(file));
            bWriter = new BufferedWriter(new FileWriter(file, true)); // open in append mode
            // Read data in to the member list
            String line;
            while ((line = bReader.readLine()) != null) {
                lines.add(line); // read data in to member list
            }      
        }
        catch (IOException ex) {
            closeFile();
            throw ex;
        }
        // Check that new data is valid
        String error;
        if ((error = invalidData(lines)) != null) {
            closeFile();
            throw new FormatException (error);
        }
        // Check that the new data contains settings for DROP1, DROP2, WATCH and PICK
        if (!containsData(lines,"DROP1") || !containsData(lines,"DROP2") ||
            !containsData(lines,"WATCH") || !containsData(lines,"PICK")) {
            closeFile();
            throw new FormatException("Data file does not contain required "
                    + "settings for DROP1,DROP2,WATCH and PICK.");
        }
    }
    
    
    /**
     * Change existing data or add new data if it doesn't exist to the member 
     * list and write out the changes to the data file.
     * @param data - data string containing data name and angles
     * @throws IOException - if file is not open
     * @throws FormatException - if data argument is not of the right format
     * @return - true if data was changed, else false.
     */
    public boolean editDataItem(String data) throws IOException, FormatException{
        if (!isValidDataString(data)) {
            throw new FormatException("Invalid data format.");
        }
        String dataName = findDataName(data);
        for (int i = 0; i < lines.size(); ++i) { // loop over all lines
            if (lines.get(i).equals(data)) { // data already exists
                return false; // nothing to do
            }
            if (lines.get(i).contains(dataName)) { // different data of same name exists
                lines.set(i, data); // edit member list
                updateFileWithList(); // write out changes
                return true;
            }
        }
        // data does not exist, add it
        lines.add(data);
        try {
            bWriter.newLine();
            bWriter.write(data);
            bWriter.flush();            
        }
        catch (IOException ex) {
            closeFile();
            throw ex;
        }
        return true;
    }
    
    
    /**
     * Remove the specified data from the member list and write out the changes 
     * to the data file.
     * @param data
     * @throws IOException - if file is not open
     * @throws NotFoundException - specified data does not exist on the member 
     * list to delete it.
     */
    public void removeDataItem(String data) throws IOException, NotFoundException, BadDeleteException {
        if (!isValidDataString(data)) {
            throw new NotFoundException("Data not found.");
        }
        int delIdx = lines.indexOf(data);
        if (delIdx == -1) {
            throw new NotFoundException("Data not found.");
        }
        String name = findDataName(data);
        if (name.equals("DROP1") || name.equals("DROP2") || name.equals("WATCH") 
            || name.equals("DEFAULT") || name.equals("PICK")) {
            throw new BadDeleteException("DEFAULT,DROP1,DROP2,WATCH,PICK are "
                    + "required settings");
        }
        lines.remove(data); // edit member list
        updateFileWithList(); // write out changes
    }
    
    
    
    public double[] getAnglesByName(String name) throws FormatException, NotFoundException {
        String dataString;
        if ((dataString = getDataString(lines,name)) != null) {
            double[] angles = parseData(dataString);
            return angles;
        }
        else {
            throw new NotFoundException("Data not found.");
        } 
    }
    
    
    /**
     * Close the data file. Ignore IOException.
     */
    public void closeFile () {
        try {
            lines.clear();
            bReader.close();
            bWriter.close();
            file = null;
        } catch (IOException ex) {
            Logger.getLogger(ArmDataController.class.getName()).log(Level.WARNING, null, ex);
        }
    }
    
    
    /**
     * Return list containing all data items.
     * @return 
     */
    public List<String> getAllItems() {
        return lines;
    }
    
    
    /**
     * Extract robotic arm angle data from a data string.
     * @param data - String containing data name and arm angle data in the order 
     * base,elbow,top,gripper
     * @return - array of 4 angles in the order base,elbow,top,gripper
     * @throws FormatException 
     */
    public double[] parseData(String data) throws FormatException {
        if (!isValidDataString(data)) {
            throw new FormatException("Invalid data format.");
        }
        String angleData = findAngleString(data);
        String[] angleStringList = angleData.split(","); // list of angles
        double[] angles = new double[4];
        for (int i = 0; i < 3; ++i) {
            angles[i] = -Double.parseDouble(angleStringList[i])*PI/180;
        }
        angles[3] = Double.parseDouble(angleStringList[3]); // gripper
        return angles;
    }
    
    
    /**
     * Return data file status.
     * @return 
     */
    public boolean dataFileOpen() {
        return (file != null);
    }
    
    
    /**
     * Write out data as listed in the member list to the data file.
     * @throws IOException - if the data file is not open
     */
    private void updateFileWithList() throws IOException {
        try {
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
            bReader = new BufferedReader(new FileReader(file)); // reinitialize reader
        }
        catch (IOException ex) {
            closeFile();
            throw ex;
        }
    }
    
    
    /**
     * Check a list of Strings for whether a data item of a given name is 
     * present. Assume data is of the correct format and no duplicates are 
     * present.
     * @param data - list containing data to match against
     * @param name - data name to search for
     * @return - true if data item of the specified name is present, else false.
     */
    private boolean containsData (List<String> data, String name) {
        for (String line : data) {
            String dataName = findDataName(line);
            if (dataName.equals(name)) {
                return true;
            }
        }
        return false;
    }
    
    
    /**
     * Retrieve the data string inside a list, given the name. Assume data is 
     * of the correct format and no duplicates are present.
     * @param data
     * @param name
     * @return 
     */
    private String getDataString(List<String> data, String name) {
        for (String line : data) {
            String dataName = findDataName(line);
            if (dataName.equals(name)) {
                return line;
            }
        }
        return null;
    }
    
    
    /**
     * Check list of dataList items for presence of dataList, validity of format, and 
     * presence of duplicates.
     * @param dataList - list of Strings, each of which is to be checked.
     * @return - an error message if any dataList is invalid. null if all dataList is 
     * valid.
     */
    private String invalidData(List<String> dataList) {
        String error = null;
        if (dataList.isEmpty()) {
            error = "Empty data list.";
        }
        List<String> namesList = new ArrayList<>();
        for (String line : dataList) {
            if (!isValidDataString(line)) {
                error = "Line in data has an invalid format.";
                break;
            }
            String dataName = findDataName(line);
            // regex matches - no need to check if findDataName returns ""
            if (namesList.contains(dataName)) {
                error = "Data list contains duplicates";
                break;
            }
            else {
                namesList.add(dataName);
            }
        }
        return error;
    }
    
    
    /**
     * Check if data string is of the right format
     * @param data - string to check
     * @return - true if data is of the right format
     */
    private boolean isValidDataString(String data) {
        // valid string has form: "dataName:ang1,ang2,ang3,ang4"
        if (data == null) {
            return false;
        }
        String regex = "\\w+:(-?[0-9]{1,3}(\\.[0-9])?,){3}-?[0-9]{1,3}(\\.[0-9])?"; 
        Pattern pattern = Pattern.compile(regex);
        Matcher m = pattern.matcher(data);
        return m.matches();
    }
    
    
    /**
     * Find the data name within the provided data string. Assume data is of the 
     * correct format.
     * @param data
     * @return - data name or "" if data name is not found.
     */
    private String findDataName(String data) {
        int colonIdx = data.indexOf(":");
        String dataName = data.substring(0,colonIdx);
        return dataName;
    }
    
    
    /**
     * Find the angle data within the provided data string. Assume data is of 
     * the correct format.
     * @param data
     * @return - String containing a comma separated list of angles.
     */
    private String findAngleString(String data) {
        int colonIdx = data.indexOf(":");
        String angles = data.substring(colonIdx+1);
        return angles;
    }
}
