# Create your views here.
from opendsa.models import  UserExercise, UserExerciseLog, UserData , UserProgLog
from opendsa.exercises import update_module_proficiency
from opendsa import models 
from decimal import Decimal                         
from django.http import HttpResponse
import xml.etree.ElementTree as xml # for xml parsing
import shlex # for strings splitting
import re # for special characters escaping
import os
import subprocess
import datetime
import codecs
import unicodedata
import sys
import string
import time, sys
import shutil
from btsemanticCodeAnalysis import btcheckEfficientCode
from pntrsemanticCodeAnalysis import pntrcheckEfficientCode
#from subprocess import call
#import pdb; pdb.set_trace()

# Static code analysis Includes
#sys.path.append(os.path.abspath('plyj/'))
#import plyj.model as model
#import plyj.parser as plyj
#import pprint


sys.path.append(os.path.abspath('.'))
import settings


def attempt_problem_pop(user_data, user_exercise, attempt_number,
    completed, count_hints, time_taken, attempt_content, module,   
    ex_question, ip_address, request_post):
    
    data = request_post.get('code') 
    
    generatedList =request_post.get('genlist')
    
    progexType =request_post.get('progexType')
   
    checkDefinedvar= request_post.get('checkdefvar')

    if checkDefinedvar == "True":
       listoftypes= request_post.get('listoftypes')
    else : 
       listoftypes=""
    # Clean the strings from bad characters
    
    #listoftypes = ''.join([x for x in listoftypes if ord(x) < 128])

    data = ''.join([x for x in data if ord(x) < 128])

    # Summary Programming Exercises so we need to get the current selected exercise name to run the eqivelant unit test
    if request_post.get('summexname')  != 'null':
       exerciseName = request_post.get('summexname')

    else:
        exerciseName = request_post.get('sha1')
    
    feedback, pathtouserFiles= setparameters(exerciseName, data, generatedList, checkDefinedvar , listoftypes , progexType, user_data)

    if  os.path.exists(pathtouserFiles ):
        shutil.rmtree(pathtouserFiles)
     
    if user_exercise:   # and user_exercise.belongs_to(user_data):
        dt_now = datetime.datetime.now()
        #exercise = user_exercise.exercise
        user_exercise.last_done = dt_now
        # Build up problem log for deferred put
        problem_log = models.UserExerciseLog(
                user=user_data.user,
                exercise=user_exercise.exercise,
                time_taken=time_taken,
                time_done=dt_now,
                count_hints=count_hints,
                hint_used=int(count_hints) > 0,
                correct=feedback[0],
                count_attempts=attempt_number,
                ex_question=exerciseName,
                ip_address=ip_address,
        )


        first_response = (attempt_number == 1 and count_hints == 0) or (count_hints == 1 and attempt_number == 0)

        if user_exercise.total_done > 0 and user_exercise.streak == 0 and first_response:
            bingo('hints_keep_going_after_wrong')

        just_earned_proficiency = False
        #update list of started exercises
        if not user_data.has_started(user_exercise.exercise):
            user_data.started(user_exercise.exercise.id)

        proficient = user_data.is_proficient_at(user_exercise.exercise)
        #if str2bool(completed):

        user_exercise.total_done += 1
        if problem_log.correct:

                # Streak only increments if problem was solved correctly (on first attempt)
           user_exercise.total_correct += 1
           user_exercise.streak += 1
           user_exercise.longest_streak = max(user_exercise.longest_streak, user_exercise.streak)
           user_exercise.progress = Decimal(user_exercise.streak)/Decimal(user_exercise.exercise.streak)
           if not proficient:
              problem_log.earned_proficiency = user_exercise.update_proficiency_ka(correct=True,ubook=user_data.book)
              if user_exercise.progress >= 1:
                 if len(user_data.all_proficient_exercises)==0:
                    user_data.all_proficient_exercises += "%s" %user_exercise.exercise.id
                 else:
                    user_data.all_proficient_exercises += ",%s" %user_exercise.exercise.id
           else:
             user_exercise.total_done += 1
             user_exercise.progress = Decimal(user_exercise.streak)/Decimal(user_exercise.exercise.streak)
    
        # Saving student's code and the feedback received
       
        problem_log.save()
        user_exercise.save()
        user_data.save()
        if proficient or problem_log.earned_proficiency:
            update_module_proficiency(user_data, module, user_exercise.exercise)
        userprog_log = models.UserProgLog(
               problem_log= problem_log ,
               student_code= data,
               feedback=feedback[1],
              )
 
        userprog_log.save()
        return user_exercise,feedback


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#  Set the testing folder and passed parameters to the programming exercise
def setparameters(exerciseName, data, generatedList, checkDefinedvar, listoftypes, progexType , user_data ):
    # Check from which programming exercise we got this request
    if exerciseName == "BinaryTreePROG" : #count number of nodes
       feedback , peruserFilesPath= assessprogkaex (data, "binarytreetest", "binarytreetest","",checkDefinedvar , listoftypes , "" , user_data)

    elif exerciseName == "BTLeafPROG" :  #count number of leaf nodes
       feedback, peruserFilesPath= assessprogkaex (data , "btleaftest", "btleaftest","", checkDefinedvar , listoftypes, "", user_data)      

    elif "list" in progexType:  #generate a list
       feedback , peruserFilesPath= assessprogkaex(data , "listadttest", "listadttest" ,generatedList, checkDefinedvar, listoftypes, "", user_data)

    # Binary Trees programming exercises 
    elif "BTRecurTutor" in progexType:   
       feedback, peruserFilesPath= assessprogkaex(data,"BTRecurTutor/"+exerciseName, exerciseName,"",checkDefinedvar , listoftypes, progexType, user_data)

    # Recursion programming exercises have the same folder with different subfolders. Where the subfolder is the exercise name
    elif "RecurTutor" in progexType:   
       feedback, peruserFilesPath= assessprogkaex(data,"RecurTutor/"+exerciseName, exerciseName,"",checkDefinedvar , listoftypes , progexType, user_data)

    elif "Pointers" in progexType:   
       feedback, peruserFilesPath= assessprogkaex(data,"Pointers/"+exerciseName, exerciseName,"",checkDefinedvar , listoftypes , progexType, user_data)
    return feedback, peruserFilesPath   

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#  All Programming exercises are compiled and run through the following function
def assessprogkaex(data, testfoldername, testfilenamep, generatedList, checkDefinedvar, listoftypes, progexType,user_data):
    print "=============="
    print settings 
    filesPath = settings.File_Path  + testfoldername+'/'
 
    testfilename = testfilenamep+".java"
    studentfilename = "student"+testfilename
    
    peruserFilesPath = filesPath + str(user_data.user.username)+'/'
    #print testfilenamep
    print peruserFilesPath 
    # count the number of lines in the original test file so that we can have the error shown to the student with respect to the student's code
    if progexType == "pointers":
      TestFile = open(filesPath+testfilenamep+"part1.java" , 'r')
      with TestFile:
        for i, l in enumerate(TestFile):
            pass
    else:
      TestFile = open(filesPath+testfilename , 'r')
      with TestFile:
        for i, l in enumerate(TestFile):
            pass
    
    
    feedback=[False, 'null', i+1 , studentfilename , 'class '+ studentfilename ]
    # Those are the datatypes that are not allowed to be defined in that exercise
    # The first one is already defined in the given code to the student 
    # so the student should not define more and the others should not be declared at all
    
    if not os.path.exists(peruserFilesPath ):
       os.makedirs(peruserFilesPath)
   
    #cleaning: deleting already created files
    if generatedList != 'null':
       if os.path.isfile(peruserFilesPath +'generatedlist'):
          os.remove(peruserFilesPath+'generatedlist')
       genlistfile = open(peruserFilesPath+'generatedlist', 'w')
       genlistfile.write(generatedList)
       genlistfile.close()

    if os.path.isfile(peruserFilesPath +''):
       os.remove(peruserFilesPath+studentfilename)
 
    if os.path.isfile(peruserFilesPath +'output'):
       os.remove(peruserFilesPath+'output')

    if os.path.isfile(peruserFilesPath +'compilationerrors.out'):
       os.remove(peruserFilesPath + 'compilationerrors.out')
   
    if os.path.isfile(peruserFilesPath +'runerrors.out'):
       os.remove(peruserFilesPath + 'runerrors.out')
    
    if os.path.isfile(peruserFilesPath +'newpolicy.policy'):
       os.remove(peruserFilesPath + 'newpolicy.policy')


    # Saving the submitted/received code in the studentrectest.java file by copying the preorder + studentcode +}
    
    

    

    if progexType == "pointers":
       TestFile = open(filesPath+testfilenamep+"part1.java" , 'r')
       test = TestFile.read()
       answer = open(peruserFilesPath+studentfilename, 'w')
       answer.write(test)
       TestFilepart2 = open(filesPath+testfilenamep+"part2.java" , 'r')
       testpart2 = TestFilepart2.read()
       answer.write(data) 
       answer.write(testpart2)
    else:
       TestFile = open(filesPath+testfilename , 'r')
       test = TestFile.read()
       answer = open(peruserFilesPath+studentfilename, 'w')
       answer.write(test)
       answer.write("public static ")
       answer.write(data)
       answer.write("}")
    answer.close()
    

    # create the policy file on the fly instead of having a static copy per exercise
    policyfile = open(peruserFilesPath+"newpolicy.policy" , 'w')
    policyfile.write('grant codeBase "file:'+ peruserFilesPath +'*" {')
    #policyfile.write('permission java.security.AllPermission;')
    policyfile.write('permission java.io.FilePermission "'+ peruserFilesPath +'output","read , write";')
    policyfile.write('permission java.io.FilePermission "'+ peruserFilesPath +'compilationerrors","read , write";')
    policyfile.write('permission java.io.FilePermission "'+ peruserFilesPath +'runerrors","read , write";')
    policyfile.write('permission java.io.FilePermission "'+ peruserFilesPath + studentfilename +'","read , write , execute";')
    policyfile.write('};')
    policyfile.close()

    # Run the Javac and java command to compile and test the submitted code
    proc1 = subprocess.Popen(" cd "+ peruserFilesPath +"; javac "+studentfilename+" 2> "+peruserFilesPath + "compilationerrors.out ; java -Djava.security.manager -Djava.security.policy==newpolicy.policy student"+testfilenamep+" 2> " + peruserFilesPath +"runerrors.out", stdout=subprocess.PIPE, shell=True)
   
    
    time.sleep(2) #Should change in the next push that to be in the java files instead of sleeping here
    #os.system("kill -9 "+ str(proc1.pid) )

    print data
    # Read the success file if has Success inside then "Well Done!" Otherwise "Try Again!"
    if  os.path.isfile(peruserFilesPath+'compilationerrors.out'):
          syntaxErrorFile = open(peruserFilesPath+'compilationerrors.out' , 'r')
          feedback[0] = False
          feedback[1]= syntaxErrorFile.readlines()
          syntaxErrorFile.close()
          if os.stat(peruserFilesPath+'compilationerrors.out')[6]!=0:
             feedback[1]= feedback[1]
             print feedback[1]
             if  feedback[1][0].find("Note:") == -1: # Ignore the warnings
                 NewList =  [x for x in feedback[1] if not x.startswith('Note:') ]
                 feedback[1] = NewList
                 return feedback , peruserFilesPath

    if checkDefinedvar == "True":
       datatypes= re.split(",", listoftypes )

    if checkDefinedvar == "True":
       if data.count(datatypes[0]) > 1 or (any( x in data for x in datatypes[1:len(datatypes)])):
          feedback[1]= ["Try Again! You should not declare any variables."]
          return feedback , peruserFilesPath

    if os.path.isfile(peruserFilesPath+'runerrors.out'):
       #Check what is returned from the test : what is inside the success file
          runErrorFile = open(peruserFilesPath+'runerrors.out' , 'r')
          feedback[0] = False
          feedback[1]= runErrorFile.readlines()
          print feedback[1]
          for line in feedback[1]:
              print "line" + line
              if "at java.security.AccessControlContext.checkPermission" in line:
                 feedback[1]= ["Try Again! Your solution shouldn't write files to the disk."]
                 return feedback , peruserFilesPath
              elif 'Exception in thread "main" java.lang.StackOverflowError' in line:
                 feedback[1]= ["Try Again! Your solution leads to infinite recursion!"]
                 return feedback , peruserFilesPath
              elif 'NullPointerException' in line and progexType == "binarytree":
		 feedback[1]= ["Try Again! You are trying to access a null node. You have forgotten to check if the node is null before accessing it. Have you checked if the root is null or not? if yes then ask your self the next question: are you trying to access the root's left or right children before the recursive call? You may need to revise your code and check if the solution really need to do that. If you have to get the value of one or both of the children before the recursive call then make sure to check if they are null or not."]
		 #return feedback
	      
              elif 'infinite recursion' in line:
                 feedback[1]= ["Try Again! You probably have infinite recursion."]
                 os.system("pkill -TERM -P"+ str(proc1.pid) ) # terminate all the processes because we need to terminate the thread as well
                 return feedback , peruserFilesPath
              elif 'Exception in thread "main"' in line:
		 feedback[1]= ["Try Again! Your solution leads to "+ line.replace("Exception in thread \"main\" java.lang.", "")]
                 return feedback , peruserFilesPath

          runErrorFile.close()
          if os.stat(peruserFilesPath+'runerrors.out')[6]!=0:
             return feedback, peruserFilesPath
    
    
    if os.path.isfile(peruserFilesPath+'output'):
       #Check what is returned from the test : what is inside the success file
       successFile = open(peruserFilesPath+'output' , 'r')
       feedback[1] = successFile.readlines()
       print feedback[1] 
       for line in feedback[1]:
		   # it is correct but..for recursion check they are doing it recursively
		   # it is correct but..for binary trees check they are doing it in the effecient way
           if "Well Done" in line: # static code analysis
	      if progexType == "BTRecurTutor": 
		   efficient,btineffFB = btcheckEfficientCode(data , testfilenamep)
		   if efficient == True:
	 	     feedback[0] = True
	 	     return feedback , peruserFilesPath
                   else:
		     feedback[0] = False
		     feedback[1]= btineffFB
		     return feedback , peruserFilesPath
					
              elif progexType =="Pointers": 
		    efficient,pntrineffFB = pntrcheckEfficientCode(data , testfilenamep)
		    if efficient == True:
	               feedback[0] = True
		       return feedback , peruserFilesPath
	            else:
		       feedback[0] = False
		       feedback[1]= pntrineffFB
		       return feedback , peruserFilesPath
					 
	      feedback[0] = True
	      return feedback , peruserFilesPath
               
           else:
              feedback[0] = False
              return feedback , peruserFilesPath

    feedback[1]=['Try Again Later!']
    return feedback , peruserFilesPath

                
