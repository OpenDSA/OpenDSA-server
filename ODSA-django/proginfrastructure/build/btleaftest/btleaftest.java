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

public class studentbtleaftest
{

 public static int countLeaf(BinNode root) {
  if(root == null)  return 0;
  if(root.isLeaf())      
    return 1;            
  else 
    return countLeaf(root.left())+ countLeaf(root.right());      

 }



 public static void writeResult(BinNode rt,boolean SUCCESS){
 try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS) { 
   
      output.println("Well Done!");
      output.close();
     }
    else 
    {
     //output.println("Try Again!  Expected Answer is "+ Integer.toString(count(rt)) +" Your Answer is: " + Integer.toString(exercise2(rt)));
     output.println("Try Again! Your answer is not correct for all test cases."); // Later we should display the binary tree where the test case failed
     output.close();
    }
  
    }
      catch (IOException e) {
	e.printStackTrace();
    }

 }
 
 public static boolean runTestCase(BinNode rt)
 { 
   boolean SUCCESS = false;  
   if (exercise3(rt)  == countLeaf(rt)) 
   { 
     SUCCESS = true;   
   }
  
   else  // This test case fail then will write the result and abort the function
   {
    SUCCESS = false;
    writeResult(rt , SUCCESS);
    
   }
  return SUCCESS;
 }
 


  public static void main(String [ ] args) {
 
  // We will more than one test case
   
  //First test case ..empty tree
   BSTNode<Integer,Integer> root = null;
   
   if (runTestCase(root)== false) return;
   ////// End of the first test case

   // Second test case
   root = new BSTNode<Integer,Integer>(10,10);
   BSTNode<Integer,Integer> leftChild = new BSTNode<Integer,Integer>(15,15);
   BSTNode<Integer,Integer> rightChild = new BSTNode<Integer,Integer>(20,20);

   root.setLeft(leftChild); 
   root.setRight(rightChild);

   if (runTestCase(root)== false) return;
   ////// End of the second test case


  //Third test case
  root= null;
  root = new BSTNode<Integer,Integer>(10,10);
  BSTNode<Integer,Integer> currentNode= root;
  ArrayList <BSTNode<Integer,Integer>> leftChildren = new ArrayList<BSTNode<Integer,Integer>>() ; 
  ArrayList <BSTNode<Integer,Integer>> rightChildren = new ArrayList<BSTNode<Integer,Integer>>() ;

  for (int i=0 ; i<10; i++)
  {   
   leftChildren.add( new BSTNode<Integer,Integer>(15,15));
   rightChildren.add( new BSTNode<Integer,Integer>(15,15));
  
  }

   for (int i=0 ; i<10; i++)
  {      
   currentNode.setLeft(leftChildren.get( i));
   currentNode = leftChildren.get( i);
  }
  currentNode= root;

   for (int i=0 ; i<10; i++)
  {   
   currentNode.setRight(rightChildren.get( i));
   currentNode = rightChildren.get(i);
  }
 currentNode=root;
  if (runTestCase(root)== false) return;
 ///End of the third test case

  // If none the test cases failed then all of them are ok then sucess=true
  writeResult(root , true);

  } 
