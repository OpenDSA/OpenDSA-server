/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 27: modifies an array of Strings to remove duplicates.


import java.io.*;
import java.util.Random;
import java.util.ArrayList;

public class studentRecWRemoveDupPROG
{
	public static  long fTimeout= 10;
    public static boolean fFinished= false;
    public static Throwable fThrown= null;
    public static ArrayList<String> studentList = new ArrayList<String>();
        
    public static void evaluate() throws Throwable {
	    Thread thread= new Thread() {
		@Override
		public void run() {
		 try {
		  removeDuplicates(studentList , 0);
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

 public static void modelremoveDuplicates(ArrayList<String> list, int counter)
 {
  if(counter < list.size()){
   if(list.contains(list.get(counter))){
    if(list.lastIndexOf(list.get(counter))!=counter)
     {
	list.remove(list.lastIndexOf(list.get(counter)));
	counter--;
      }
     }
     modelremoveDuplicates(list, ++counter);
    }
 }

 public static void main(String [ ] args) 
{
  
    boolean SUCCESS = false;
    ArrayList<String> modelList = new ArrayList<String>();
    modelList.add("one");
    modelList.add("one");
    modelList.add("two");
    modelList.add("two");
    modelList.add("three");
    modelList.add("three");
    
    modelremoveDuplicates(modelList , 0);
 
    studentList.add("one");
    studentList.add("one");
    studentList.add("two");
    studentList.add("two");
    studentList.add("three");
    studentList.add("three");
    
    try {
     // Fail on time out object
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
    
    
    if (studentList.equals(modelList)) SUCCESS = true;

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

  
