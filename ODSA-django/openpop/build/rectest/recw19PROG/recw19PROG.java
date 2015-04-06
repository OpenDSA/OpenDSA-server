/** Test program for recursion programming exercise.
Author: Sally Hamouda */

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
   int n = popBottom(s);
   modelstackReversal(s);   
   s.push(n);
  }

 
	  
 public static void main(String [ ] args) {
  
   boolean SUCCESS = false;

    Stack <Integer> lifo = new Stack <Integer> ();
    lifo.push(1);
    lifo.push(2);
    lifo.push(3);
    lifo.push(4);
    
    modelstackReversal(lifo);
    
    Stack <Integer> lifo2 = new Stack <Integer> ();
    lifo2.push(1);
    lifo2.push(2);
    lifo2.push(3);
    lifo2.push(4);
   
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

  
