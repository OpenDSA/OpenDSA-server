/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 15:  determines if an integer N is prime or not
import java.io.*;
import java.util.Random;


public class studentrechw2bc15PROG
{
 
 public static boolean modelPrime(int X,int Y)
{
   if ( Y == 1)
    return true;
  else if ( X%Y == 0)
    return false;	
   else
    return modelPrime(X,Y-1);
}
	
     
	
  public static void main(String [ ] args) {
    boolean SUCCESS1 = false;
    boolean SUCCESS2 = false;
    
    boolean SUCCESS = false;
    
    Random randNumGenerator = new Random();
    
    int number=  randNumGenerator.nextInt(100)+1;
	
    int number2=  randNumGenerator.nextInt(100)+1;
    
    if(Prime(number, number-1) == modelPrime(number , number-1))
        SUCCESS1 = true;
    
    if(Prime(number2, number2-1) == modelPrime(number2 , number2-1))
        SUCCESS2 = true;
        
    if (SUCCESS1 && SUCCESS2)
       SUCCESS = true;
           
    try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS) { 
   
      output.println("Well Done!");
      output.close();
     }
    else 
    {
     output.println("Try Again! Incorrect Base Case(s)");
     output.close();
    }
  
    }
      catch (IOException e) {
	e.printStackTrace();
    }

  }

  
