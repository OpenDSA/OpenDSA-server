/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 21:  takes as its argument the height of a pyramid	of cannonballs and returns the number of cannonballs it contains based on the height of the stack

import java.io.*;
import java.util.Random;


public class studentrecw21PROG
{
 
 public static  int  modelCannonball(int height)
{
  if (height == 0)		
  {
   return 0;
  }
  else
  {
   return (height * height + modelCannonball(height - 1));
  }
}
	  
 public static void main(String [ ] args) 
{
  
    boolean SUCCESS = false;

    Random randNumGenerator = new Random();
    
   
    int height = randNumGenerator.nextInt(30)+1;
    
    
    if (Cannonball(height) == modelCannonball(height)) SUCCESS = true;

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

  
