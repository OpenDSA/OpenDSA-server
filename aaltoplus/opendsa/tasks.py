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

from opendsa.models import Exercise, UserExercise, UserExerciseLog, UserData, UserButton, UserModule, Module, Books, UserSummary, ExerciseModule 
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

@task()
@periodic_task(run_every=crontab(hour="*", minute="*/30", day_of_week="*"))
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
            u_summary1 = models.UserSummary(
                grouping = grouping,
                key = ex.name,
                value = '-1',
            )
            u_summary1.save()
         cur_user = u_exe.user
         grouping += 1
         del u_exe_list[:]

      if not UserSummary.objects.filter(value=u_exe.user.username):
         u_summary = models.UserSummary(
              grouping = grouping,
              key = 'user',
              value = u_exe.user.username,
         )
         u_summary.save()
      else:
         if u_exe.is_proficient():
             value = '1'
         else:
             value = '0'
         u_summary1 = models.UserSummary(
              grouping = grouping,
              key = u_exe.exercise.name,
              value = value,
         )
         u_summary1.save()
      u_exe_list.append(u_exe.exercise.id)
   u_exe_list.append(u_exe.exercise.id)
   exe_not_started = diff(set(exe_list),set(u_exe_list))
   for ex in exe_not_started:
       u_summary1 = models.UserSummary(
            grouping = grouping,
            key = ex.name,
            value = '-1',
       )
       u_summary1.save()


@task()
@periodic_task(run_every=crontab(hour="*", minute="*/5", day_of_week="*"))
def exercise_module():
   #we empty the table first
   cursor = connection.cursor()
   cursor.execute("TRUNCATE TABLE `opendsa_exercisemodule`")
   exercises = Exercise.objects.all() 
   modules = Module.objects.all() 

   for exer in exercises: 
      for mod in modules: 
         if exer.id in mod.get_proficiency_model() : 
             ex_mod = models.ExerciseModule(
                  exercise = exer.name,
                  module = mod.name,
             )
             ex_mod.save()
         else: 
             ex_mod = models.ExerciseModule(
                  exercise = exer.name,
                  module = "",
             )
             ex_mod.save()

