/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 16:  prints the binary equivalent of an integer N
import java.io.*;
import java.util.Random;


public class studentRecHDecibinaryPROG
{
    public static  long fTimeout=5;
    public static boolean fFinished= false;
    public static Throwable fThrown= null;
    public static String studentAnswer;
    public static int number;
    
    public static void evaluate() throws Throwable {
	    Thread thread= new Thread() {
		@Override
		public void run() {
		 try {
		  studentAnswer = decibinary(number);
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
 
 
 public static String modeldecibinary (int num)
  {
   if ( num < 2)
     return Integer.toString(num);
   else
      return modeldecibinary(num/2) + Integer.toString(num%2);
  }
	
     
	
  public static void main(String [ ] args) {
    boolean SUCCESS = false;
   
    Random randNumGenerator = new Random();
    
    number=  (randNumGenerator.nextInt(20)+1);
    
	try {
     // Fail on time out object
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
    
    if (studentAnswer.equals(modeldecibinary(number))) SUCCESS = true;

    try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS) { 
   
      output.println("Well Done!");
      output.close();
     }
    else 
    {
     output.println("Try Again! Incorrect recursive call or action!");
     output.close();
    }
  
    }
      catch (IOException e) {
	e.printStackTrace();
    }

  }

  
