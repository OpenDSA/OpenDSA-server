/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 13: takes a non-negative integer and returns the sum of its digits. For example, sumOfDigits(1234) returns 1+2+3+4 =10
import java.io.*;
import java.util.Random;


public class studentRecCSumOfDigitsPROG
{
    public static  long fTimeout=1;
    public static boolean fFinished= false;
    public static Throwable fThrown= null;
    public static int studentAnswer;
    public static int number;
    
    public static void evaluate() throws Throwable {
	    Thread thread= new Thread() {
		@Override
		public void run() {
		 try {
		  studentAnswer = sumOfDigits(number);
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
	
 public static int modelsumOfDigits(int number)
 {  
    if(number/10 == 0)
      return number;    
    return number%10 + modelsumOfDigits(number/10);
 }

     
	
  public static void main(String [ ] args) {
    boolean SUCCESS = false;
    
   
    Random randNumGenerator = new Random();
    number=  randNumGenerator.nextInt(1000000);
	
	try {
     // Fail on time out object
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
    
    if ( studentAnswer == modelsumOfDigits(number)) SUCCESS = true;

    try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS) { 
   
      output.println("Well Done!");
      output.close();
     }
    else 
    {
     output.println("Try Again! Incorrect recursive call!");
     output.close();
    }
  
    }
      catch (IOException e) {
	e.printStackTrace();
    }

  }

  
