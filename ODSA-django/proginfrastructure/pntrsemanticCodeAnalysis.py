import shlex # for strings splitting
import re # for special characters escaping
import sys
import string

# Addresses the common misconceptions found in pointers

def pntrcheckEfficientCode(studentCode , exerciseName):
  
	if exerciseName == "pntrequalspntrPROG" :
                efficient, feedback = checkpq(studentCode)
        else: 
                 efficient = True
                 feedback  = [""]
	return (efficient, feedback)
 
# Used in BST Misconceptions: Checking if the student traverse the left sub-tree or not
# This misconception can be called if for example it is required from the student to get the minimum value in a binary search tree.. the student HAS to traverse the left sub-tree to get the minimum value
def checkpq(studentCode):
	if "p=q" not in studentCode.replace(" ", ""):
          return (False, ["\nTry Again!  It was required to use the pointer q."])

	else:
          return (True,[""])

