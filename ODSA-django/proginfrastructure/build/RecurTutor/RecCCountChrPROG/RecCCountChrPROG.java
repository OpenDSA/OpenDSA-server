/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 12: Counts the number of As in a given string::
import java.io.*;
import java.util.Random;


public class studentRecCCountChrPROG
{
    public static  long fTimeout=2;
    public static boolean fFinished= false;
    public static Throwable fThrown= null;
    public static int studentAnswer;
    public static String [] testStrings = new String[10];;
    public static int index;
    
    public static void evaluate() throws Throwable {
	    Thread thread= new Thread() {
		@Override
		public void run() {
		 try {
		  studentAnswer = countChr(testStrings[index]);
		  fFinished= true;
		 } 
          catch (Throwable e) {
		  fThrown= e;
		 }
	       }
	 };
	
        thread.start();
		thread.join(fTimeout);
		if (fFinished)
			return;
		if (fThrown != null)
			throw fThrown;
		Exception exception= new Exception(String.format(
				"test timed out after %d milliseconds", fTimeout));
		exception.setStackTrace(thread.getStackTrace());
		throw exception;
	
	}
 
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
    
	testStrings[0] = "AbAAcdfe";
	testStrings[1] = "Abc";
    testStrings[2] = "AAAAAA";
    testStrings[3] = "A";
    testStrings[4] = "AbAAAAusAAwjhsjAhs";
    testStrings[5] = "AvA";
    testStrings[6] = "sAAA";
    testStrings[7] = "ymAnmAs";
    testStrings[8] = "qiwkwAAAA";
    testStrings[9] = "1o2unAAAs";
    
    Random randNumGenerator = new Random();
    index=  randNumGenerator.nextInt(9);

	try {
     // Fail on time out object
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
    
    if ( studentAnswer ==  modelcountChr(testStrings[index]) ) SUCCESS = true;

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

  
