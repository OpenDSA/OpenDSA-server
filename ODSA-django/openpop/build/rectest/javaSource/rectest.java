
/** Test program for recursion programming exercise.
Author: Sally Hamouda */

import java.io.*;
import java.util.Random;


public class studentrectest
{
 // The model answer of the largest number: the student is asked to write the base case
 public static int modellargest(int[] numbers, int index) {
   if(index==numbers.length-1)
   {
     return numbers[index];
   }
   else if(numbers[index] > numbers[index+1]) {
     numbers[index+1] = numbers[index];
   }
    return modellargest(numbers,index+1);
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
    int modelanswerlargest = largest(numbers, 0);    
   
    if (largest(numbers,0)  == modellargest(numbers,0)) SUCCESS = true;

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

  
