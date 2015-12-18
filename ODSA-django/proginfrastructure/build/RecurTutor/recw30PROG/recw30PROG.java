/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 30: Stack Sorting

import java.io.*;
import java.util.Random;

interface Stack { // Stack class ADT

  // Reinitialize the stack.
  void clear();

  // Push "it" onto the top of the stack
  boolean push(Object it);

  // Remove and return the element at the top of the stack
  Object pop();

  // Return a copy of the top element
  Object topValue();

  // Return the number of elements in the stack
  int length();
}


// Array-based stack implementation
/* *** ODSATag: AStack1 *** */
class AStack implements Stack {
  public static final int defaultSize = 10;
  public int maxSize;            // Maximum size of stack
  public int top;                // Index for top Object
  public Object stackArray[];    // Array holding stack

  // Constructors
  AStack(int size) {
    maxSize = size;
    top = 0; 
    stackArray = new Object[size]; // Create stackArray
  }
  AStack() { this(defaultSize); }
/* *** ODSAendTag: AStack1 *** */


 public void clear() { top = 0; }       // Reinitialize stack

// Push "it" onto stack
/* *** ODSATag: AStackPush *** */
 public boolean push(Object it) {
    if (top >= maxSize) return false;
    stackArray[top++] = it;
    return true;
  }
/* *** ODSAendTag: AStackPush *** */

// Remove and return top element
/* *** ODSATag: AStackPop *** */
  public Object pop() {               
    if (top == 0) return null;
    return stackArray[--top];
  }
/* *** ODSAendTag: AStackPop *** */

  public Object topValue() {             // Return top element
    if (top == 0) return null;
    return stackArray[top-1];
  }

  public int length() { return top; }    // Return stack size
}
/* *** ODSAendTag: AStack2 *** */
public class studentrecw30PROG
{

public static void modelstacksort(Stack S1, Stack S2)
{
  int temp;
  while(S1.length()>0)
  { temp= (Integer) S1.pop();
    while(S2.length()>0 && (Integer)S2.topValue() < temp) 
    {
      S1.push(S2.pop());
    }
   S2.push(temp);
  		
  }
  while (S1.length()>0 && (Integer)S1.topValue() < (Integer) S2.topValue())
  {
    S2.push(S1.pop());
  }
}
public static String mytoString(AStack s) {
    StringBuffer out = new StringBuffer(s.top * 4);
    for (int i= s.top-1; i>=0; i--) {
      out.append(s.stackArray[i]);
      out.append(" ");
    }
    return out.toString();
}

 public static void main(String [ ] args) 
{
  
    boolean SUCCESS = false;

    AStack S1 = new AStack();
    AStack S2 = new AStack();
    AStack A = new  AStack();
    AStack B = new  AStack();
    
    Random randNumGenerator = new Random();
    int[] numbers = new int[5];
    for (int i=0; i< numbers.length; i++)
    {
       numbers[i] = (randNumGenerator.nextInt(100)+1);
    }
    
    for (int i=0; i< numbers.length; i++)
    {
        S1.push(new Integer( numbers[i]));
        A.push(new Integer( numbers[i]));
    }

    modelstacksort(S1, S2);
    stacksort(A, B);

    String S2Str= mytoString(S2);
    String BStr= mytoString(B);

    if (S2Str.equals(BStr)) SUCCESS = true;
    
    try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS) { 
   
      output.println("Well Done!");
      output.close();
     }
    else 
    {
     output.println("Try Again! Incorrect Answer! \nFor the following stack:\n" + mytoString(A) +"\nExpected Answer is: "+ S2Str +"\nBut your Answer is: " + BStr );
     output.close();
    }
  
    }
      catch (IOException e) {
	e.printStackTrace();
    }

  }

  
