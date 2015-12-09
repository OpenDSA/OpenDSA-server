
/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 4:sum of all positive odd numbers less than or equal to n
import java.io.*;
import java.util.Random;


public class studentRecCAddoddPROG
{
    public static  long fTimeout=1;
    public static boolean fFinished= false;
    public static Throwable fThrown= null;
    public static int studentAnswer;
    public static int n;
    
    public static void evaluate() throws Throwable {
	    Thread thread= new Thread() {
		@Override
		public void run() {
		 try {
		  studentAnswer = addodd(n);
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
	
 public static int modelOddRecursive(int n) {
  if(n<=0)
  {
    return 0;    
  }
  if(n%2 != 0)
  {
    return (n+ modelOddRecursive(n-1));
  }
  else
  {
    return modelOddRecursive(n-1);
  }
      
}
 

  public static void main(String [ ] args) {
    boolean SUCCESS = false;
    
    // To test: generate a random number
    Random randNumGenerator = new Random();
    n=  randNumGenerator.nextInt(100)+1;
    try {
     // Fail on time out object
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
    
    if ( studentAnswer == modelOddRecursive(n)) SUCCESS = true;

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

  
