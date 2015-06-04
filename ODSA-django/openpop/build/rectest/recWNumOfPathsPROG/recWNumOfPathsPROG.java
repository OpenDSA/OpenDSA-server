/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 26: this function counts the number of different ways to reach a basketball score. Example: For the input 3, the output will be 4, since there are 4 different	ways to accumulate 3: 1+1+1, 1+2, 2+1, 3.


import java.io.*;
import java.util.Random;

public class studentrecWNumOfPathsPROG
{
	public static  long fTimeout= 10;
    public static boolean fFinished= false;
    public static Throwable fThrown= null;
    public static int studentAnswer;
    public static int n;
        
    public static void evaluate() throws Throwable {
	    Thread thread= new Thread() {
		@Override
		public void run() {
		 try {
		  studentAnswer = numOfPaths(n);
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

 public static  int modelnoOfPath (int n)
		
 {
	 if (n==1)
	  return 1;
	 if (n==2)
	  return 2;
	 if (n==3)
	  return 4;
			
	 return modelnoOfPath(n-1) + modelnoOfPath(n-2) + modelnoOfPath(n-3);
		
}

 public static void main(String [ ] args) 
{
  
    boolean SUCCESS = false;
   
    Random randNumGenerator = new Random();
    
    n= randNumGenerator.nextInt(20);
    
    
    try {
     // Fail on time out object
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
    
    if (studentAnswer == modelnoOfPath(n)) SUCCESS = true;
    
    SUCCESS = false;
    n= randNumGenerator.nextInt(20);
    try {
     // Fail on time out object
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
    
    if (studentAnswer == modelnoOfPath(n)) SUCCESS = true;

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

  
