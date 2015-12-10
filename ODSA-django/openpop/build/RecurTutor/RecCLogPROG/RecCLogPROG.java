
/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 3: computes logb n

import java.io.*;
import java.util.Random;


public class studentRecCLogPROG
{ 
    public static  long fTimeout=1;
    public static boolean fFinished= false;
    public static Throwable fThrown= null;
    public static int studentAnswer;
    public static int b;
    public static int n;
    public static void evaluate() throws Throwable {
	    Thread thread= new Thread() {
		@Override
		public void run() {
		 try {
		  studentAnswer = log(b , n);
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
	
   public static int modellog(int b, int n ) { 

   if ( b == n ) return 1;
   return 1+ modellog(b,n/b); 
 }
  
   

  public static void main(String [ ] args) {
    boolean SUCCESS = false;
    b=10;
    n=100;
   try {
     // Fail on time out object
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
    if (studentAnswer == modellog(b , n)) SUCCESS = true;

    try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS) { 
   
      output.println("Well Done!");
      output.close();
     }
    else 
    {
     output.println("Try Again! Incorrect Base case or recursive call!");
     output.close();
    }
  
    }
      catch (IOException e) {
	e.printStackTrace();
    }

  }

  
