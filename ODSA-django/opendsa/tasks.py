import re
import os
import itertools
import hashlib
import urllib
import logging


import datetime
from datetime import timedelta
import models
import simplejson as json
import time
from decimal import Decimal
import jsonpickle
import math

from opendsa.models import Exercise, UserExercise, UserExerciseLog, UserData, UserButton, \
                           UserModule, Module, Books, BookModuleExercise 
from django.conf.urls.defaults import patterns, url
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.utils import simplejson
from django.contrib.sessions.models import Session
from django.db import connection

from celery import task 
from celery.task.schedules import crontab  
from celery.decorators import periodic_task 
from django.conf import settings

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
@periodic_task(run_every=crontab(hour="*", minute="*/15", day_of_week="*"))
def user_exercises():
    now = datetime.datetime.now()
    yesterday = now - timedelta(1)    
    c_user = 0
    c_exer = 0
    #c_user = User.objects.all().count()
    user_reg_log = User.objects.raw('''SELECT id, COUNT(id) As regs,
                                                      DATE(date_joined) As date
                                                      FROM auth_user
                                                      WHERE DATE(date_joined) = %s
                                                      GROUP BY date
                                                      ORDER BY date ASC''',[yesterday.date().strftime('%Y-%m-%d')])
    all_exe_log = UserExerciseLog.objects.raw('''SELECT id, COUNT(exercise_id) AS exe, 
                                                             DATE(time_done) AS date
                                                      FROM  opendsa_userexerciselog 
                                                      WHERE DATE(time_done) = %s
                                                      GROUP BY date 
                                                      ORDER BY date ASC''',[yesterday.date().strftime('%Y-%m-%d')])
   
    for url in user_reg_log: 
        if not url.is_staff: 
            c_user+=1

    #c_exer = UserExerciseLog.objects.all().count()
    for ael in all_exe_log:
        c_exer += ael.exe

    #write data into a file
    try:
        json_data = open(settings.MEDIA_ROOT + 'widget_stats.json')
        data = json.load(json_data)
        data['users'] = int(data['users']) + c_user 
        data['exercises'] = int(data['exercises']) + c_exer

        ofile = open(settings.MEDIA_ROOT + 'widget_stats.json','w')
        ofile.writelines(str(data).replace("'",'"'))
        ofile.close
    except IOError as e:
        print "error ({0}) written file : {1}".format(e.errno, e.strerror)


@task()
@periodic_task(run_every=crontab(hour="1", minute="0", day_of_week="*"))
def class_data():
    
    day_list = []
    now = datetime.datetime.now()
    yesterday = now - timedelta(1)
    day_list.append(yesterday)

    #distinct user exercise attempts
    user_day_log = UserExerciseLog.objects.raw('''SELECT id, COUNT(DISTINCT user_id) As users,
                                                         DATE(time_done) As date
                                                  FROM opendsa_userexerciselog
                                                  WHERE DATE(time_done) = %s 
                                                  GROUP BY date
                                                  ORDER BY date ASC''', [yesterday.date().strftime('%Y-%m-%d')])
    #user registration per day 
    user_reg_log = User.objects.raw('''SELECT id, COUNT(id) As regs,
                                                      DATE(date_joined) As date
                                                      FROM auth_user
                                                      WHERE DATE(date_joined) = %s
                                                      GROUP BY date
                                                      ORDER BY date ASC''', [yesterday.date().strftime('%Y-%m-%d')])
    #user usage per day (interactions)
    user_use_log = UserButton.objects.raw('''SELECT id, COUNT(user_id) As users,
                                                             DATE(action_time) As date
                                                      FROM opendsa_userbutton
                                                      WHERE DATE(action_time) = %s
                                                      GROUP BY date
                                                      ORDER BY date ASC''', [yesterday.date().strftime('%Y-%m-%d')])

    #distinct all proficiency per day per exercise
    all_prof_log = UserExerciseLog.objects.raw('''SELECT id, COUNT(earned_proficiency) AS profs,
                                                          DATE(time_done) AS date
                                                   FROM  opendsa_userexerciselog 
                                                   WHERE earned_proficiency = 1 AND DATE(time_done) = %s
                                                   GROUP BY date   
                                                   ORDER BY date ASC''', [yesterday.date().strftime('%Y-%m-%d')])

    #number of exercises attempted
    all_exe_log = UserExerciseLog.objects.raw('''SELECT id, COUNT(exercise_id) AS exe, 
                                                             DATE(time_done) AS date
                                                      FROM  opendsa_userexerciselog 
                                                      WHERE DATE(time_done) = %s
                                                      GROUP BY date 
                                                      ORDER BY date ASC''', [yesterday.date().strftime('%Y-%m-%d')])

   #total number of ss 
    all_ss_log = UserExerciseLog.objects.raw('''SELECT `opendsa_userexerciselog`.`id`, COUNT(`opendsa_userexerciselog`.`exercise_id`) AS ss_exe,
                                                       DATE(`opendsa_userexerciselog`.`time_done`)  AS date 
                                                       FROM `opendsa_userexerciselog`
                                                       JOIN `opendsa_exercise`
                                                       ON `opendsa_userexerciselog`.`exercise_id` = `opendsa_exercise`.`id`
                                                       WHERE `opendsa_exercise`.`ex_type`='ss' AND DATE(`opendsa_userexerciselog`.`time_done`) = %s
                                                       GROUP BY date
                                                       ORDER BY date ASC''', [yesterday.date().strftime('%Y-%m-%d')])
    #total number of ka 
    all_ka_log = UserExerciseLog.objects.raw('''SELECT `opendsa_userexerciselog`.`id`, COUNT(`opendsa_userexerciselog`.`exercise_id`) AS ka_exe,
                                                       DATE(`opendsa_userexerciselog`.`time_done`)  AS date 
                                                       FROM `opendsa_userexerciselog`
                                                       JOIN `opendsa_exercise`
                                                       ON `opendsa_userexerciselog`.`exercise_id` = `opendsa_exercise`.`id`
                                                       WHERE `opendsa_exercise`.`ex_type`='ka' AND DATE(`opendsa_userexerciselog`.`time_done`) = %s
                                                       GROUP BY date
                                                       ORDER BY date ASC''', [yesterday.date().strftime('%Y-%m-%d')])
    #total number of pe 
    all_pe_log = UserExerciseLog.objects.raw('''SELECT `opendsa_userexerciselog`.`id`, COUNT(`opendsa_userexerciselog`.`exercise_id`) AS pe_exe,
                                                       DATE(`opendsa_userexerciselog`.`time_done`)  AS date 
                                                       FROM `opendsa_userexerciselog`
                                                       JOIN `opendsa_exercise`
                                                       ON `opendsa_userexerciselog`.`exercise_id` = `opendsa_exercise`.`id`
                                                       WHERE `opendsa_exercise`.`ex_type`='pe' AND DATE(`opendsa_userexerciselog`.`time_done`) = %s
                                                       GROUP BY date
                                                       ORDER BY date ASC''', [yesterday.date().strftime('%Y-%m-%d')])


    all_daily_logs=[]
    for day in day_list:
        ex_logs={}
        ex_logs['dt'] = day.date().strftime('%Y-%m-%d')
        ex_logs['d_attempts']=0
        ex_logs['registrations']=0
        ex_logs['proficients']=0
        ex_logs['a_attempts']=0
        ex_logs['interactions']=0
        ex_logs['ss']=0
        ex_logs['ka']=0
        ex_logs['pe']=0
        #distinct users attempts
        for udl in user_day_log:
            if (day.date == udl.date):
                ex_logs['d_attempts'] = int(udl.users)
        #distinct users registration
        for url in user_reg_log:
            if (day.date == url.date):
                ex_logs['registrations'] = int(url.regs)
        #total proficient  
        for apl in all_prof_log:
            if (day.date == apl.date):
                ex_logs['proficients'] = int(apl.profs)
        #all exercises attempts (all questions)
        for ael in all_exe_log:
            if (day.date == ael.date):
                ex_logs['a_attempts'] = int(ael.exe)
        #all interactions
        for uul in user_use_log:
            if (day.date == uul.date):
                ex_logs['interactions'] = int(uul.users)
        #all ss attempts
        for asl in all_ss_log:
            if (day.date == asl.date):
                ex_logs['ss'] = int(asl.ss_exe)
        #all ka attempts
        for akl in all_ka_log:
            if (day.date == akl.date):
                ex_logs['ka'] = int(akl.ka_exe)
        #all pe attempts
        for apl in all_pe_log:
            if (day.date == apl.date):
                ex_logs['pe'] = int(apl.pe_exe)

        #all_daily_logs.append(ex_logs)

    #write data into a file
    try:
        json_data = open(settings.MEDIA_ROOT + 'daily_stats1.json')
        data = json.load(json_data)
        data.append(ex_logs)        
    
        ofile = open(settings.MEDIA_ROOT + 'daily_stats1.json','w') 
        ofile.writelines(str(data).replace("'",'"'))
        ofile.close
    except IOError as e:
        print "error ({0}) written file : {1}".format(e.errno, e.strerror)

