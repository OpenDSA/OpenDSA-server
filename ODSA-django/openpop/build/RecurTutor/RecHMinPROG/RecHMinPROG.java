/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 17:  determines the minimum element in an array of integers
import java.io.*;
import java.util.Random;


public class studentRecHMinPROG
{
    public static  long fTimeout=5;
    public static boolean fFinished= false;
    public static Throwable fThrown= null;
    public static int studentAnswer;
    public static int[] numbers = new int[5];
    
    public static void evaluate() throws Throwable {
	    Thread thread= new Thread() {
		@Override
		public void run() {
		 try {
		  studentAnswer = recursiveMin(numbers,0);
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
 
 
 public static  int modelrecursiveMin(int numbers[] , int startIndex)
{ 
  if(startIndex == numbers.length-1)
    return numbers[startIndex];
  else
    return Math.min(numbers[startIndex], modelrecursiveMin(numbers , startIndex+1));	
}
	  
  public static void main(String [ ] args) {
    boolean SUCCESS = false;
   
    // To test: generate a random array of length 10
    Random randNumGenerator = new Random();
  
    for (int i=0; i< numbers.length; i++)
    {
       numbers[i] = (randNumGenerator.nextInt(20)+1);
    }
  
    try {
     // Fail on time out object
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
    
    if (studentAnswer == modelrecursiveMin(numbers,0)) SUCCESS = true;

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

  
