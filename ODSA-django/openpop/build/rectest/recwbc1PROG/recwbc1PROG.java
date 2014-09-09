
/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 1: finds the largest number in the array named numbers.

import java.io.*;
import java.util.Random;


public class studentrecwbc1PROG
{
 
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

  
