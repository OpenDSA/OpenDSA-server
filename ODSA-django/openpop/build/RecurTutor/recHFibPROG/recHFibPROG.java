/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 14:  computes the Fibonacci of a given number
import java.io.*;
import java.util.Random;


public class studentrecHFibPROG
{
   public static  long fTimeout=5;
    public static boolean fFinished= false;
    public static Throwable fThrown= null;
    public static long studentAnswer;
    public static int number;
    
    public static void evaluate() throws Throwable {
	    Thread thread= new Thread() {
		@Override
		public void run() {
		 try {
		  studentAnswer = Fibonacci(number);
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
	
	
 public static long modelFibonacci(int n)
  {
   if (n > 2)  
     return modelFibonacci(n-1) + modelFibonacci(n-2);
   else
     return 1;   
 } 
     
	
  public static void main(String [ ] args) {
    boolean SUCCESS = false;
    
   
    Random randNumGenerator = new Random();
    number=  randNumGenerator.nextInt(8) + 2;
	//int number2 = randNumGenerator.nextInt(30);
	 try {
     // Fail on time out object
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
    
    if ( studentAnswer == modelFibonacci(number)) SUCCESS = true;

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

  
