/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 14:  computes the Fibonacci of a given number
import java.io.*;
import java.util.Random;


public class studentrechwrc14PROG
{
 
 public static long modelFibonacci(int n)
  {
   if (n > 2)  
     return modelFibonacci(n-1) + modelFibonacci(n-2);
   else
     return 1;   
 } 
     
	
  public static void main(String [ ] args) {
    boolean SUCCESS = false;
    
   
    Random randNumGenerator = new Random();
    int number=  randNumGenerator.nextInt(30);
	int number2 = randNumGenerator.nextInt(30);
    if ((Fibonacci(number) == modelFibonacci(number)) &&  (Fibonacci(number2) == modelFibonacci(number2)) ) SUCCESS = true;

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

  
