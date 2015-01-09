/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 22:  takes a string and returns true if it is read the same forwards or back-wards (palindrome)


import java.io.*;
//import java.util.Random;


public class studentrecw22PROG
{
 
 public static  boolean  modelCheckPalindrome(String s)
{
 if(s.length() < 2) { return true;  }
  char first  = s.charAt(0);
  char last   = s.charAt(s.length()-1);
  if(  first != last  ) { return false; }
  else { return modelCheckPalindrome(s.substring(1,s.length()-1)); }	
}
	  
 public static void main(String [ ] args) 
{
  
    boolean SUCCESS1 = false;
    boolean SUCCESS2 = false;

    
    String str = "kcaack";
    
    if (checkPalindrome(str) == modelCheckPalindrome(str)) SUCCESS1 = true;

    str = "others";

    if (checkPalindrome(str) == modelCheckPalindrome(str)) SUCCESS2 = true;

    try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS1 && SUCCESS2) { 
   
      output.println("Well Done!");
      output.close();
     }
    else 
    {
     output.println("Try Again! Incorrect answer!");
     output.close();
    }
  
    }
      catch (IOException e) {
	e.printStackTrace();
    }

  }

  
