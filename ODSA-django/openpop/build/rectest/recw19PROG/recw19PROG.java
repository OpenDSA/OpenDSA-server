/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 19:  given stack without using any other data structures(or without extra memory). You cannot use any memory at all. All what you have to do is use recursion only to attain this. You don’t need to implement a function to push, pop or check if the stack is empty or not.

import java.io.*;
import java.util.Random;
import java.util.Stack;
import java.util.*;
import java.awt.*;

public class studentrecw19PROG
{
 
 public  static <T> boolean compareStacks(Stack<T> a, Stack<T> b) {
    if (a.isEmpty() != b.isEmpty()) return false; 
    if (a.isEmpty() && b.isEmpty()) return true; 
    T element_a = a.pop(); 
    T element_b = b.pop();
    try {
        if (((element_a==null) && (element_b!=null)) || (!element_a.equals(element_b)))
            return false;
        return compareStacks(a, b); 
    } finally { // restore elements
        a.push(element_a); 
        b.push(element_b);
    }
 }


 public static  void modelstackReversal(Stack<Integer> s)
   {
   if(s.size() == 0)  
    return; 
   int n = getLast(s);
   modelstackReversal(s);   
   s.push(n);
  }

	  
 public static void main(String [ ] args) {
  
   boolean SUCCESS = false;

    Stack lifo = new Stack();
        
    for (int i = 1; i <= 10; i++)
    {
      lifo.push ( new Integer(i) );
    }
    
    modelstackReversal(lifo);
    
    Stack lifo2 = new Stack(); 
    
    for (int i = 1; i <= 10; i++)
    {
     lifo2.push ( new Integer(i) );
    }

    stackReversal(lifo2);    
    
    if (compareStacks(lifo , lifo2)) SUCCESS = true;

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

  
