/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 29: Given a string from which all characters except the bracketing operators have been removed. The method should return true if the bracketing operators in str are balanced, which means that they are correctly nested and aligned. If the string is not balanced, the method returns false

import java.io.*;
import java.util.Random;


public class studentRecWIsbalancedPROG
{
    public static  long fTimeout= 10;
    public static boolean fFinished= false;
    public static Throwable fThrown= null;
    public static boolean studentAnswer;
    public static String str;
        
    public static void evaluate() throws Throwable {
	    Thread thread= new Thread() {
		@Override
		public void run() {
		 try {
		  studentAnswer = isBalanced(str);
		  fFinished= true;
		 } 
          catch (Throwable e) {
		  fThrown= e;
		 }
	       }
	 };
	
        thread.start();
		thread.join(fTimeout);
		if (fFinished)
			return;
		if (fThrown != null)
			throw fThrown;
		Exception exception= new Exception(String.format(
				"test timed out after %d milliseconds", fTimeout));
		exception.setStackTrace(thread.getStackTrace());
		throw exception;
	
	} 

public static boolean modelisBalanced(String str) {

   if (str.length() == 0) {
        return true;
    }
    if (str.contains("()")) {
        return modelisBalanced(str.replaceFirst("\\(\\)", ""));
    }

    else {
        return false;
    }
		
}	

 public static void main(String [ ] args) 
{
  
    boolean SUCCESS1 = false;
    boolean SUCCESS2 = false;

    str="(())";
         
    try {
     // Fail on time out object
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
    
    if (studentAnswer == modelisBalanced(str)) SUCCESS1 = true;
    
    str="((()((";

    
    try {
     // Fail on time out object
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
    
    if (studentAnswer ==  modelisBalanced(str)) SUCCESS2 = true;
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

  
