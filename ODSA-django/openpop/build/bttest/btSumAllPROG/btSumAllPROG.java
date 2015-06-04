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

public class studentbtSumAllPROG
{

    public static  long fTimeout=1;
    public static boolean fFinished= false;
    public static Throwable fThrown= null;
    public static  BinNode rtmember; 
    public static int studentAnswer;
    public static void evaluate() throws Throwable {
	    Thread thread= new Thread() {
		@Override
		public void run() {
		 try {
		  studentAnswer = btSumAll(rtmember);
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

 public static int modelbtSumAll(BinNode rt) {
    if (rt == null) return 0; 
     else return ((Integer)rt.element()) + modelbtSumAll(rt.left())+ modelbtSumAll(rt.right());
 }



 
 public static void writeResult(BinNode rt,boolean SUCCESS , String treeAsString , int modelAnswer, int studentAnswer ){
 try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS) { 
   
      output.println("Well Done!");
      output.close();
     }
    else 
    {
     output.println("Try Again! Your answer is not correct for all test cases. For example if the given tree is:\n " + treeAsString + ", your code returns:  " + studentAnswer+ " while the expected answer is: " + modelAnswer+"."); 
     output.close();
    }
  
    }
      catch (IOException e) {
	e.printStackTrace();
    }

 }
 
 public static boolean runTestCase(BinNode rt , String treeAsString)
 {  

   try {
     // Fail on time out
     rtmember = rt;
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
   boolean SUCCESS = false;
   
   int modelAnswer  = modelbtSumAll(rt);
  // int studentAnswer= btSumAll(rt);
   
   if (modelAnswer  ==  studentAnswer)
   { 
     SUCCESS = true;   
   }
  
   else  // This test case fail then will write the result and abort the function
   {
    SUCCESS = false;
    writeResult(rt , SUCCESS ,  treeAsString , modelAnswer, studentAnswer);
    
   }
  return SUCCESS;
 }
 


  public static void main(String [ ] args) {
 
 
  // We will have more than one test case
   String treeAsString = " empty ";
  //First test case ..empty tree
   BSTNode root = null;
   Comparable value = new Integer(15);
  
   if (runTestCase(root , treeAsString ) == false) return;
   ////// End of the first test case

   // Second test case
   root = new BSTNode(10);
   BSTNode leftChild = new BSTNode(15);
   BSTNode rightChild = new BSTNode(20);

   root.setLeft(leftChild); 
   root.setRight(rightChild);
   
   treeAsString = "  10\n"
                  +" / \\ \n"
                  +"15 20 \n ";
 
   if (runTestCase(root , treeAsString )== false) return;
   ////// End of the second test case


  //Third test case
  root= null;
  root = new BSTNode(5);
  leftChild = new BSTNode(15);
  rightChild = new BSTNode(15);

   root.setLeft(leftChild); 
   root.setRight(rightChild);
 
 treeAsString = "  5\n"
                  +" / \\ \n"
                  +"15 15 \n ";
 
  if (runTestCase(root , treeAsString ) == false) return;
 ///End of the third test case

  // If none the test cases failed then all of them are ok then sucess=true
  writeResult(root , true , treeAsString  , 0 , 0);


  } 
