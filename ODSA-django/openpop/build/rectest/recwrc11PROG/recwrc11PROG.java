
/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 11: counts the number of digits in an integer
import java.io.*;
import java.util.Random;


public class studentrecwrc11PROG
{
 
 public static int modelGetDigits(int number, int digits)
 {
	if (number < 10)
	  return digits;
	  
	return modelGetDigits(number/ 10, ++digits);
 }

  
     
	
  public static void main(String [ ] args) {
    boolean SUCCESS = false;
    
    // To test: generate a random number
    Random randNumGenerator = new Random();
    int number=  randNumGenerator.nextInt(100)+1;

    if ( getDigits(number,1) == modelGetDigits(number,1)) SUCCESS = true;

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

  
