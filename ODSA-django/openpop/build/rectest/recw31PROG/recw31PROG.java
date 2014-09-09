/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 31: Old merchants problem. Find out if a certain target weight can be measured or not

import java.io.*;
import java.util.Vector;

public class studentrecw31PROG
{

public static boolean modelRecIsMeasurable(int target, Vector<Integer> weights, int index)
{
		
if (target == 0)
{
return true;
}
if (index >= weights.size())
{
return false;
}
return modelRecIsMeasurable(target + weights.elementAt(index), weights, index +1)|| modelRecIsMeasurable(target, weights, index + 1)||modelRecIsMeasurable(target - weights.elementAt(index), weights,index+ 1);
		
}

 public static void main(String [ ] args) 
{
  
    boolean SUCCESS1 = false;
    boolean SUCCESS2 = false;

    Vector<Integer> vector = new Vector<Integer>(); 
    vector.add(1);
    vector.add(2);
    vector.add(3);

    if (RecIsMeasurable(5, vector, 0)== modelRecIsMeasurable(5, vector, 0)) SUCCESS1 = true;
    if (RecIsMeasurable(10, vector, 0)== modelRecIsMeasurable(10, vector, 0)) SUCCESS2 = true;
    try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS1 && SUCCESS2) { 
   
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

  
