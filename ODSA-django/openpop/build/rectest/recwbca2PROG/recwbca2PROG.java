
/** Test program for recursion programming exercise.
Author: Sally Hamouda */

//Exercise 2: Concatenate the values in an array named list and return it in one String. The values must be in the order of increasing subscript and seprated with a space.
import java.io.*;
import java.util.Random;



public class studentrecwbca2PROG
{

   private static final String ALPHA_NUM = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
   
  // The model answer of the print : the student is asked to write the base case action
   public static String modelprint(String[] list, int index) { 
       if (index < list.length) 
         return list[index] + " "+ modelprint(list, index + 1) ;
                        
      return "";   
 }
  
   /*public static String getAlphaNumeric(int len) {
    StringBuffer sb = new StringBuffer(len);
    for (int i = 0; i < len; i++) {
     int ndx = (int) (Math.random() * ALPHA_NUM.length());
     sb.append(ALPHA_NUM.charAt(ndx));
    }
    return sb.toString();
   }
  */

  public static void main(String [ ] args) {
    boolean SUCCESS = false;
    
    // To test: generate a random array string of length 10
    //String [] array = new String[10];
    //for (int i=0 ; i<10 ; i++)
   // {
    // array[i]= getAlphaNumeric(5);
   // }
    // We need to redirect the  stream.out to a string
    String [] array = {"Cheese", "Mushrooms", "Black Olives","Green Pepper"};

    //OutputStream out = new ByteArrayOutputStream();
    //System.setOut(new PrintStream(out));
    //recursiveprint(array , 0);
    //String sysout_content = out.toString();
    //System.out.flush();
    //modelprint(array, 0);
    //String sysout_content2 = out.toString();
   
    if (recursiveprint(array , 0).equals(modelprint(array, 0))) SUCCESS = true;

    try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS) { 
   
      output.println("Well Done!");
      output.close();
     }
    else 
    {
     output.println("Try Again! Incorrect Base case action!");
     output.close();
    }
  
    }
      catch (IOException e) {
	e.printStackTrace();
    }

  }

  
