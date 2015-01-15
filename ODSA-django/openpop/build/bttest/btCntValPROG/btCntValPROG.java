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



public class studentbtCntValPROG
{

 public static int modelbtCntVal(BinNode rt , Comparable value) {
    if (rt == null) return 0;    
    int count = 0;
    
    if(value.compareTo(rt.element()) == 0)
          count++;
     count += modelbtCntVal(rt.left(), value);
     count += modelbtCntVal(rt.right(), value);
     return count;
    
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
 
 public static boolean runTestCase(BinNode rt , Comparable value)
 { 
   boolean SUCCESS = false;  
   if (btCntVal(rt, value)  == modelbtCntVal(rt, value)) 
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
   BSTNode root = null;
   Comparable value = new Integer(15);
  
   if (runTestCase(root , value) == false) return;
   ////// End of the first test case

   // Second test case
   root = new BSTNode(10);
   BSTNode leftChild = new BSTNode(15);
   BSTNode rightChild = new BSTNode(20);

   root.setLeft(leftChild); 
   root.setRight(rightChild);
   if (runTestCase(root , value)== false) return;
   ////// End of the second test case


  //Third test case
  root= null;
  root = new BSTNode(10);
  BSTNode currentNode= root;
  ArrayList <BSTNode> leftChildren = new ArrayList<BSTNode>() ; 
  ArrayList <BSTNode> rightChildren = new ArrayList<BSTNode>() ;

  for (int i=0 ; i<10; i++)
  {   
   leftChildren.add( new BSTNode(15));
   rightChildren.add( new BSTNode(15));
  
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
 
  if (runTestCase(root , value) == false) return;
 ///End of the third test case

  // If none the test cases failed then all of them are ok then sucess=true
  writeResult(root , true);

  } 
