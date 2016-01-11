
/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 1: finds the largest number in the array named numbers.

import java.io.*;
import java.util.Random;


public class studentRecCLargestPROG
{
 
    public static  long fTimeout=1;
    public static boolean fFinished= false;
    public static Throwable fThrown= null;
    public static int studentAnswer;
    public static int[] numbers;
    public static void evaluate() throws Throwable {
	    Thread thread= new Thread() {
		@Override
		public void run() {
		 try {
		  studentAnswer = largest(numbers,0);
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

 
 
 public static int modellargest(int[] numbers, int index) {
   if(index==numbers.length-1)
   {
     return numbers[index];
   }
   else if(numbers[index] > numbers[index+1]) {
     numbers[index+1] = numbers[index];
   }
    return modellargest(numbers,index+1);
 } 
 

  public static void main(String [ ] args) {
	  
	 // To test: generate a random array of length 10
    Random randNumGenerator = new Random();
    numbers = new int[10];
    for (int i=0; i< numbers.length; i++)
    {
       numbers[i] = (randNumGenerator.nextInt(100)+1);
    }
      
	 try {
     // Fail on time out object
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
    
    boolean SUCCESS = false;
    
    
   
    if (studentAnswer  == modellargest(numbers,0)) SUCCESS = true;

    try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS) { 
   
      output.println("Well Done!");
      output.close();
     }
    else 
    {
     output.println("Try Again! Incorrect Base case!");
     output.close();
    }
  
    }
      catch (IOException e) {
	e.printStackTrace();
    }

  }

  
