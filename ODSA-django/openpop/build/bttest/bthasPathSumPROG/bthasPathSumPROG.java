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



public class studentbthasPathSumPROG
{

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
  
   boolean SUCCESS1 = false;
   boolean SUCCESS2 = false;

    int sum1= 25;
    int sum2= 5;

    if (bthasPathSum(root, sum1)== modelbthasPathSum(root, sum1)) SUCCESS1 = true;
    if (bthasPathSum(root, sum2)== modelbthasPathSum(root, sum2)) SUCCESS2 = true;
    try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS1 && SUCCESS2) { 
   
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
