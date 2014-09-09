/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 24: outputs the minimal number of invocations of the operations +1 and ∗2 that are required to obtain Y from X. For Example: If the inputs 10 17, the output will be 7 (due to 7 invocations of +1). For the input 10 21, the output will be 2 (due to ∗2 and then +1).


import java.io.*;
import java.util.Random;

public class studentrecw24PROG
{

 public static  int modelminOps (int x, int y)
		
{
if (2*x > y)
   return y-x;
		
else if (y%2 == 1)
		
   return (modelminOps (x, y-1) + 1);
else
		
   return (modelminOps (x, y/2) + 1);
}


 public static void main(String [ ] args) 
{
  
    boolean SUCCESS = false;
   
    Random randNumGenerator = new Random();
    
    
    int x= randNumGenerator.nextInt(100);
    int y= randNumGenerator.nextInt(100);
    int temp= x;
    // x has to be greater than y by problem definition 
    if (x>y){
     x=y;
     y=temp;
    }

    if (minOps(x,y)== modelminOps(x,y)) SUCCESS = true;

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

  
