/** Test program for recursion programming exercise.
Author: Sally Hamouda */

import java.io.*;
import java.util.Random;

public class studentrecWMinOpsPROG
{
    public static  long fTimeout= 10;
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
		  studentAnswer = minOps(x,y);
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
 
 public static  int modelminOps (int x, int y)
		
{
if (2*x > y)
   return y-x;
		
else if (y%2 == 1)
		
   return (modelminOps (x, y-1) + 1);
else
		
   return (modelminOps (x, y/2) + 1);
}


 public static void main(String [ ] args) 
{
  
    boolean SUCCESS = false;
   
    Random randNumGenerator = new Random();
    
    
    x= randNumGenerator.nextInt(100);
    y= randNumGenerator.nextInt(100);
    int temp= x;
  
    if (x>y){
     x=y;
     y=temp;
    }
    
    try {
     // Fail on time out object
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
    
    if (studentAnswer == modelminOps(x,y)) SUCCESS = true;

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

  
