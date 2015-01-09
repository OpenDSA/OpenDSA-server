/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 26: this function counts the number of different ways to reach a basketball score. Example: For the input 3, the output will be 4, since there are 4 different	ways to accumulate 3: 1+1+1, 1+2, 2+1, 3.


import java.io.*;
import java.util.Random;

public class studentrecw26PROG
{

 public static  int modelnoOfPath (int n)
		
 {
 if (n==1)
  return 1;
 if (n==2)
  return 2;
 if (n==3)
  return 4;
		
 return modelnoOfPath(n-1) + modelnoOfPath(n-2) + modelnoOfPath(n-3);
		
}

 public static void main(String [ ] args) 
{
  
    boolean SUCCESS = false;
   
    Random randNumGenerator = new Random();
    
    int n= randNumGenerator.nextInt(20);
    
    int anothern= randNumGenerator.nextInt(20);
   
    if ((numOfPaths(n)== modelnoOfPath(n)) && (numOfPaths(anothern)== modelnoOfPath(anothern)))SUCCESS = true;

    try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS) { 
   
      output.println("Well Done!");
      output.close();
     }
    else 
    {
     output.println("Try Again! Incorrect answer!");
     output.close();
    }
  
    }
      catch (IOException e) {
	e.printStackTrace();
    }

  }

  
