/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 20:  recursive function which takes a row and a column and finds the value at that position in the Pascal's triangle. 

import java.io.*;
import java.util.Random;


public class studentrecw20PROG
{
 
 public static  int  modelpascal(int row, int column)
{
   if ((row+1)==1 || (column+1)==1 || row==column)
     return 1;
   else
     return modelpascal(row-1, column-1) + modelpascal(row-1, column);	
}
	  
 public static void main(String [ ] args) {
  
    boolean SUCCESS = false;

    Random randNumGenerator = new Random();
    
    int row = randNumGenerator.nextInt(10)+1;
    int column = randNumGenerator.nextInt(10)+1;
    
    
    if (pascal(row, column) == modelpascal(row, column)) SUCCESS = true;

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

  
