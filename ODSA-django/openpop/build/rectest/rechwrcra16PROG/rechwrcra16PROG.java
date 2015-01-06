/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 16:  prints the binary equivalent of an integer N
import java.io.*;
import java.util.Random;


public class studentrechwrcra16PROG
{
 
 public static String modeldecibinary (int num)
  {
   if ( num < 2)
     return Integer.toString(num);
   else
      return modeldecibinary(num/2) + Integer.toString(num%2);
  }
	
     
	
  public static void main(String [ ] args) {
    boolean SUCCESS = false;
   
    Random randNumGenerator = new Random();
    
    int number=  randNumGenerator.nextInt(32);
    
	int number2=  randNumGenerator.nextInt(32);
	
    if (decibinary(number).equals(modeldecibinary(number)) && decibinary(number2).equals(modeldecibinary(number2)) ) SUCCESS = true;

    try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS) { 
   
      output.println("Well Done!");
      output.close();
     }
    else 
    {
     output.println("Try Again! Incorrect recursive call or action!");
     output.close();
    }
  
    }
      catch (IOException e) {
	e.printStackTrace();
    }

  }

  
