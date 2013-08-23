# Create your views here.
from opendsa.models import  UserExercise, UserExerciseLog, UserData
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
#from subprocess import call
#import pdb; pdb.set_trace()

def attempt_problem_pop(user_data, user_exercise, attempt_number,
    completed, count_hints, time_taken, attempt_content, module,   
    ex_question, ip_address, request_post):
    
    data = request_post.get('code') 
    generatedList =request_post.get('genlist')
    # Will have here a check from which programming exercise we got this request
    # Temp: will use generated list --- if it has binarytree not a list then call the binary tree
    if generatedList == "Binarytree" :
       feedback= assesskaexbintree (data)
    else : # should have many else and if here by time 
       feedback= assesskaex(data , generatedList)

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

        problem_log.save()
        user_exercise.save()
        user_data.save()
        if proficient or problem_log.earned_proficiency:
            update_module_proficiency(user_data, module, user_exercise.exercise)

       
        return user_exercise,feedback     #, user_exercise_graph, goals_updated


def assesskaex(data , generatedList):
    
    print generatedList
    feedback=[False, 'null']
    #print feedback
    #filesPath = '/home/OpenPOP/Backend/visualize/build/ListTest/javaSource/'
    filesPath = '/home/aalto-beta/ODSA-django/openpop/build/ListTest/javaSource/'
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
    #proc1 = subprocess.Popen(" cd /home/OpenPOP/Backend/visualize/build/ListTest/javaSource/; javac studentlisttest.java 2> /home/OpenPOP/Backend/visualize/build/ListTest/javaSource/compilationerrors.out ; java studentlisttest 2> /home/OpenPOP/Backend/visualize/build/ListTest/javaSource/runerrors.out", stdout=subprocess.PIPE, shell=True)
    proc1 = subprocess.Popen(" cd /home/aalto-beta/ODSA-django/openpop/build/ListTest/javaSource/; javac studentlisttest.java 2> /home/aalto-beta/ODSA-django/openpop/build/ListTest/javaSource/compilationerrors.out ; java studentlisttest 2> /home/aalto-beta/ODSA-django/openpop/build/ListTest/javaSource/runerrors.out", stdout=subprocess.PIPE, shell=True)
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
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Assessing binary tree exercise
def assesskaexbintree (data):
    feedback=[False, 'null']
    filesPath = '/home/aalto-beta/ODSA-django/openpop/build/TreeTest/javaSource/'
    
    #cleaning: deleting already created files
    if os.path.isfile(filesPath +'studentpreordertest.java'):
       os.remove(filesPath+'studentpreordertest.java')
 
    if os.path.isfile(filesPath +'output'):
       os.remove(filesPath+'output')

    if os.path.isfile(filesPath +'compilationerrors.out'):
       os.remove(filesPath + 'compilationerrors.out')
   
    if os.path.isfile(filesPath +'runerrors.out'):
       os.remove(filesPath + 'runerrors.out')

   
    # Saving the submitted/received code in the studentpreordertest.java file by copying the preorder + studentcode +}
    BTTestFile = open(filesPath+'PreorderTest.java' , 'r')
    BTtest = BTTestFile.read()
    answer = open(filesPath+'studentpreordertest.java', 'w')
    answer.write(BTtest)
    answer.write("public static")
    answer.write(data.decode('utf-8'))
    answer.write("}")
    answer.close()
    
    # Setting the DISPLAY then run the processing command to test the submitted code
    proc1 = subprocess.Popen(" cd /home/aalto-beta/ODSA-django/openpop/build/TreeTest/javaSource/; javac studentpreordertest.java 2> /home/aalto-beta/ODSA-django/openpop/build/TreeTest/javaSource/compilationerrors.out ; java studentpreordertest 2> /home/aalto-beta/ODSA-django/openpop/build/TreeTest/javaSource/runerrors.out", stdout=subprocess.PIPE, shell=True)
    (out1, err1) = proc1.communicate() 
    
    print data
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

    return feedback
        
