/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 28: counts the number of inversions in a list of numbers.

import java.io.*;
import java.util.Random;


public class studentrecw28PROG
{

 public static int modelcountInversions(int nums[])
 {
       int mid = nums.length/2, k;
       int countLeft, countRight, countMerge;
			
	if (nums.length <= 1)
	return 0;
	
	int left[] = new int[mid];
	
	int right[] = new int[nums.length - mid];
	
	for (k = 0; k < mid; k++)
	
	left[k] = nums[k];
	
	for (k = 0; k < nums.length - mid; k++)
	
	right[k] = nums[mid+k];
	
	countLeft = modelcountInversions (left);
	
	countRight = modelcountInversions (right);
	
	int result[] = new int[nums.length];
	
	countMerge = modelmergeAndCount (left, right, result);
	
	for (k = 0; k < nums.length; k++)
	
	nums[k] = result[k];
	
	return (countLeft + countRight + countMerge);
	
 }
	
/* This procudure will merge two lists, and count the number of inversions 
caused by the elements in the "right" list that are
less than elements in the "left" list.
*/
	
public static int modelmergeAndCount (int left[], int right[], int result[])
{
	
	int a = 0, b = 0, count = 0, i, k=0;
	
	while ( ( a < left.length) && (b < right.length) )
	{
	
	if ( left[a] <= right[b] )
	
	result [k] = left[a++];
	
	else
	
	/* You have found (a number of) inversions here. */
	
	
	{
	
	result [k] = right[b++];
	
	count += left.length - a;
	
	}
	
	k++;
	
	
	}
	
	if ( a == left.length )
	
	for ( i = b; i < right.length; i++)
	
	result [k++] = right[i];
	
	else
	
	for ( i = a; i < left.length; i++)
	
	result [k++] = left[i];
	
	return count;
	
}

 public static void main(String [ ] args) 
{
  
    boolean SUCCESS = false;
    
    // To test: generate a random array of length 10
    Random randNumGenerator = new Random();
    int[] numbers = new int[10];
    int[] numbers2 = new int[10];
    for (int i=0; i< numbers.length; i++)
    {
       numbers[i] = (randNumGenerator.nextInt(100)+1);
       numbers2[i]= numbers[i];
    }

    if (countInversions(numbers2)== modelcountInversions(numbers)) SUCCESS = true;

    try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS) { 
   
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

  
