/** Source code example for "A Practical Introduction to Data
    Structures and Algorithm Analysis, 3rd Edition (Java)" 
    by Clifford A. Shaffer
    Copyright 2008-2011 by Clifford A. Shaffer
*/

/** Test program for various preorder traversals of a binary tree.
    This includes two implementations for preorder traversal,
    a traversal that counts the number of nodes in the tree,
    and a traversal that verifies that a given tree is a BST. */

import java.io.*;
import java.util.Random;
import java.lang.*;
import java.util.ArrayList;
import java.util.*;
import java.lang.Integer;

/* *** ODSATag: BinNode *** */
interface BinNode { // Binary tree node ADT
  // Get and set the element value
  Object element();
  void setElement(Object v);

  // return the children
  BinNode left();
  BinNode right();

  // return TRUE if a leaf node, FALSE otherwise
  boolean isLeaf();
 
}
/* *** ODSAendTag: BinNode *** */

 

// Binary tree node implementation: supports comparable objects
class BSTNode implements BinNode {
  private Comparable element; // Element for this node
  private BSTNode left;       // Pointer to left child
  private BSTNode right;      // Pointer to right child

  // Constructors
  BSTNode() {left = right = null; }
  BSTNode(Comparable val) { left = right = null; element = val; }
  BSTNode(Comparable val, BSTNode l, BSTNode r)
    { left = l; right = r; element = val; }

  // Get and set the element value
  public Comparable element() { return element; }
  public void setElement(Comparable v) { element = v; }
  public void setElement(Object v) { // We need this one to satisfy BinNode interface
    if (!(v instanceof Comparable))
      throw new ClassCastException("A Comparable object is required.");
    element = (Comparable)v;
  }

  // Get and set the left child
  public BSTNode left() { return left; }
  public void setLeft(BSTNode p) { left = p; }

  // Get and set the right child
  public BSTNode right() { return right; }
  public void setRight(BSTNode p) { right = p; }

  // return TRUE if a leaf node, FALSE otherwise
  public boolean isLeaf() { return (left == null) && (right == null); }


}



public class studentBTpathsumPROG
{

 public static  long fTimeout=1;
    public static boolean fFinished= false;
    public static Throwable fThrown= null;
    public static  BinNode rtmember; 
    public static int summemeber;
    public static boolean studentAnswer;

    public static void evaluate() throws Throwable {
	    Thread thread= new Thread() {
		@Override
		public void run() {
		 try {
		  studentAnswer = BTpathsum(rtmember, summemeber);
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

 public static boolean modelbthasPathSum(BinNode rt , int sum) {
    if (rt == null)
      return (sum==0);
    else
    {
      int subsum= sum - (Integer)rt.element();
      return (modelbthasPathSum(rt.left(), subsum)|| modelbthasPathSum(rt.right(), subsum));
    }
  }

 
  public static void main(String [ ] args) {
 
   BSTNode root = null;
     
   root = new BSTNode(10);
   BSTNode leftChild = new BSTNode(15);
   BSTNode rightChild = new BSTNode(20);

   root.setLeft(leftChild); 
   root.setRight(rightChild);
  
  
   String   treeAsString = "  10\n"
                          +" / \\ \n"
                          +"15 20 \n ";
 
   boolean SUCCESS1 = false;
   boolean SUCCESS2 = false;


    boolean modelAnswer = false;
  
    boolean studentAnswer1 = true;
    boolean studentAnswer2 = true;
    int sum =0;
    
    int sum1= 25;
    int sum2= 5;
    
    
    try {
     // Fail on time out object
     rtmember = root;
     summemeber= sum1;

     evaluate();
    studentAnswer1 = studentAnswer;
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
//    studentAnswer1 = bthasPathSum(root, sum1);
    boolean modelAnswer1 = modelbthasPathSum(root, sum1);
    boolean modelAnswer2 = modelbthasPathSum(root, sum2);
    
    if (studentAnswer1== modelAnswer1) SUCCESS1 = true;
    else 
    {
		modelAnswer= modelAnswer1;
		studentAnswer= studentAnswer1;
		sum = sum1;
    }
   try {
     // Fail on time out object
     rtmember = root;
     summemeber= sum2;
     evaluate();
     studentAnswer2 = studentAnswer;
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }

    //studentAnswer2 = bthasPathSum(root, sum2);
    
    
    if (studentAnswer2== modelAnswer2) SUCCESS2 = true;
    else 
    {
		modelAnswer= modelAnswer2;
		studentAnswer= studentAnswer2;
		sum = sum2;
	}
	
	
    try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS1 && SUCCESS2) { 
   
      output.println("Well Done!");
      output.close();
     }
    else 
    { 
     output.println("Try Again! Your answer is not correct for all test cases. For example, if the given tree is:\n " + treeAsString + " and the sub-sum is " + sum + ", then your code returns:  " + studentAnswer+ ". The expected answer is: " + modelAnswer+".");
     output.close();
    }
  
    }
      catch (IOException e) {
	e.printStackTrace();
    }

  } 
