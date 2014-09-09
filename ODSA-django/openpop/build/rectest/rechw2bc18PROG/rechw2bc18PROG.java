/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 18:  given two Strings, returns true if the two strings have the same sequence of characters but in the opposite order (ignoring white space and capitalization), and returns false otherwise
import java.io.*;
import java.util.Random;


public class studentrechw2bc18PROG
{
 
 public static  boolean modelisReverse(String s1, String s2) {  
 if  (s1.length() == 0 && s2.length() == 0)
   return true;
 else if (s1.length() == 0 || s2.length() == 0)
   return false;	  
 else
 {
   String s1first = s1.substring(0, 1);
   String s2last = s2.substring(s2.length() - 1);
   return s1first.equalsIgnoreCase(s2last) && modelisReverse(s1.substring(1), s2.substring(0, s2.length()-1));
 }
}
	  
  public static void main(String [ ] args) {
    boolean SUCCESS1 = false;
    boolean SUCCESS2 = false;
    //In case they are reverse of each others
    String s1 = "abc";
    String s2 = "cba";

    if (isReverse(s1,s2)==modelisReverse(s1,s2)) SUCCESS1 = true;

    //In case they are not reverse of each others
    s1 = "a1bc";
    s2 = "cba";

    if (isReverse(s1,s2)==modelisReverse(s1,s2)) SUCCESS2 = true;
    
    try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS1 && SUCCESS2) { 
   
      output.println("Well Done!");
      output.close();
     }
    else 
    {
     output.println("Try Again! Incorrect base cases!");
     output.close();
    }
  
    }
      catch (IOException e) {
	e.printStackTrace();
    }

  }

  
