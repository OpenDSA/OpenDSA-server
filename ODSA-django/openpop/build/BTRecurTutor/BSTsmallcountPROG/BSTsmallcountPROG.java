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



public class studentBSTsmallcountPROG
{
    public static  long fTimeout=4;
    public static boolean fFinished= false;
    public static Throwable fThrown= null;
    public static  BinNode rtmember; 
    public static int keymember;
    public static int studentAnswer;
    public static void evaluate() throws Throwable {
	    Thread thread= new Thread() {
		@Override
		public void run() {
		 try {
		  studentAnswer = BSTsmallcount(rtmember, keymember);
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

 public static int  modelbstsmallCount(BinNode root , int key) {
	   
    if(root==null)
      return 0;
    
    if((Integer)root.element() < key)
      return 1+ modelbstsmallCount(root.left(), key) + modelbstsmallCount( root.right(), key);
      
    else return modelbstsmallCount(root.left(), key);
 }



  public static void writeResult(BinNode rt, boolean SUCCESS, int key, String treeAsString ,int modelAnswer, int studentAnswer ){
 try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS) { 
      output.println("Well Done!");
      output.close();
     }
    else 
    {
     output.println("Try Again! Your answer is not correct for all test cases. For example, if the given tree is:\n " + treeAsString + " and the key is "+key+" , then your code returns: " + studentAnswer+ ".The expected answer is: " + modelAnswer);  
     output.close();
    }
  
    }
      catch (IOException e) {
	e.printStackTrace();
    }

 }
 
 public static boolean runTestCase(BinNode rt,  int key,String treeAsString)
 { 
   try {
     // Fail on time out object
     rtmember = rt;
     keymember = key;
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
   boolean SUCCESS = false; 
   int modelAnswer = modelbstsmallCount(rt , key)  ;
   //int studentAnswer = bstsmallCount(rt , key); 
   if (modelAnswer   ==  studentAnswer) 
   { 
     SUCCESS = true;   
   }
  
   else  // This test case fail then will write the result and abort the function
   {
    SUCCESS = false;
    writeResult(rt , SUCCESS ,  key,treeAsString, modelAnswer, studentAnswer);
    
   }
  return SUCCESS;
 }
 
  public static void main(String [ ] args) {
    
   // First test case 
    BSTNode root = null;
    String treeAsString = " empty ";
    int key = 20;
   if (runTestCase(root , key , treeAsString) == false) return;
   
   // Second test case
   root = new BSTNode(20);
   BSTNode leftChild = new BSTNode(15);
   BSTNode rightChild = new BSTNode(30);

   root.setLeft(leftChild); 
   root.setRight(rightChild);
   
   treeAsString = "  20\n"
                  +" / \\ \n"
                  +"15 30 \n ";
                  
   if (runTestCase(root , key , treeAsString )== false) return;
   ////// End of the second test case


  //Third test case
   key= 90;
   root = new BSTNode(40);
   leftChild = new BSTNode(30);
   rightChild = new BSTNode(50);
   
   BSTNode leftChild2 = new BSTNode(15);
   BSTNode rightChild2 = new BSTNode(35);
   
   root.setLeft(leftChild); 
   root.setRight(rightChild);
   
   leftChild.setLeft(leftChild2); 
   leftChild.setRight(rightChild2);
   
    treeAsString = "  40\n"
                  +" / \\ \n"
                  +"30 50 \n "
                  +"/ \\ \n"
                  +"15 35 \n ";
   
   
   if (runTestCase(root , key , treeAsString )== false) return;
  //End of the third test case

  // If none the test cases failed then all of them are ok then sucess=true
  writeResult(root , true , 0, treeAsString , 0, 0);

  } 
