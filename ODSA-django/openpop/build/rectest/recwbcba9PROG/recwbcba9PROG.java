
/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 9: computes the GCD of x and y
import java.io.*;
import java.util.Random;


public class studentrecwbcba9PROG
{
 
 public static int modelGCD(int x, int y)
 {
 if ((x % y) == 0)
  {
   return y;
  }   
 else
 {
   return modelGCD (y, x % y);
 }
}
	
  public static void main(String [ ] args) {
    boolean SUCCESS = false;
    
    // To test: generate a random number
    Random randNumGenerator = new Random();
    int x=  randNumGenerator.nextInt(100)+1;
    int y=  randNumGenerator.nextInt(100)+1;

    if ( GCD(x,y) == modelGCD(x,y)) SUCCESS = true;

    try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS) { 
   
      output.println("Well Done!");
      output.close();
     }
    else 
    {
     output.println("Try Again! Incorrect base case or base case action!");
     output.close();
    }
  
    }
      catch (IOException e) {
	e.printStackTrace();
    }

  }

  
