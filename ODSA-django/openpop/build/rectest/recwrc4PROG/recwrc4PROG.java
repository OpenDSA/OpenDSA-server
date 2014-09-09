
/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 4:sum of all positive odd numbers less than or equal to n
import java.io.*;
import java.util.Random;


public class studentrecwrc4PROG
{

 public static int modelOddRecursive(int n) {
  if(n<=0)
  {
    return 0;    
  }
  if(n%2 != 0)
  {
    return (n+ modelOddRecursive(n-1));
  }
  else
  {
    return modelOddRecursive(n-1);
  }
      
}
 

  public static void main(String [ ] args) {
    boolean SUCCESS = false;
    
    // To test: generate a random number
    Random randNumGenerator = new Random();
    int n=  randNumGenerator.nextInt(100)+1;
   
    if ( addodd(n) == modelOddRecursive(n)) SUCCESS = true;

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

  
