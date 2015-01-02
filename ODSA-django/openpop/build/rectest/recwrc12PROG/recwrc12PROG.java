/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 12: Counts the number of As in a given string::
import java.io.*;
import java.util.Random;


public class studentrecwrc12PROG
{
 
 public static int modelcountChr(String str ) {
	
	   if (str.length() == 0) {
	 
	   return 0;
	  }
	  
	   int count = 0;
	 
	   if (str.substring(0, 1).equals("A")) {
	 
	    count = 1;
	   }
	 
	   return count +  modelcountChr(str.substring(1));
	
	  }
	

     
	
  public static void main(String [ ] args) {
    boolean SUCCESS = false;
    
    String [] testStrings = {"abcdfe", "abc" , "a" , "" , "abuswjhsjahs" , "av", "s" , "12ymanmas" , "qiwkw" , "1o2unas"};
	
    Random randNumGenerator = new Random();
    int index=  randNumGenerator.nextInt(9);
	
    if ( countChr(testStrings[index]) == modelcountChr(testStrings[index]) ) SUCCESS = true;

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

  
