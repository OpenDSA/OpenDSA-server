import shlex # for strings splitting
import re # for special characters escaping
import sys
import string

# Addresses the common misconceptions found in binary trees problems. The code executes correctly but inefficient

def btcheckEfficientCode(studentCode , exerciseName):
        # Get the minimum node in a binary tree exercise or the number of nodes having value less than a given value
        # Check on the following misconceptions (The following should not be done):
        # 1- Traversing the right sub-tree.
        # 2- Checking on the children values.
        # 3- No check on Left (for any min of a bst the left sub-tree has to be traversed)
        # 4- Check if the root is leaf to terminate
	if exerciseName == "bstMinPROG" or  exerciseName == "bstsmallCountPROG":
                efficient1, feedback1 = checkNoLeftSubTreeMisconception(studentCode)
		efficient2, feedback2 = checkChildisNullMisconception(studentCode) 
                efficient3, feedback3 = checkChildValueMisconception(studentCode)
                efficient = (efficient1 and efficient2 and efficient3)
                feedback = feedback1 + feedback2 + feedback3

                if  exerciseName == "bstMinPROG":
                  efficient4, feedback4 = checkRightSubTreeMisconception(studentCode)
                  efficient = efficient4
                  feedback = feedback4
             

        # For everynode check if the sum of the left subtree plus the right sub-tree always equals the root value
        # Check on the following misconceptions (The following should not be done):
        # 1- Check if the root is leaf to terminate
        elif exerciseName== "btcheckSumPROG":
                efficient, feedback =  checkifLeafMisconception(studentCode)                       
	
        # Other exercises:
        # Check on the following misconceptions (The following should not be done):
        # 1- Checking if the children is Null.
        # 2- Checking on the children values.
        # 3- Check if the root is leaf to terminate (except for the count leaf nodes exercise)
	else:
		efficient1, feedback1 = checkChildisNullMisconception(studentCode)
                efficient2, feedback2 = checkChildValueMisconception(studentCode)
                efficient = (efficient1 and efficient2)
                feedback = feedback1 + feedback2 

                if exerciseName != "btLeafPROG":
                  efficient3, feedback3 = checkifLeafMisconception(studentCode)
                  efficient = (efficient and efficient3)
                  feedback = feedback + feedback3
            
                if exerciseName == "mbtSwapPROG":
		  efficient4, feedback4 = checkifRootsSwapped(studentCode)
                  efficient = (efficient and efficient4)             
                  feedback = feedback + feedback4

	return (efficient, feedback)
 
# Used in BST Misconceptions: Checking if the student traverse the left sub-tree or not
# This misconception can be called if for example it is required from the student to get the minimum value in a binary search tree.. the student HAS to traverse the left sub-tree to get the minimum value
def checkNoLeftSubTreeMisconception(studentCode):
	if "left()" not in studentCode:
          return (False, ["\nTry Again! Your solution is incorrect. To find the minimum value in a BST, you MUST check at least some values that are less than the root. These are in the left subtree."])

	else:
          return (True,[""])

# Used in BST Misconceptions: Checking if the student traverse the right sub-tree (if you want to get the min value in a bst ...you don't need)
def checkRightSubTreeMisconception(studentCode):
	if "right()" in studentCode:
          return (False, ["Try Again! Your solution executes correctly but is not efficient. Remember that in a BST, a smaller value than the current node can only be in the left subtree."])

	else:
          return (True,[""])

#Used in Binary Tree and/or BST Misconceptions: Check if the student is checking on if the child(ren) is/are null or not
def checkChildisNullMisconception(studentCode):
       notAllowedConditions = ["left()==null" , "right()==null" , "left()!=null" , "right()!=null"]

       if  any(notAllowedCondition in studentCode.replace(" ", "") for notAllowedCondition in notAllowedConditions):
         return (False, ["Try Again! Your solution executes correctly but is not efficient. There is no reason to check if the children are null or not. Remember that the root's left or right child is treated as the new root when processed by the recursive call."])

       else:
         return (True,[""])



#Used in Binary Tree and/or BST Misconceptions: Check if the student is checking on the values of one or both children
def checkChildValueMisconception(studentCode):
       notAllowedStatments = ["left().element()" , "right().element()"]
       if any(notAllowedStatment in studentCode.replace(" ", "") for notAllowedStatment in notAllowedStatments):
        return (False, ["\n Try Again! Your solution executes correctly but is not efficient. There is no reason to check the children's values. Remember that the root's left or right child is treated as the new root when processed by the recursive call."])

       else:
        return (True,[""])


#Used in Binary Tree and/or BST Misconceptions: Check if the student is checking if the root is leaf or not while it is needed
def checkifLeafMisconception(studentCode):
       if "isLeaf()" in studentCode:
         return (False, ["\n Try Again! Your solution executes correctly but is not efficient. There is no reason to check if the root is a leaf or not."])

       else:
         return (True,[""])

def checkifRootsSwapped(studentCode):
      notAllowedStatments = ["root1=root2" , "root2=root1"]
      if any(notAllowedStatment in studentCode.replace(" ", "") for notAllowedStatment in notAllowedStatments):
         return (False, ["\n Try Again! The problem requires you to swap the values of the nodes in the trees, not just swap the roots of the trees."])
      else:
         return (True,[""])


