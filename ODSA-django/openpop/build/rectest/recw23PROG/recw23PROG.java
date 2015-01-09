/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 23: returns the given string in a reverse order.


import java.io.*;
import java.util.Random;

public class studentrecw23PROG
{
private static final String CHAR_LIST =
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890";
private static final int RANDOM_STRING_LENGTH = 10;
     
    
//This method generates random string
public static String generateRandomString(){
 Random randNumGenerator = new Random();
 StringBuffer randStr = new StringBuffer();
 for(int i=0; i<RANDOM_STRING_LENGTH; i++){
   int number =   randNumGenerator.nextInt(60);
   char ch = CHAR_LIST.charAt(number);
   randStr.append(ch);
  }
  return randStr.toString();
}
     
 
 public static  String modelReverseStringRecursive (String str)
{
 if (str.length() == 0)
  {
    return "";
  }
  return modelReverseStringRecursive(str.substring(1)) + str.charAt(0);
}
 public static void main(String [ ] args) 
{
  
    boolean SUCCESS = false;
   
    String str = generateRandomString();
 
    if (reverseStringRecursive(str).equals(modelReverseStringRecursive(str))) SUCCESS = true;

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

  
