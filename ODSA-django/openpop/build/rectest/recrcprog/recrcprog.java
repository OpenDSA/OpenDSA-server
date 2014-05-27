
/** Test program for recursion programming exercise.
Author: Sally Hamouda */

import java.io.*;
import java.util.Random;


public class studentrecrcprog
{
 // The model answer of the largest number: the student is asked to write the base case
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
    int n=  randNumGenerator.nextInt(100)+1;
   
    if ( addodd(n) == modelOddRecursive(n)) SUCCESS = true;

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

  
