/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 30: Stack Sorting

import java.io.*;
import java.util.Stack;

public class studentrecwprog30
{

public static void modelstacksort(Stack S1, Stack S2)
{
  int temp;
  while(! S1.empty())
  { temp= (Integer) S1.pop();
    while(! S2.empty() && (Integer) S2.peek() < temp) 
    {
      S1.push(S2.pop());
    }
   S2.push(temp);
  		
  }
}

 public static void main(String [ ] args) 
{
  
    boolean SUCCESS = false;

    Stack S1 = new Stack();
    Stack S2 = new Stack();
    Stack A = new Stack();
    Stack B = new Stack();
    
    S1.push(new Integer(2));
    S1.push(new Integer(4));
    S1.push(new Integer(1));

    A.push(new Integer(2));
    A.push(new Integer(4));
    A.push(new Integer(1));

    modelstacksort(S1, S2);
    stacksort(A, B);
    
    if (S2.equals(B)) SUCCESS = true;
    
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

  
