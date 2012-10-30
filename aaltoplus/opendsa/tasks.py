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

from opendsa.models import Exercise, UserExercise, UserExerciseLog, UserData, UserButton, \
                           UserModule, Module, Books, UserSummary, ExerciseModule, UserModuleSummary, BookModuleExercise 
from django.conf.urls.defaults import patterns, url
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.utils import simplejson
from django.contrib.sessions.models import Session
from django.db import connection

#Celery task
#from celery import Celery
from celery import task 
from celery.task.schedules import crontab  
from celery.decorators import periodic_task 


def diff(a, b):
    b = set(b)
    return [aa for aa in a if aa not in b]

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")


def get_pe_name_from_referer(referer):
    tab = referer.split('/')
    return tab[len(tab)-1].split('.')[0]

def date_from_timestamp(tstamp):
    date = datetime.datetime.fromtimestamp(tstamp/1000)
    return date.strftime('%Y-%m-%d %H:%M:%S')

def make_wrong_attempt(user_data, user_exercise):
    if user_exercise and user_exercise.belongs_to(user_data):
        user_exercise.update_proficiency_model(correct=False)
        user_exercise.put()

        return user_exercise





@task()
@periodic_task(run_every=crontab(hour="*", minute="*/5", day_of_week="*"))
def book_module_exercise():

   modules = Module.objects.all() 
   book = Books.objects.get(book_name="Fall2012")  
   for mod in modules:
      exe_list = mod.get_proficiency_model()
      for exer in exe_list:
          if len( Exercise.objects.filter(id=exer))>0:
             bme = BookModuleExercise(  
                      book= book,
                      module= mod,
                      exercise = Exercise.objects.get(id=exer) 
             )    
             bme.save()  


@task()
@periodic_task(run_every=crontab(hour="*", minute="*/8", day_of_week="*"))
def student_summary():

   #we empty the table first
   cursor = connection.cursor()
   cursor.execute("TRUNCATE TABLE `opendsa_usersummary`")

   user_exercises = UserExercise.objects.order_by('user').all()
   exercises =Exercise.objects.all()
   exe_list = []
   u_exe_list = []

   cur_user = 0
   grouping = 0
   for exer in exercises:
      exe_list.append(exer)
   for u_exe in user_exercises:
      #u_exe_list.append(u_exe.exercise.id)
      if cur_user != u_exe.user and grouping == 0:
         cur_user = u_exe.user
         grouping += 1
         #u_exe_list.append(u_exe.exercise)
      elif cur_user != u_exe.user and grouping != 0:
         exe_not_started = diff(set(exe_list),set(u_exe_list))
         for ex in exe_not_started:
            if len(UserSummary.objects.filter(grouping=grouping, key=ex.name))==0 and ex.name!="":
               u_summary1 = models.UserSummary(
                   grouping = grouping,
                   key = ex.name,
                   value = '-1',
               )
               u_summary1.save()
         cur_user = u_exe.user
         grouping += 1
         del u_exe_list[:]
      if u_exe.is_proficient():
             value = '1'
      else:
             value = '0'

      if not UserSummary.objects.filter(value=u_exe.user.username):
         u_summary = models.UserSummary(
              grouping = grouping,
              key = 'user',
              value = u_exe.user.username,
         )
         u_summary.save()
         if u_exe.exercise.name !="":
            u_summary2 = models.UserSummary(
                   grouping = grouping,
                   key = u_exe.exercise.name,
                   value = value,
            )
            u_summary2.save()
      else:
         if len(UserSummary.objects.filter(grouping=grouping, key=u_exe.exercise.name))==0:
            u_summary1 = models.UserSummary(
                 grouping = grouping,
                 key = u_exe.exercise.name,
                 value = value,
            )
            u_summary1.save()
         else:
            u_summary1 = UserSummary.objects.filter(grouping=grouping, key=u_exe.exercise.name)[0]
            if int(u_summary1.value)<int(value):  
               u_summary1.value = value
               u_summary1.save()  
      u_exe_list.append(u_exe.exercise.id)
   u_exe_list.append(u_exe.exercise.id)
   exe_not_started = diff(set(exe_list),set(u_exe_list))
   for ex in exe_not_started:
       if len(UserSummary.objects.filter(grouping=grouping, key=ex.name))==0 and ex.name!="":
          u_summary1 = models.UserSummary(
               grouping = grouping,
               key = ex.name,
               value = '-1',
          )
          u_summary1.save()


#given a user exercise activity list returs 3 list conataining not started, started and proficient exercises respectively.
def exercise_list_split(u_exe_list, mod):
    prof =[]
    started = []
    notstart = []
    exe_in_table = []
    for ue in u_exe_list:
       if ue.exercise.id in mod.get_proficiency_model():
          exe_in_table.append(ue.exercise.name)  
          if ue.is_proficient:
             prof.append(ue.exercise.name)
          else:
             started.append(ue.exercise.name)
    for mod_exe in mod.get_proficiency_model():
          if mod_exe not in prof and mod_exe not in started and len(Exercise.objects.filter(id=mod_exe))>0: 
              notstart.append(Exercise.objects.filter(id=mod_exe)[0].name)
    return notstart, started, prof  

@task()
@periodic_task(run_every=crontab(hour="*", minute="*/5", day_of_week="*"))
def student_module_summary():

   #we empty the table first
   cursor = connection.cursor()
   cursor.execute("TRUNCATE TABLE `opendsa_usermodulesummary`")
  
   users = User.objects.all()
   modules = Module.objects.all()
   exercises = Exercise.objects.all() 
   for user in users: 
       for mod in modules:
           if len(UserModule.objects.filter(user=user,module=mod))==0: #module not started
               if mod.exercise_list=="":
                  exe_list ='None' 
               u_mod_s = models.UserModuleSummary( 
                       user = user.username,
                       module = mod.name,
                       module_status = "-1",
                       proficient_exe = "",
                       started_exe = "",
                       notstarted_exe = exe_list,
               )
               u_mod_s.save()
           else:  
               u_mod = UserModule.objects.get(user=user,module=mod)
               if u_mod.is_proficient_at():
                   stat = "1"
               else:
                   stat = "0"
               u_exe = UserExercise.objects.filter(user=user)
               notstart, start, prof = exercise_list_split(u_exe, mod) 
               
               u_mod_s = models.UserModuleSummary(
                       user = user.username,
                       module = mod.name,
                       module_status = stat,
                       first_done = u_mod.first_done,
                       last_done = u_mod.last_done,
                       proficient_date = u_mod.proficient_date,
                       proficient_exe = ",".join(prof),
                       started_exe = ",".join(start),
                       notstarted_exe = ",".join(notstart),
               )
               u_mod_s.save()


     





@task()
@periodic_task(run_every=crontab(hour="*/3", minute="0", day_of_week="*"))
def exercise_module():
   #we empty the table first
   cursor = connection.cursor()
   cursor.execute("TRUNCATE TABLE `opendsa_exercisemodule`")
   exercises = Exercise.objects.all() 
   modules = Module.objects.all() 

   for exer in exercises: 
      for mod in modules: 
         if exer.id in mod.get_proficiency_model() and  exer.name!='' and  mod.name!='': 
             ex_mod = models.ExerciseModule(
                  exercise = exer.name,
                  module = mod.name,
             )
             ex_mod.save()


@task()
@periodic_task(run_every=crontab(hour="*", minute="*/5", day_of_week="*"))
def compute_points():

   user_data = UserData.objects.all()
   book = Books.objects.get(book_name="Fall2012")
   for u_data in user_data:
      grade = 0 
      prof_list = u_data.get_prof_list()
      for exercise_id in prof_list:
          exercise = Exercise.objects.get(id=exercise_id)
          if exercise.ex_type == 'ss':
                 points = Decimal(book.ss_points)
          elif exercise.ex_type == 'pe':
                 points = Decimal(book.pe_points)
          elif exercise.ex_type == 'ka':
                 points = Decimal(book.ka_points)
          elif exercise.ex_type == 'ot':
                 points = Decimal(book.ot_points)
          elif exercise.ex_type == 'pr':
                 points = Decimal(book.pr_points)
          else:
                 points = 0 
          grade += points
      u_data.points = Decimal(format(Decimal(grade), '.2f'))  #grade 
      u_data.save()
