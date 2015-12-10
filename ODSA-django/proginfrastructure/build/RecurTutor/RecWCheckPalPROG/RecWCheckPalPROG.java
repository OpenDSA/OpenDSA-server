/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 22:  takes a string and returns true if it is read the same forwards or back-wards (palindrome)


import java.io.*;
//import java.util.Random;


public class studentRecWCheckPalPROG
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
		  studentAnswer = checkPalindrome(str);
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

    
    str = "kcaack";
    
     try {
     // Fail on time out object
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
    
    if (studentAnswer == modelCheckPalindrome(str)) SUCCESS1 = true;

    str = "others";

    try {
     // Fail on time out object
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
    
    if (studentAnswer == modelCheckPalindrome(str)) SUCCESS2 = true;

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

  
