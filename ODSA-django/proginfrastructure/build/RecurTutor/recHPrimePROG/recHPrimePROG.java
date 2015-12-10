/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 15:  determines if an integer N is prime or not
import java.io.*;
import java.util.Random;


public class studentrecHPrimePROG
{
 
    public static  long fTimeout=3;
    public static boolean fFinished= false;
    public static Throwable fThrown= null;
    public static boolean studentAnswer;
    public static int number;
   
    
    public static void evaluate() throws Throwable {
	    Thread thread= new Thread() {
		@Override
		public void run() {
		 try {
		  studentAnswer = Prime(number, number-1);
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
 
 
 public static boolean modelPrime(int X,int Y)
{
   if ( Y == 1)
    return true;
  else if ( X%Y == 0)
    return false;	
   else
    return modelPrime(X,Y-1);
}
	
     
	
  public static void main(String [ ] args) {
    boolean SUCCESS1 = false;
    boolean SUCCESS2 = false;
    
    boolean SUCCESS = false;
    
    Random randNumGenerator = new Random();
    
    number=  randNumGenerator.nextInt(100)+1;
	
      try {
     // Fail on time out object
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
    
    if (studentAnswer == modelPrime(number , number-1))
        SUCCESS1 = true;
    
    number=  randNumGenerator.nextInt(100)+1;
    
      try {
     // Fail on time out object
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
    
    if (studentAnswer == modelPrime(number , number-1))
        SUCCESS2 = true;
        
    if (SUCCESS1 && SUCCESS2)
       SUCCESS = true;
           
    try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS) { 
   
      output.println("Well Done!");
      output.close();
     }
    else 
    {
     output.println("Try Again! Incorrect Base Case(s)");
     output.close();
    }
  
    }
      catch (IOException e) {
	e.printStackTrace();
    }

  }

  
