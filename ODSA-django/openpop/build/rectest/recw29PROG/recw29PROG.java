/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 29: Given a string from which all characters except the bracketing operators have been removed. The method should return true if the bracketing operators in str are balanced, which means that they are correctly nested and aligned. If the string is not balanced, the method returns false

import java.io.*;
import java.util.Random;


public class studentrecw29PROG
{

public static boolean modelisBalanced(String str) {

   if (str.length() == 0) {
        return true;
    }
    if (str.contains("()")) {
        return modelisBalanced(str.replaceFirst("\\(\\)", ""));
    }

    if (str.contains("[]")) {
        return modelisBalanced(str.replaceFirst("\\[\\]", ""));
    }

    if (str.contains("{}")) {
        return modelisBalanced(str.replaceFirst("\\{\\}", ""));
    } else {
        return false;
    }
		
}	

 public static void main(String [ ] args) 
{
  
    boolean SUCCESS1 = false;
    boolean SUCCESS2 = false;

    String str1="{{}}";
    String str2="{{{}{{";

    if (isBalanced(str1)== modelisBalanced(str1)) SUCCESS1 = true;
    if (isBalanced(str2)== modelisBalanced(str2)) SUCCESS2 = true;
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

  
