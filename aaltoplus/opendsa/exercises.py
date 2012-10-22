import re
import os
import itertools
import hashlib
import urllib
import logging


import datetime
import models
import simplejson as json
import time
from decimal import Decimal
import jsonpickle 
import math

from opendsa.models import Exercise, UserExercise, UserExerciseLog, UserData, UserButton, UserModule, Module, Books, UserSummary
from django.conf.urls.defaults import patterns, url
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.utils import simplejson
from django.contrib.sessions.models import Session
from django.db import connection

def diff(a, b):
    b = set(b)
    return [aa for aa in a if aa not in b]

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")


def get_pe_name_from_referer(referer):
    tab = referer.split('/')
    print tab[len(tab)-1].split('.')[0] 
    return tab[len(tab)-1].split('.')[0]

def date_from_timestamp(tstamp):
    date = datetime.datetime.fromtimestamp(tstamp/1000)
    return date.strftime('%Y-%m-%d %H:%M:%S')

def make_wrong_attempt(user_data, user_exercise):
    if user_exercise and user_exercise.belongs_to(user_data):
        user_exercise.update_proficiency_model(correct=False)
        user_exercise.put()

        return user_exercise


def student_grade_all(user):

    #prof_list = user_data.get_prof_list()
    student_data_id = UserSummary.objects.get(value = user.username)
    student_data = UserSummary.objects.filter(grouping = student_data_id.grouping)  
    book = Books.objects.get(book_name="Fall2012")   #book name will be later send by the frontend
    modules =  Module.objects.all()
    user_grade = {}
    grade = []
    for u_data in student_data:
        if u_data.key != 'name' and  len(Exercise.objects.filter(name=u_data.key))==1:
           ex = Exercise.objects.get(name=u_data.key)
           for mod in modules:
              if ex.id in mod.get_proficiency_model():
                 module_name = mod.name    
           if ex.ex_type == 'ss':
              points = Decimal(book.ss_points)
           elif ex.ex_type == 'pe':
              points = Decimal(book.pe_points)
           elif ex.ex_type == 'ka':
              points = Decimal(book.ka_points)
           else:
              points = Decimal(book.ss_points)
           if int(u_data.value) != 1:
              points = 0
           grade.append({'exercise':ex.name, 'description':ex.description,'type':ex.ex_type,'points':points,'module':module_name})
    user_grade['max_points'] = {"ss":book.ss_points,"ka":book.ka_points,"pe":book.pe_points}
    user_grade['grades'] = grade
    return user_grade


 
def student_grade(user_data):

    prof_list = user_data.get_prof_list()
    book = Books.objects.get(book_name="Fall2012")   #book name will be later send by the frontend
    modules =  Module.objects.all()
    user_grade = {}
    grade = []
    for ex_prof in prof_list:
        ex = Exercise.objects.get(id=ex_prof)
        for mod in modules:
            if ex.id in mod.get_proficiency_model(): 
               module_name = mod.name
        if ex.ex_type == 'ss':
            points = Decimal(book.ss_points)
        elif ex.ex_type == 'pe':
            points = Decimal(book.pe_points)
        elif ex.ex_type == 'ka':
            points = Decimal(book.ka_points)
        else:
            points = Decimal(book.ss_points)
        grade.append({'exercise':ex.name, 'description':ex.description,'type':ex.ex_type,'points':points,'module':module_name})  
    user_grade['headers'] = {"ss":"Slideshow","ka":"MCQ","pe":"Proficiency Ex."}
    user_grade['grades'] = grade 
    return user_grade

def update_module_proficiency(user_data, module, exercise):
      
    db_module = Module.objects.get(name=module)
    module_ex_list = db_module.get_proficiency_model() 
    user_prof = user_data.get_prof_list() 
    user_module, exist =  UserModule.objects.get_or_create(user=user_data.user, module=db_module)
    dt_now = datetime.datetime.now()
    if user_module: 
        if user_module.first_done == None:
            user_module.first_done = dt_now
        user_module.last_done = dt_now
#        print 'diff == %s - Exercise == %s\n' %(diff(set(module_ex_list),set(user_prof)),[int(exercise.id)])
#        print  '%s' %(diff(set(module_ex_list),set(user_prof))==[exercise.id])
        print 'value %s' %(user_module.proficient_date == datetime.datetime.strptime('2012-01-01 00:00:00','%Y-%m-%d %H:%M:%S'))
        if user_module.proficient_date == datetime.datetime.strptime('2012-01-01 00:00:00','%Y-%m-%d %H:%M:%S'):
            if exercise is not None: 
               is_last_exercise = diff(set(module_ex_list),set(user_prof))==[exercise.id]
            else:
               is_last_exercise = False 
            if (set(module_ex_list).issubset(set(user_prof))) or is_last_exercise:
                print 'value1'
                user_module.proficient_date = dt_now 
                user_module.save()
                print 'updated'  
                return True
            else:
                user_module.save()
                return False
        user_module.save()   
        return True 
    return False

    

def attempt_problem(user_data, user_exercise, attempt_number,
    completed, count_hints, time_taken, attempt_content, module, 
    ip_address):

    if user_exercise:   # and user_exercise.belongs_to(user_data):
        dt_now = datetime.datetime.now()
        #exercise = user_exercise.exercise 
        user_exercise.last_done = dt_now
        # Build up problem log for deferred put
        problem_log = models.UserExerciseLog(
                user=user_data, 
                exercise=user_exercise.exercise,
                time_taken=time_taken,
                time_done=dt_now,
                count_hints=count_hints,
                hint_used=int(count_hints) > 0,
                correct=str2bool(completed) and not str2bool(count_hints) and (int(attempt_number) == 1),
                count_attempts=attempt_number,
                ip_address=ip_address,
        )


        first_response = (attempt_number == 1 and count_hints == 0) or (count_hints == 1 and attempt_number == 0)

        if user_exercise.total_done > 0 and user_exercise.streak == 0 and first_response:
            bingo('hints_keep_going_after_wrong')

        just_earned_proficiency = False

        # Users can only attempt problems for themselves, so the experiment
        # bucket always corresponds to the one for this current user
        #struggling_model = StrugglingExperiment.get_alternative_for_user(
        #         user_data, current_user=True) or StrugglingExperiment.DEFAULT
        proficient = user_data.is_proficient_at(user_exercise.exercise)  
        if str2bool(completed):

            user_exercise.total_done += 1
            #proficient = user_data.is_proficient_at(user_exercise.exercise)
            if problem_log.correct:

                #proficient = user_data.is_proficient_at(user_exercise.exercise)


                problem_log.points_earned +=1   #points.ExercisePointCalculator(user_exercise[0], suggested, proficient)
                # Streak only increments if problem was solved correctly (on first attempt)
                user_exercise.total_correct += 1
                user_exercise.streak += 1
                user_exercise.longest_streak = max(user_exercise.longest_streak, user_exercise.streak)
                user_exercise.progress = Decimal(user_exercise.streak)/Decimal(user_exercise.exercise.streak)  
                if not proficient: 
                        problem_log.earned_proficiency = user_exercise.update_proficiency_ka(correct=True)
                #if problem_log.earned_proficiency:
                #    update_module_proficiency(user_data, module)
            else:  
                user_exercise.total_done += 1
                user_exercise.progress = Decimal(user_exercise.streak)/Decimal(user_exercise.exercise.streak) 
        else:
            if ((int(count_hints) ==0) or (attempt_content!='hint')):
            # Only count wrong answer at most once per problem
               if user_exercise.streak - 1 > 0:
                   user_exercise.streak = user_exercise.streak - 1
               else:
                   user_exercise.streak = 0
            user_exercise.progress = Decimal(user_exercise.streak)/Decimal(user_exercise.exercise.streak)
            if first_response:
                   user_exercise.update_proficiency_model(correct=False)
                   bingo(['hints_wrong_problems', 'struggling_problems_wrong'])
        
        problem_log.save()
        user_exercise.save() 
        if proficient or problem_log.earned_proficiency:
            update_module_proficiency(user_data, module, user_exercise.exercise)
        return user_exercise,True      #, user_exercise_graph, goals_updated



def attempt_problem_pe(user_data, user_exercise, attempt_number,
    completed, time_taken, fix, undo, correct, student, total, module, ip_address):

    if user_exercise:   # and user_exercise.belongs_to(user_data):
        print user_exercise
        dt_now = datetime.datetime.now()
        exercise = user_exercise.exercise
        user_exercise.last_done = dt_now
        count_hints=0
        print ' exercise.name %s' %exercise.name
        print ' exercise.streak %s' %exercise.streak
        print ' total %s-\n' %total
        print ' correct %s' %correct
        print 'threshold  %s-\n' %((Decimal(exercise.streak)/100) * int(total))
        threshold = (Decimal(exercise.streak)/100) * int(total)
        # Build up problem log for deferred put
        problem_log = models.UserExerciseLog(
                user=user_data,
                exercise=user_exercise.exercise,
                time_taken=time_taken,
                time_done=dt_now,
                count_hints=count_hints,
                hint_used=int(count_hints) > 0,
                correct=correct>= threshold,  
                count_attempts=attempt_number,
                ip_address=ip_address,
        )



        just_earned_proficiency = False


        user_exercise.total_done += 1
        value = False
        proficient = user_data.is_proficient_at(user_exercise.exercise)
        if problem_log.correct:

                #proficient = user_data.is_proficient_at(user_exercise.exercise)

                problem_log.points_earned = total   
                user_exercise.total_correct += 1
                user_exercise.longest_streak = max(user_exercise.longest_streak, total)
                value = True  
                if not proficient:
                   #if(total>=user_exercise.streak):
                        problem_log.earned_proficiency =  user_exercise.update_proficiency_pe(correct=True) 

        problem_log.save()  
        pe_log = models.UserProfExerciseLog( 
                                             problem_log=problem_log,  #user_exercise,
                                             student = student,
                                             correct = correct,
                                             fix =fix,
                                             undo = undo, 
                                             total = total)

        pe_log.save() 
        user_exercise.save() 
        if proficient or problem_log.earned_proficiency:
            update_module_proficiency(user_data, module, user_exercise.exercise)
        return user_exercise,value  



def log_button_action( user, exercise, module, name, description, action_time, ip_address):
    button_log = models.UserButton(
                        user = user,
                        exercise = exercise,
                        module = module,
                        name = name,
                        description = description,
                        action_time =  date_from_timestamp(action_time),
                        ip_address = ip_address) 




    return button_log.save(),True  

        
