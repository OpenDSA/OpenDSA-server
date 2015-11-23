/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 20:  recursive function which takes a row and a column and finds the value at that position in the Pascal's triangle. 

import java.io.*;
import java.util.Random;


public class studentRecWPascalPROG
{
    public static  long fTimeout= 10;
    public static boolean fFinished= false;
    public static Throwable fThrown= null;
    public static int studentAnswer;
    public static int row;
    public static int column;
    
            
    public static void evaluate() throws Throwable {
	    Thread thread= new Thread() {
		@Override
		public void run() {
		 try {
		  studentAnswer = pascal(row, column);
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
	 
 public static  int  modelpascal(int row, int column)
{
   if ((row+1)==1 || (column+1)==1 || row==column)
     return 1;
   else
     return modelpascal(row-1, column-1) + modelpascal(row-1, column);	
}
	  
 public static void main(String [ ] args) {
  
    boolean SUCCESS = false;

    Random randNumGenerator = new Random();
    
    row = randNumGenerator.nextInt(10)+1;
    column = randNumGenerator.nextInt(10)+1;
    
    
    try {
     // Fail on time out object
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
    
    if (studentAnswer == modelpascal(row, column))  SUCCESS = true;

    row = randNumGenerator.nextInt(10)+1;
    column = randNumGenerator.nextInt(10)+1;
    SUCCESS = false;
    
    try {
     // Fail on time out object
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }

    if (studentAnswer == modelpascal(row, column))  SUCCESS = true;
    
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

  
