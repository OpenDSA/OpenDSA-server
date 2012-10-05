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

from opendsa.models import Exercise, UserExercise, UserExerciseLog, UserData, UserButton, UserModule, Module
from django.conf.urls.defaults import patterns, url
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.utils import simplejson
from django.contrib.sessions.models import Session



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


def update_module_proficiency(user_data, module):

    db_module = Module.objects.get(name=module)
    module_ex_list = db_module.get_proficiency_model() 
    user_prof = user_data.get_prof_list() 
    user_module, exist =  UserModule.objects.get_or_create(user=user_data.user, module=db_module)
    dt_now = datetime.datetime.now()
    if user_module: 
        if user_module.first_done == None:
            user_module.first_done = dt_now
        user_module.last_done = dt_now
        if user_module.proficient_date == datetime.datetime.strptime('2012-01-01 00:00:00','%Y-%m-%d %H:%M:%S'):
            if set(module_ex_list).issubset(set(user_prof)):
                user_module.proficient_date = dt_now 
                user_module.save()
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
        if str2bool(completed):

            user_exercise.total_done += 1

            if problem_log.correct:

                proficient = user_data.is_proficient_at(user_exercise.exercise)


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
               user_exercise.streak = 0 #user_exercise.streak - 1 
            user_exercise.progress = Decimal(user_exercise.streak)/Decimal(user_exercise.exercise.streak)
            if first_response:
                   user_exercise.update_proficiency_model(correct=False)
                   bingo(['hints_wrong_problems', 'struggling_problems_wrong'])
        
        update_module_proficiency(user_data, module)
        problem_log.save()
        user_exercise.save() 
        return user_exercise,True      #, user_exercise_graph, goals_updated



def attempt_problem_pe(user_data, user_exercise, attempt_number,
    completed, time_taken, fix, undo, correct, student, total, module, ip_address):

    if user_exercise:   # and user_exercise.belongs_to(user_data):
        print user_exercise
        dt_now = datetime.datetime.now()
        exercise = user_exercise.exercise
        user_exercise.last_done = dt_now
        count_hints=0
        # Build up problem log for deferred put
        problem_log = models.UserExerciseLog(
                user=user_data,
                exercise=user_exercise.exercise,
                time_taken=time_taken,
                time_done=dt_now,
                count_hints=count_hints,
                hint_used=int(count_hints) > 0,
                correct=correct>= total,
                count_attempts=attempt_number,
                ip_address=ip_address,
        )



        just_earned_proficiency = False


        user_exercise.total_done += 1
        value = False
        if problem_log.correct:

                proficient = user_data.is_proficient_at(user_exercise.exercise)

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
        update_module_proficiency(user_data, module)
        return user_exercise.save(),value  



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

        
