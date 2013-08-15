# Create your views here.

from django.http import HttpResponse
import xml.etree.ElementTree as xml # for xml parsing
import shlex # for strings splitting
import re # for special characters escaping
import os
import subprocess
#from subprocess import call
#import pdb; pdb.set_trace()
def assesskaex(data , generatedList):
    
    print generatedList
    feedback=[False, 'null']
    print feedback
    filesPath = '/home/OpenPOP/Backend/visualize/build/ListTest/javaSource/'
    print "In the begining of assessing the code using java compiler"
    #cleaning: deleting already created files
    if os.path.isfile(filesPath +'generatedlist'):
       os.remove(filesPath+'generatedlist')

    if os.path.isfile(filesPath +'studentlisttest.java'):
       os.remove(filesPath+'studentlisttest.java')
 
    if os.path.isfile(filesPath +'output'):
       os.remove(filesPath+'output')

    if os.path.isfile(filesPath +'compilationerrors.out'):
       os.remove(filesPath + 'compilationerrors.out')
   
    if os.path.isfile(filesPath +'runerrors.out'):
       os.remove(filesPath + 'runerrors.out')
    
    genlistfile = open(filesPath+'generatedlist', 'w')
    genlistfile.write(generatedList)
    genlistfile.close()
    
    # Saving the submitted/received code in the studentlisttest.java file by copying the listtest + studentcode +}
    listTestFile = open(filesPath+'listtest.java' , 'r')
    listtest = listTestFile.read()
    answer = open(filesPath+'studentlisttest.java', 'w')
    answer.write(listtest)
    answer.write("public static" + data)
    answer.write("}")
    answer.close()
    
    # Setting the DISPLAY then run the processing command to test the submitted code
    proc1 = subprocess.Popen(" cd /home/OpenPOP/Backend/visualize/build/ListTest/javaSource/; javac studentlisttest.java 2> /home/OpenPOP/Backend/visualize/build/ListTest/javaSource/compilationerrors.out ; java studentlisttest 2> /home/OpenPOP/Backend/visualize/build/ListTest/javaSource/runerrors.out", stdout=subprocess.PIPE, shell=True)
    (out1, err1) = proc1.communicate() 
    
    # Read the success file if has Success inside then "Well Done!" Otherwise "Try Again!"
    if  os.path.isfile(filesPath+'compilationerrors.out'):
          syntaxErrorFile = open(filesPath+'compilationerrors.out' , 'r')
          feedback[0] = False
          feedback[1]= syntaxErrorFile.readlines()
          syntaxErrorFile.close()
          if os.stat(filesPath+'compilationerrors.out')[6]!=0:
             feedback[1]= feedback[1]#.rsplit(':',1)[1]
             return feedback;
    if os.path.isfile(filesPath+'runerrors.out'):
       #Check what is returned from the test : what is inside the success file
          runErrorFile = open(filesPath+'runerrors.out' , 'r')
          feedback[0] = False
          feedback[1]= runErrorFile.readlines()
          runErrorFile.close()
          if os.stat(filesPath+'runerrors.out')[6]!=0:
             return feedback;
    
    
    if os.path.isfile(filesPath+'output'):
       #Check what is returned from the test : what is inside the success file
       successFile = open(filesPath+'output' , 'r')
       feedback[1] = successFile.readlines()
       print feedback[1]
       for line in feedback[1]:
           if "Well Done" in line:
              feedback[0] = True
              break 
           else :
              feedback[0] = False
        
      
    return  feedback

