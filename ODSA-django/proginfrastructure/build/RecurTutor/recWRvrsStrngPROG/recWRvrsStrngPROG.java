/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 23: returns the given string in a reverse order.


import java.io.*;
import java.util.Random;

public class studentrecWRvrsStrngPROG
{
    private static final String CHAR_LIST =
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890";
    private static final int RANDOM_STRING_LENGTH = 10;

    public static  long fTimeout= 10;
    public static boolean fFinished= false;
    public static Throwable fThrown= null;
    public static String studentAnswer;
    public static String str;
        
    public static void evaluate() throws Throwable {
	    Thread thread= new Thread() {
		@Override
		public void run() {
		 try {
		  studentAnswer = reverseStringRecursive(str);
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
    
//This method generates random string
public static String generateRandomString(){
 Random randNumGenerator = new Random();
 StringBuffer randStr = new StringBuffer();
 for(int i=0; i<RANDOM_STRING_LENGTH; i++){
   int number =   randNumGenerator.nextInt(60);
   char ch = CHAR_LIST.charAt(number);
   randStr.append(ch);
  }
  return randStr.toString();
}
     
 
 public static  String modelReverseStringRecursive (String str)
{
 if (str.length() == 0)
  {
    return "";
  }
  return modelReverseStringRecursive(str.substring(1)) + str.charAt(0);
}
 public static void main(String [ ] args) 
{
  
    boolean SUCCESS = false;
   
    str = generateRandomString();
 
    try {
     // Fail on time out object
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
    
    if (studentAnswer.equals(modelReverseStringRecursive(str))) SUCCESS = true;

    try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS) { 
   
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

  
