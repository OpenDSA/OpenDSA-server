
/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 6: computes the value of y to the x power
import java.io.*;
import java.util.Random;


public class studentrecCPowerPROG
{
    public static  long fTimeout=1;
    public static boolean fFinished= false;
    public static Throwable fThrown= null;
    public static int studentAnswer;
    public static int x;
    public static int y;
    public static void evaluate() throws Throwable {
	    Thread thread= new Thread() {
		@Override
		public void run() {
		 try {
		  studentAnswer = power(x , y);
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
 
 // The model answer of the largest number: the student is asked to write the base case
 public static int modelpower(int x, int y) {
  if ( x == 1 )

   return y;

  else

   return modelpower(x-1, y) * y;
}
 

  public static void main(String [ ] args) {
   boolean SUCCESS = false;
    
    // To test: generate a random number
   Random randNumGenerator = new Random();
   x=  randNumGenerator.nextInt(100)+1;
   y=  randNumGenerator.nextInt(100)+1;
   try {
     // Fail on time out object
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
    if ( studentAnswer == modelpower(x,y)) SUCCESS = true;

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

  
