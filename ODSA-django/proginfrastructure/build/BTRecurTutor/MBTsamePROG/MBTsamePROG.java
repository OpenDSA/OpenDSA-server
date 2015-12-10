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



public class studentMBTsamePROG
{
    public static  long fTimeout=4;
    public static boolean fFinished= false;
    public static Throwable fThrown= null;
    public static  BSTNode rtmember; 
    public static  BSTNode rtmember2; 
    public static boolean studentAnswer;
    public static void evaluate() throws Throwable {
	    Thread thread= new Thread() {
		@Override
		public void run() {
		 try {
		  studentAnswer = MBTsame(rtmember , rtmember2);;
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
 
 public static boolean modelmbtSame(BSTNode a, BSTNode b) {
    // check for reference equality and nulls
    if (a==b) return true; // note this picks up case of two nulls
    if (a==null) return false;
    if (b==null) return false;

    // check for data inequality
    if ((Integer)a.element().compareTo((Integer)b.element()) !=0) {
        if (((Integer)a.element()==null)||((Integer)b.element()==null)) return false;
        if ((((Integer)a.element()).compareTo((Integer)b.element())) !=0) return false;
    }

    // recursively check branches
    if (!modelmbtSame(a.left(),b.left())) return false;
    if (!modelmbtSame(a.right(),b.right())) return false;

    // we've eliminated all possibilities for non-equality, so trees must be equal
    return true;
}

 public static void writeResult(BSTNode rt, BSTNode rt2 , boolean SUCCESS, String tree1AsString , String tree2AsString, boolean modelAnswer, boolean studentAnswer ){
 try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS) { 
   
      output.println("Well Done!");
      output.close();
     }
    else 
    {
    output.println("Try Again! Your answer is not correct for all test cases. For example, if the first tree is:\n " + tree1AsString + "\n and the second tree is:\n "+ tree2AsString + " \n, then your code returns:  " + studentAnswer+ ". The expected answer is: " + modelAnswer+".");  
    output.close();
    }
  
    }
      catch (IOException e) {
	e.printStackTrace();
    }

 }
 
 public static boolean runTestCase(BSTNode rt, BSTNode rt2, String tree1AsString , String tree2AsString)
 { 
     try {
     // Fail on time out object
     rtmember = rt;
     rtmember2 = rt2;
     evaluate();
    } 
    catch(Throwable t) {	
     throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
   boolean SUCCESS = false;
   boolean modelAnswer  = modelmbtSame(rt, rt2);
   //boolean studentAnswer= btIdenticalTrees(rt , rt2); 
   
   if (modelAnswer  ==  studentAnswer)  
   { 
     SUCCESS = true;   
   }
  
   else  // This test case fail then will write the result and abort the function
   {
    SUCCESS = false;
    writeResult(rt , rt2, SUCCESS ,  tree1AsString ,  tree2AsString, modelAnswer, studentAnswer);
    
   }
  return SUCCESS;
 }
 


  public static void main(String [ ] args) {
 
  // We will have more than one test case
   
  //First test case ..empty tree
   BSTNode root = null;
   BSTNode root2 = null;
   
   String tree1AsString = " empty ";
   
   String tree2AsString = " empty ";
   
   if (runTestCase(root, root2 , tree1AsString , tree2AsString) == false) return;
   ////// End of the first test case

   // Second test case -- the same tree
   root = new BSTNode(10);
   root2 = new BSTNode(10);

   BSTNode leftChild = new BSTNode(15);
   BSTNode rightChild = new BSTNode(20);

   BSTNode leftChild2 = new BSTNode(15);
   BSTNode rightChild2 = new BSTNode(20);

   root.setLeft(leftChild); 
   root.setRight(rightChild);
  
   root2.setLeft(leftChild2); 
   root2.setRight(rightChild2);
   
   tree1AsString = "  10\n"
                  +" / \\ \n"
                  +"15 20 \n ";

   tree2AsString = "  10\n"
                  +" / \\ \n"
                  +"15 20 \n ";

   if (runTestCase(root, root2 , tree1AsString , tree2AsString)== false) return;
   ////// End of the second test case


  //Third test case ---Different trees 
   root = new BSTNode(30);
   root2 = new BSTNode(10);

   leftChild = new BSTNode(5);
   rightChild = new BSTNode(40);
   
   BSTNode leftChild3 = new BSTNode(10);
   BSTNode rightChild3 = new BSTNode(20);

   
   leftChild2 = new BSTNode(15);
   rightChild2 = new BSTNode(20);

   root.setLeft(leftChild); 
   root.setRight(rightChild);
   
   leftChild.setLeft(leftChild3); 
   leftChild.setRight(rightChild3);
  
   root2.setLeft(leftChild2); 
   root2.setRight(rightChild2);
   
   tree1AsString = "  30\n"
                  +" / \\ \n"
                  +"5 40 \n "
                  +"/ \\ \n"
                  +"10 20 \n ";

   tree2AsString = "  10\n"
                  +" / \\ \n"
                  +"15 20 \n ";

   if (runTestCase(root, root2 , tree1AsString , tree2AsString)== false) return;

  // If none the test cases failed then all of them are ok then sucess=true
 writeResult(root , root2, true , tree1AsString , tree2AsString , true , true);

  } 
