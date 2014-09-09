
/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 6: computes the value of y to the x power
import java.io.*;
import java.util.Random;


public class studentrecwrc6PROG
{
 // The model answer of the largest number: the student is asked to write the base case
 public static int modelpower(int x, int y) {
  if ( x == 1 )

   return y;

  else

   return power(x-1, y) * y;
}
 

  public static void main(String [ ] args) {
    boolean SUCCESS = false;
    
    // To test: generate a random number
    Random randNumGenerator = new Random();
    int x=  randNumGenerator.nextInt(100)+1;
    int y=  randNumGenerator.nextInt(100)+1;

    if ( power(x,y) == modelpower(x,y)) SUCCESS = true;

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

  
