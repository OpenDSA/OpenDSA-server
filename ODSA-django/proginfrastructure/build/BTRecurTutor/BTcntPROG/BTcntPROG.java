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

public class studentBTcntPROG
{

 public static int count(BinNode rt) {
    if (rt == null) return 0;  // Nothing to count
    return 1 + count(rt.left()) + count(rt.right());
   }



  public static void main(String [ ] args) {
    boolean SUCCESS = false;
    BSTNode<Integer,Integer> root = new BSTNode<Integer,Integer>(10,10);

    //Generating a tree at random
    Random randomGenerator = new Random();
   int randomLeftChildernIter = randomGenerator.nextInt(10); 
   int randomrightChildernIter = randomGenerator.nextInt(10); 
   for (int idx = 1; idx <= 10; ++idx){
      
       root.setLeft(new BSTNode<Integer,Integer>(15,15));
    }
   for (int idx = 1; idx <= 10; ++idx){
      
        root.setRight(new BSTNode<Integer,Integer>(20,20));
    }
   
    if (BTcnt(root)  == count(root)) SUCCESS = true;

    try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS) { 
   
      output.println("Well Done!");
      output.close();
     }
    else 
    {
     output.println("Try Again!  Expected Answer is "+ Integer.toString(count(root)) +" Your Answer is: " + Integer.toString(exercise2(root)));
     output.close();
    }
  
    }
      catch (IOException e) {
	e.printStackTrace();
    }

  }

  
