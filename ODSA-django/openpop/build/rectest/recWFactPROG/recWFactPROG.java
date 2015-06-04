
/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 8: computes the factorial of n
import java.io.*;
import java.util.Random;


public class studentrecWFactPROG
{
 
 public static int modelfact(int n)
	  {
	
	   int result;
	
	   if(n==1)
	
	   return 1;
	
	  return modelfact(n-1) * n;
	
	 }
 

  public static void main(String [ ] args) {
    boolean SUCCESS = false;
    
    // To test: generate a random number
    Random randNumGenerator = new Random();
    int n=  randNumGenerator.nextInt(100)+1;


    if ( fact(n) == modelfact(n)) SUCCESS = true;

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

  
