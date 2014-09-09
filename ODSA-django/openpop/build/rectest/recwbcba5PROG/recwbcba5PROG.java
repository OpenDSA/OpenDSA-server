
/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 5: multiply two  numbers x and y. (Assume both values given are positive.)
import java.io.*;
import java.util.Random;


public class studentrecwbcba5PROG
{
 
 public static int modelmult(int x, int y) {

    if ( x == 1 )
    
      return y;

     else

     return modelmult(x-1, y) + y;
     }
 

  public static void main(String [ ] args) {
    boolean SUCCESS = false;
    
    // To test: generate a random number
    Random randNumGenerator = new Random();
    int x=  randNumGenerator.nextInt(100)+1;
    int y=  randNumGenerator.nextInt(100)+1;

    if ( mult(x,y) == modelmult(x,y)) SUCCESS = true;

    try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS) { 
   
      output.println("Well Done!");
      output.close();
     }
    else 
    {
     output.println("Try Again! Incorrect Base case condition or base case action!");
     output.close();
    }
  
    }
      catch (IOException e) {
	e.printStackTrace();
    }

  }

  
