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



public class studentMBTswapPROG
{
    public static  long fTimeout=4;
    public static boolean fFinished= false;
    public static Throwable fThrown= null;
    public static  BSTNode rtmember; 
    public static  BSTNode rtmember2; 
   
    public static void evaluate() throws Throwable {
	    Thread thread= new Thread() {
		@Override
		public void run() {
		 try {
		  MBTswap(rtmember , rtmember2);
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

 public static boolean checkEqualTrees(BSTNode a, BSTNode b) {
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
    if (!checkEqualTrees(a.left(),b.left())) return false;
    if (!checkEqualTrees(a.right(),b.right())) return false;

    // we've eliminated all possibilities for non-equality, so trees must be equal
    return true;
}

 public static void modelmbtSwap(BSTNode a, BSTNode b) {
    
    if (a==null || b== null) return;
    
    //Swapping
    int temp = (Integer)a.element();
    a.setElement(((Integer)b.element()));
    b.setElement(temp);
    
    modelmbtSwap(a.left(), b.left());
    modelmbtSwap(a.right(), b.right());
}

 public static void writeResult(BSTNode rt, BSTNode rt2, boolean SUCCESS , String tree1AsString  , String tree2AsString , String studentAnswerrt1 , String studentAnswerrt2 ){
 try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS) { 
   
      output.println("Well Done!");
      output.close();
     }
    else 
    {
     output.println("Try Again! Your answer is not correct for all test cases. For example, if the first tree is:\n " + tree1AsString + "\n and the second tree is:\n "+ tree2AsString + " \n, then your code changes the first tree to:\n  " + studentAnswerrt1 +"and the second tree to:\n"+ studentAnswerrt2+ ". The expected answer is the trees swapped.");  
     output.close();
    }
  
    }
      catch (IOException e) {
	e.printStackTrace();
    }

 }
 
 public static boolean runTestCase(BSTNode rt, BSTNode rt2 , BSTNode rt3, BSTNode rt4 , String tree1AsString  , String tree2AsString )
 { 
    
   boolean SUCCESS = false; 
   // The model answer will swap the  trees
   modelmbtSwap (rt, rt2);
   
   // Student's answer should swap them back again
  
   try {
     // Fail on time out object
     rtmember = rt;
     rtmember2 = rt2;
     evaluate();
    } 
    catch(Throwable t) {	
     throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }

   // The result should be the same as the original tree
   if (checkEqualTrees(rt , rt3) && checkEqualTrees(rt2, rt4))
   { 
     SUCCESS = true;   
   }
  
   else  // This test case fail then will write the result and abort the function
   {
    SUCCESS = false;
    String studentAnswerrt1 ="";
    String studentAnswerrt2 ="";
    if (rt!= null && rt2!=null){
     studentAnswerrt1 = getTreeAsaString(rt2);
     studentAnswerrt2 = getTreeAsaString(rt);
     }
    writeResult(rt , rt2, SUCCESS , tree1AsString , tree2AsString , studentAnswerrt1 , studentAnswerrt2);
    
   }
  return SUCCESS;
 }
 
public static String getTreeAsaString(BinNode rt)
 {

   String tree = " "+ (Integer)rt.element()+"\n";
   tree = tree +" / \\ \n";
   tree= tree + " "+ (Integer)rt.left().element()+ " "+ (Integer)rt.right().element() + "\n";
   
   return tree;
 }

  public static void main(String [ ] args) {
 
  // We will have more than one test case
   
  //First test case ..empty tree
   BSTNode root = null;
   BSTNode root2 = null;
   
   BSTNode root3 = null;
   BSTNode root4 = null;
   
   String tree1AsString = " empty ";
   
   String tree2AsString = " empty ";
   
   if (runTestCase(root, root2 , root3, root4 ,  tree1AsString  ,  tree2AsString  ) == false) return;
   ////// End of the first test case

   // Second test case 
   root = new BSTNode(10);
   root2 = new BSTNode(66);
   
   root3 = new BSTNode(10);//Original First tree
   
   root4 = new BSTNode(66); //Original Second tree

   BSTNode leftChild = new BSTNode(15);
   BSTNode rightChild = new BSTNode(20);

   BSTNode leftChild2 = new BSTNode(77);
   BSTNode rightChild2 = new BSTNode(80);
   
   BSTNode leftChild3 = new BSTNode(15);
   BSTNode rightChild3 = new BSTNode(20);

   BSTNode leftChild4 = new BSTNode(77);
   BSTNode rightChild4 = new BSTNode(80);

   root.setLeft(leftChild); 
   root.setRight(rightChild);
  
   root2.setLeft(leftChild2); 
   root2.setRight(rightChild2);
   
   root3.setLeft(leftChild3); 
   root3.setRight(rightChild3);
  
   root4.setLeft(leftChild4); 
   root4.setRight(rightChild4);
   
   
   tree1AsString = "  10\n"
                  +" / \\ \n"
                  +"15 20 \n ";

   tree2AsString = "  66\n"
                  +" / \\ \n"
                  +"77 80 \n ";

   if (runTestCase(root, root2, root3, root4 , tree1AsString  , tree2AsString )== false) return;
   ////// End of the second test case

  // If none the test cases failed then all of them are ok then sucess=true
  writeResult(root , root2 , true, ""  , "" , "" , "" );
  } 
