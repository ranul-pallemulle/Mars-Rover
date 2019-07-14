/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package Exceptions;

/**
 *
 * @author Ranul Pallemulle
 */
public class BadDeleteException extends Exception{
    public BadDeleteException (String errorMessage) {
        super (errorMessage);
    }
}
