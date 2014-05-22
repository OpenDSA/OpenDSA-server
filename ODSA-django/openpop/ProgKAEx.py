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
import time


#from subprocess import call
#import pdb; pdb.set_trace()

def attempt_problem_pop(user_data, user_exercise, attempt_number,
    completed, count_hints, time_taken, attempt_content, module,   
    ex_question, ip_address, request_post):
    
    #reload(sys)
    #sys.setdefaultencoding("utf8")
    #student code
    data = request_post.get('code') 
    generatedList =request_post.get('genlist')
    data = ''.join([x for x in data if ord(x) < 128]) 
    
    #  Check from which programming exercise we got this request
    if request_post.get('sha1') == "BinaryTreePROG" : #count number of nodes
       feedback= assessprogkaex (data, "binarytreetest","")
    elif request_post.get('sha1') == "BTLeafPROG" :  #count number of leaf nodes
       feedback= assessprogkaex (data , "btleaftest","")      
    elif request_post.get('sha1') == "ListADTPROG":  #generate a list
       feedback= assessprogkaex(data , "listadttest", generatedList)
    #recursion programming exercises
    elif request_post.get('sha1') == "RecWBCProg":   
       feedback= assessprogkaex(data,"rectest","")
    
       
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
                ex_question=ex_question,
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
        #else:
            #if (int(count_hints) ==0) and (attempt_content!='hint') and (int(attempt_number) == 1):
            # Only count wrong answer at most once per problem
             #  if user_exercise.streak - 1 > 0:
             #      user_exercise.streak = user_exercise.streak - 1
             #  else:
             #      user_exercise.streak = 0
            #user_exercise.progress = Decimal(user_exercise.streak)/Decimal(user_exercise.exercise.streak)
            #if first_response:
            #       user_exercise.update_proficiency_model(correct=False)

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
        return user_exercise,feedback     #, user_exercise_graph, goals_updated




#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#  Programming exercises
def assessprogkaex(data, testfoldername, generatedList ):
    
    filesPath = '/home/OpenDSA-server-beta/OpenDSA-server/ODSA-django/openpop/build/'+testfoldername+'/javaSource/'
    
    testfilename = testfoldername+".java"
    studentfilename = "student"+testfilename
    
    # count the number of lines in the original test file so that we can have the error shown to the student with respect to the student's code
    TestFile = open(filesPath+testfilename , 'r')
    with TestFile:
        for i, l in enumerate(TestFile):
            pass
    print i+1 
    
    feedback=[False, 'null', i+1 , studentfilename , 'class '+ studentfilename]
            
    #cleaning: deleting already created files
    if generatedList != 'null':
       if os.path.isfile(filesPath +'generatedlist'):
          os.remove(filesPath+'generatedlist')
       genlistfile = open(filesPath+'generatedlist', 'w')
       genlistfile.write(generatedList)
       genlistfile.close()

    if os.path.isfile(filesPath +''):
       os.remove(filesPath+studentfilename)
 
    if os.path.isfile(filesPath +'output'):
       os.remove(filesPath+'output')

    if os.path.isfile(filesPath +'compilationerrors.out'):
       os.remove(filesPath + 'compilationerrors.out')
   
    if os.path.isfile(filesPath +'runerrors.out'):
       os.remove(filesPath + 'runerrors.out')

   
    # Saving the submitted/received code in the studentrectest.java file by copying the preorder + studentcode +}
    TestFile = open(filesPath+testfilename , 'r')
    test = TestFile.read()
    answer = open(filesPath+studentfilename, 'w')
    answer.write(test)
    answer.write("public static ")
    answer.write(data)
    answer.write("}")
    answer.close()
    
    # Setting the DISPLAY then run the processing command to test the submitted code
    proc1 = subprocess.Popen(" cd /home/OpenDSA-server-beta/OpenDSA-server/ODSA-django/openpop/build/"+testfoldername+"/javaSource/; javac "+studentfilename+" 2> /home/OpenDSA-server-beta/OpenDSA-server/ODSA-django/openpop/build/"+testfoldername+"/javaSource/compilationerrors.out ; java -Djava.security.manager -Djava.security.policy==newpolicy.policy student"+testfoldername+" 2> /home/OpenDSA-server-beta/OpenDSA-server/ODSA-django/openpop/build/"+testfoldername+"/javaSource/runerrors.out", stdout=subprocess.PIPE, shell=True)
    #(out1, err1) = proc1.communicate() 
    #subprocess.call("cd /home/OpenDSA-server/ODSA-django/openpop; ./try.sh", shell=True)
    time.sleep(3)
    os.system("kill -9 "+ str(proc1.pid) )

    print data
    # Read the success file if has Success inside then "Well Done!" Otherwise "Try Again!"
    if  os.path.isfile(filesPath+'compilationerrors.out'):
          syntaxErrorFile = open(filesPath+'compilationerrors.out' , 'r')
          feedback[0] = False
          feedback[1]= syntaxErrorFile.readlines()
          syntaxErrorFile.close()
          if os.stat(filesPath+'compilationerrors.out')[6]!=0:
             feedback[1]= feedback[1]#.rsplit(':',1)[1]
             print feedback[1]
             return feedback
    if os.path.isfile(filesPath+'runerrors.out'):
       #Check what is returned from the test : what is inside the success file
          runErrorFile = open(filesPath+'runerrors.out' , 'r')
          feedback[0] = False
          feedback[1]= runErrorFile.readlines()
          print feedback[1]
          for line in feedback[1]:
              print "line" + line
              if "at java.security.AccessControlContext.checkPermission" in line:
                 feedback[1]= ["Try Again! Your solution shouldn't write files to the disk!"]
                 return feedback    
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
              return feedback
               
           else :
              feedback[0] = False
              return feedback

    feedback[1]=['Try Again! Your code is taking too long to run! Revise your code!']
    return feedback
                
