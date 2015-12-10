/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 31: Old merchants problem. Find out if a certain target weight can be measured or not

import java.io.*;
import java.util.Vector;

public class studentrecWIsMeasurblPROG
{
    public static  long fTimeout= 10;
    public static boolean fFinished= false;
    public static Throwable fThrown= null;
    public static boolean studentAnswer;
    public static Vector<Integer> vector = new Vector<Integer>(); 
    public static int weight;
            
    public static void evaluate() throws Throwable {
	    Thread thread= new Thread() {
		@Override
		public void run() {
		 try {
		  studentAnswer = RecIsMeasurable(weight, vector, 0) ;
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
	
	 
public static boolean modelRecIsMeasurable(int target, Vector<Integer> weights, int index)
{
		
if (target == 0)
{
return true;
}
if (index >= weights.size())
{
return false;
}
return modelRecIsMeasurable(target + weights.elementAt(index), weights, index +1)|| modelRecIsMeasurable(target, weights, index + 1)||modelRecIsMeasurable(target - weights.elementAt(index), weights,index+ 1);
		
}

 public static void main(String [ ] args) 
{
  
    boolean SUCCESS1 = false;
    boolean SUCCESS2 = false;

    
    vector.add(1);
    vector.add(2);
    vector.add(3);
    
    weight = 5;

    try {
     // Fail on time out object
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
    
    if (studentAnswer == modelRecIsMeasurable(weight, vector, 0)) SUCCESS1 = true;
    
    weight = 10;
    try {
     // Fail on time out object
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
    
    if (studentAnswer == modelRecIsMeasurable(weight, vector, 0)) SUCCESS2 = true;
    
    try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS1 && SUCCESS2) { 
   
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

  
