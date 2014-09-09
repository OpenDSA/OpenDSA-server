/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 13: takes a non-negative integer and returns the sum of its digits. For example, sumOfDigits(1234) returns 1+2+3+4 =10
import java.io.*;
import java.util.Random;


public class studentrecwrc13PROG
{
 
 public static int modelsumOfDigits(int number)
 {  
    if(number/10 == 0)
      return number;    
    return number%10 + modelsumOfDigits(number/10);
 }

     
	
  public static void main(String [ ] args) {
    boolean SUCCESS = false;
    
   
    Random randNumGenerator = new Random();
    int number=  randNumGenerator.nextInt(1000000);
	
    if (sumOfDigits(number) ==modelsumOfDigits(number)) SUCCESS = true;

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

  
