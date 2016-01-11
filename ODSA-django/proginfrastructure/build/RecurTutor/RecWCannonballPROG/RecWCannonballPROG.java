/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 21:  takes as its argument the height of a pyramid	of cannonballs and returns the number of cannonballs it contains based on the height of the stack

import java.io.*;
import java.util.Random;


public class studentRecWCannonballPROG
{
    public static  long fTimeout= 10;
    public static boolean fFinished= false;
    public static Throwable fThrown= null;
    public static int studentAnswer;
    public static int height;
    
            
    public static void evaluate() throws Throwable {
	    Thread thread= new Thread() {
		@Override
		public void run() {
		 try {
		  studentAnswer = Cannonball(height) ;
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
 public static  int  modelCannonball(int height)
{
  if (height == 0)		
  {
   return 0;
  }
  else
  {
   return (height * height + modelCannonball(height - 1));
  }
}
	  
 public static void main(String [ ] args) 
{
  
    boolean SUCCESS = false;

    Random randNumGenerator = new Random();
    
    height = randNumGenerator.nextInt(30)+1;
     try {
     // Fail on time out object
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
    
    if (studentAnswer == modelCannonball(height)) SUCCESS = true;

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

  
