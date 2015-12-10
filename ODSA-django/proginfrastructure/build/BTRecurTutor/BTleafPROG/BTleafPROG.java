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
import java.util.ArrayList;


/** ADT for binary tree nodes */
 interface BinNode<E> {
  /** Get and set the element value */
  public E element();
  public void setElement(E v);

  /** @return The left child */
  public BinNode<E> left();

  /** @return The right child */
  public BinNode<E> right();

  /** @return True if a leaf node, false otherwise */
  public boolean isLeaf();
}

/** Binary tree node implementation: Pointers to children
    @param E The data elementimport java.util.Random;
    @param Key The associated key for the record */
class BSTNode<Key, E> implements BinNode<E> {
  private Key key;              // Key for this node
  private E element;            // Element for this node
  private BSTNode<Key,E> left;  // Pointer to left child
  private BSTNode<Key,E> right; // Pointer to right child

  /** Constructors */
  public BSTNode() {left = right = null; }
  public BSTNode(Key k, E val)
  { left = right = null; key = k; element = val; }
  public BSTNode(Key k, E val,
                 BSTNode<Key,E> l, BSTNode<Key,E> r)
  { left = l; right = r; key = k; element = val; }

  /** Get and set the key value */
  public Key key() { return key; }
  public void setKey(Key k) { key = k; }

  /** Get and set the element value */
  public E element() { return element; }
  public void setElement(E v) { element = v; }

  /** Get and set the left child */
  public BSTNode<Key,E> left() { return left; }
  public void setLeft(BSTNode<Key,E> p) { left = p; }

  /** Get and set the right child */
  public BSTNode<Key,E> right() { return right; }
  public void setRight(BSTNode<Key,E> p) { right = p; }

  /** @return True if a leaf node, false otherwise */
  public boolean isLeaf()
  { return (left == null) && (right == null); }
}

public class studentBTleafPROG
{


    public static  long fTimeout=4;
    public static boolean fFinished= false;
    public static Throwable fThrown= null;
    public static  BinNode rtmember; 
    public static int studentAnswer;
    public static void evaluate() throws Throwable {
	    Thread thread= new Thread() {
		@Override
		public void run() {
		 try {
		  studentAnswer = BTleaf(rtmember);
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


 public static int modelbtcountLeaf(BinNode root) {
  if(root == null)  return 0;
  if(root.isLeaf())      
    return 1;            
  else 
    return modelbtcountLeaf(root.left())+ modelbtcountLeaf(root.right());      

 }



 public static void writeResult(BinNode rt,boolean SUCCESS , String treeAsString , int modelAnswer, int studentAnswer){
 try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS) { 
   
      output.println("Well Done!");
      output.close();
     }
    else 
    {
     output.println("Try Again! Your answer is not correct for all test cases. For example, if the given tree is:\n" + treeAsString + ", then your code returns:  " + studentAnswer+ " The expected answer is: " + modelAnswer+"."); 
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
     // Fail on time out object
     rtmember = rt;
     evaluate();
   
    } catch(Throwable t) {
    	
        throw new AssertionError("You are probably having an infinite recursion! Please revise your code!");
    }

   boolean SUCCESS = false;
   
   int modelAnswer  = modelbtcountLeaf(rt);
   
   
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
   
  //First test case ..empty tree
   String treeAsString = " empty ";
   
   BSTNode<Integer,Integer> root = null;
   
   if (runTestCase(root ,treeAsString )== false) return;
   ////// End of the first test case

   // Second test case
   root = new BSTNode<Integer,Integer>(10,10);
   BSTNode<Integer,Integer> leftChild = new BSTNode<Integer,Integer>(15,15);
   BSTNode<Integer,Integer> rightChild = new BSTNode<Integer,Integer>(20,20);

   root.setLeft(leftChild); 
   root.setRight(rightChild);
   
     
   treeAsString = "  10\n"
                  +" / \\ \n"
                  +"15 20 \n ";
 
   if (runTestCase(root , treeAsString)== false) return;
   ////// End of the second test case


  //Third test case
  root= null;
  root = new BSTNode<Integer,Integer>(5,5);
  leftChild = new BSTNode<Integer,Integer>(25,25);

  root.setLeft(leftChild); 
 
  treeAsString = "  5\n"
                  +" /  \n"
                  +"25  \n ";
                  
  if (runTestCase(root , treeAsString)== false) return;
 ///End of the third test case

  // If none the test cases failed then all of them are ok then sucess=true
  writeResult(root , true , treeAsString , 0 , 0);

  } 
