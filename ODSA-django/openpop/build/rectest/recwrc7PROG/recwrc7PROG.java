
/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 7: given 2 numbers, will find the sum of all the integers between them
import java.io.*;
import java.util.Random;


public class studentrecwrc7PROG
{

 public static int modelSum(int a, int b)
{
 if (a == b)

  return a;

else

  return modelSum(a,b-1) + b;
}
 

  public static void main(String [ ] args) {
    boolean SUCCESS = false;
    
    // To test: generate a random number
    Random randNumGenerator = new Random();
    int x=  randNumGenerator.nextInt(100)+1;
    int y=  randNumGenerator.nextInt(100)+1;

    if ( Sum(x,y) == modelSum(x,y)) SUCCESS = true;

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

  
