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
  int element();
  void setElement(int v);

  // return the children
  BinNode left();
  BinNode right();

  // return TRUE if a leaf node, FALSE otherwise
  boolean isLeaf();
 
}
/* *** ODSAendTag: BinNode *** */

 

// Binary tree node implementation: supports comparable objects
class BSTNode implements BinNode {
  private int element; // Element for this node
  private BSTNode left;       // Pointer to left child
  private BSTNode right;      // Pointer to right child

  // Constructors
  BSTNode() {left = right = null; }
  BSTNode(int val) { left = right = null; element = val; }
  BSTNode(int val, BSTNode l, BSTNode r)
    { left = l; right = r; element = val; }

  // Get and set the element value
  public int element() { return element; }
  public void setElement(int v) { element = v; }
  

  // Get and set the left child
  public BSTNode left() { return left; }
  public void setLeft(BSTNode p) { left = p; }

  // Get and set the right child
  public BSTNode right() { return right; }
  public void setRight(BSTNode p) { right = p; }

  // return TRUE if a leaf node, FALSE otherwise
  public boolean isLeaf() { return (left == null) && (right == null); }


}




public class studentBTincPROG
{

    public static  long fTimeout=4;
    public static boolean fFinished= false;
    public static Throwable fThrown= null;
    public static  BSTNode rtmember; 

    public static void evaluate() throws Throwable {
	    Thread thread= new Thread() {
		@Override
		public void run() {
		 try {
		  BTinc(rtmember);
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


 public static void modelbtInc(BinNode rt) {
    if (rt != null)
    {
     rt.setElement(rt.element() +1);
     modelbtInc(rt.left());
     modelbtInc(rt.right());
    }
 }

 
public static boolean checkEqualTrees(BSTNode a, BSTNode b) {
    // check for reference equality and nulls
    if (a==b) return true; // note this picks up case of two nulls
    if (a==null) return false;
    if (b==null) return false;

    // check for data inequality
    if (a.element()!=b.element()) {
        if ((a == null)||(b == null)) return false;
        if (a.element()!= b.element()) return false;
    }

    // recursively check branches
    if (!checkEqualTrees(a.left(),b.left())) return false;
    if (!checkEqualTrees(a.right(),b.right())) return false;

    // we've eliminated all possibilities for non-equality, so trees must be equal
    return true;
}

 public static void writeResult(BSTNode rt,boolean SUCCESS, String treeAsString , String modelAnswer, String studentAnswer ){
 try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS) { 
   
      output.println("Well Done!");
      output.close();
     }
    else 
    {
     
     output.println("Try Again! Your answer is not correct for all test cases. For example, if the given tree is:\n " + treeAsString + ", then your code returns:\n  " + studentAnswer+ " \n. The expected answer is:\n " + modelAnswer); 
     output.close();
     
    }
  
    }
      catch (IOException e) {
	e.printStackTrace();
    }

 }
 
 public static boolean runTestCase(BSTNode rt, BSTNode rt2 , String treeAsString , String modelAnswer)
 { 
   
   try {
     // Fail on time out object
     rtmember = rt;
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }
   
   
   boolean SUCCESS = false;
   
   modelbtInc(rt2);
   if (checkEqualTrees(rt , rt2) == true) 
   { 
     SUCCESS = true;   
   }
  
   else  // This test case fail then will write the result and abort the function
   {
    SUCCESS = false;
    String studentAnswer ="";
    if (rt!= null)
     studentAnswer = getTreeAsaString(rt);
    writeResult(rt , SUCCESS , treeAsString , modelAnswer , studentAnswer);
    
   }
  return SUCCESS;
 }
 
 public static String getTreeAsaString(BinNode rt)
 {

   String tree = " "+ rt.element()+"\n";
   tree = tree +" / \\ \n";
   tree= tree + " "+ rt.left().element()+ " "+ rt.right().element() + "\n";
   
   return tree;
 }

  public static void main(String [ ] args) {
 
  // We will have more than one test case
    String treeAsString = " empty ";
  //First test case ..empty tree
   BSTNode root = null;
   BSTNode root2 = null;
  
   if (runTestCase(root, root2, treeAsString , "") == false) return;
   ////// End of the first test case

   // Second test case
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
   
   treeAsString = "  10\n"
                  +" / \\ \n"
                  +"15 20 \n ";

   String modelAnswer = "  11\n"
                       +" / \\ \n"
                       +"16 21 \n ";

   if (runTestCase(root, root2 , treeAsString , modelAnswer )== false) return;
   ////// End of the second test case

   // Third test case
   root = new BSTNode(20);
   root2 = new BSTNode(20);
   
   leftChild = new BSTNode(5);
   rightChild = new BSTNode(30);

   leftChild2 = new BSTNode(5);
   rightChild2 = new BSTNode(30);

   root.setLeft(leftChild); 
   root.setRight(rightChild);
  
   root2.setLeft(leftChild2); 
   root2.setRight(rightChild2);
   
   treeAsString = "  20\n"
                  +" / \\ \n"
                  +" 5 30 \n ";

   modelAnswer = "  21\n"
                +" / \\ \n"
                +" 6  31 \n ";

  if (runTestCase(root, root2 , treeAsString , modelAnswer )== false) return;
  
  // If none the test cases failed then all of them are ok then sucess=true
 writeResult(root , true , treeAsString , "" , "" );

  } 
