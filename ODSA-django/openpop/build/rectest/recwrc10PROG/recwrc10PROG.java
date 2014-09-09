
/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 10: complete the mysrtrey function
import java.io.*;
import java.util.Random;


public class studentrecwrc10PROG
{
 
 public static int modelmystery(int k) 
 {

  if (k <= 0) {

   return 0;
 }

 else {
 
  return k + mystery(k - 1);

  }

 }
	
  public static void main(String [ ] args) {
    boolean SUCCESS = false;
    
    // To test: generate a random number
    Random randNumGenerator = new Random();
    int x=  randNumGenerator.nextInt(100)+1;
   

    if ( mystery(x) == modelmystery(x)) SUCCESS = true;

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

  
