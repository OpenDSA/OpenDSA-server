/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 17:  determines the minimum element in an array of integers
import java.io.*;
import java.util.Random;


public class studentrechwrc17PROG
{
 
 public static  int modelrecursiveMin(int numbers[] , int startIndex)
{ 
  if(startIndex+1 == numbers.length)
    return numbers[startIndex];
  else
    return Math.min(numbers[startIndex], modelrecursiveMin(numbers , startIndex+1));	
}
	  
  public static void main(String [ ] args) {
    boolean SUCCESS = false;
   
    // To test: generate a random array of length 10
    Random randNumGenerator = new Random();
    int[] numbers = new int[10];
    for (int i=0; i< numbers.length; i++)
    {
       numbers[i] = (randNumGenerator.nextInt(100)+1);
    }

    if (recursiveMin(numbers,0)==modelrecursiveMin(numbers,0)) SUCCESS = true;

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

  
