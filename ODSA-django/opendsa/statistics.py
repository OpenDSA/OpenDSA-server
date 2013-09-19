# Python
from icalendar import Calendar, Event
import json
import csv
import array
from collections import OrderedDict
from decimal import *

# A+
from userprofile.models import UserProfile
from course.models import Course, CourseInstance

# OpenDSA 
from opendsa.models import Exercise, UserExercise, Module, UserModule, Books, BookModuleExercise, UserData, UserExerciseLog, UserButton, UserBook
# Django
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseForbidden
from course.context import CourseContext
from django.template import loader, Context
from django.template.context import RequestContext
from django.utils import simplejson
from django.core import serializers
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.views.generic import TemplateView, ListView
from django.template import add_to_builtins
import jsonpickle
import datetime
from django.conf import settings
import os


def is_authorized(user, book, course):
    obj_book = Books.objects.select_related().get(book_name=book)
    user_prof = UserProfile.objects.get(user=user)
    obj_course = CourseInstance.objects.get(instance_name=course)
    if obj_course in obj_book.courses.all():
        return obj_course.is_staff(user_prof)
    else:
        return False

def get_active_exercises():
    BookModExercises = BookModuleExercise.components.select_related().all()
    active_exe =[]
    for bme in BookModExercises:
        if bme.exercise not in active_exe:
            active_exe.append(bme.exercise)
    return active_exe

def display_grade(user, book):
    if UserBook.objects.filter(user=user, book=book).count()==1:
        return UserBook.objects.filter(user=user, book=book)[0].grade
    return False


def convert(input):
    if isinstance(input, dict):
        return {convert(key): convert(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


#function that checks if a file is older than the limit
def is_file_old_enough(filename, limit): #limit in seconds
    #we only run the whole computaion if the statistic file is older than an hour
    now = datetime.datetime.now()
    stat_file = str(settings.MEDIA_ROOT + filename)
    statbuf = os.stat(stat_file)
    last_modif = datetime.datetime.fromtimestamp(statbuf.st_mtime)
    diff = now - last_modif
    data = []
    return  diff > datetime.timedelta(0, limit, 0)

def get_widget_data():
    exe = UserExerciseLog.objects.count()

    #number of registered attempted
    user = User.objects.filter(is_staff=0).count()

    #get data from old databse
    try:
        old_handle = open(settings.MEDIA_ROOT + 'widget_stats1.json')
        old_logs = convert(json.load(old_handle))
        old_handle.close
    except IOError as e:
        print "error ({0}) written file : {1}".format(e.errno, e.strerror)

    w_table = {}
    w_table['exercises'] = int(exe) + int(old_logs['exercises'])
    w_table['users'] = int(user) + int(old_logs['users'])

    #write data into a file
    try:
        ofile = open(settings.MEDIA_ROOT + 'widget_stats.json','w') #'ab+')
        ofile.writelines(str(w_table).replace("'",'"'))
        ofile.close
    except IOError as e:
        print "error ({0}) written file : {1}".format(e.errno, e.strerror)



def exercises_logs():
    #days rage, now all dayys the book was used
    day_list = UserExerciseLog.objects.raw('''SELECT id, DATE(time_done) As date
                                                  FROM opendsa_userexerciselog
                                                  GROUP BY date
                                                  ORDER BY date ASC''')
    #distinct user exercise attempts
    user_day_log = UserExerciseLog.objects.raw('''SELECT id, COUNT(DISTINCT user_id) As users,
                                                         DATE(time_done) As date
                                                  FROM opendsa_userexerciselog
                                                  GROUP BY date
                                                  ORDER BY date ASC''')
    #user registration per day 
    user_reg_log = User.objects.raw('''SELECT id, COUNT(id) As regs,
                                                         DATE(date_joined) As date
                                                  FROM auth_user
                                                  GROUP BY date
                                                  ORDER BY date ASC''')
    #user usage per day (interactions)
    user_use_log = UserButton.objects.raw('''SELECT id, COUNT(user_id) As users,
                                                         DATE(action_time) As date
                                                  FROM opendsa_userbutton
                                                  GROUP BY date
                                                  ORDER BY date ASC''')
    #distinct all proficiency per day per exercise
    all_prof_log = UserExerciseLog.objects.raw('''SELECT id, COUNT(earned_proficiency) AS profs,
                                                          DATE(time_done) AS date
                                                   FROM  opendsa_userexerciselog 
                                                   WHERE earned_proficiency = 1
                                                   GROUP BY date   
                                                   ORDER BY date ASC''')
    #number of exercises attempted
    all_exe_log = UserExerciseLog.objects.raw('''SELECT id, COUNT(exercise_id) AS exe, 
                                                             DATE(time_done) AS date
                                                      FROM  opendsa_userexerciselog 
                                                      GROUP BY date 
                                                      ORDER BY date ASC''')
    #total number of ss 
    all_ss_log = UserExerciseLog.objects.raw('''SELECT `opendsa_userexerciselog`.`id`, COUNT(`opendsa_userexerciselog`.`exercise_id`) AS ss_exe,
                                                       DATE(`opendsa_userexerciselog`.`time_done`)  AS date 
                                                       FROM `opendsa_userexerciselog`
                                                       JOIN `opendsa_exercise`
                                                       ON `opendsa_userexerciselog`.`exercise_id` = `opendsa_exercise`.`id`
                                                       WHERE `opendsa_exercise`.`ex_type`='ss'
                                                       GROUP BY date
                                                       ORDER BY date ASC''')
    #total number of ka 
    all_ka_log = UserExerciseLog.objects.raw('''SELECT `opendsa_userexerciselog`.`id`, COUNT(`opendsa_userexerciselog`.`exercise_id`) AS ka_exe,
                                                       DATE(`opendsa_userexerciselog`.`time_done`)  AS date 
                                                       FROM `opendsa_userexerciselog`
                                                       JOIN `opendsa_exercise`
                                                       ON `opendsa_userexerciselog`.`exercise_id` = `opendsa_exercise`.`id`
                                                       WHERE `opendsa_exercise`.`ex_type`='ka'
                                                       GROUP BY date
                                                       ORDER BY date ASC''')    
    #total number of pe 
    all_pe_log = UserExerciseLog.objects.raw('''SELECT `opendsa_userexerciselog`.`id`, COUNT(`opendsa_userexerciselog`.`exercise_id`) AS pe_exe,
                                                       DATE(`opendsa_userexerciselog`.`time_done`)  AS date 
                                                       FROM `opendsa_userexerciselog`
                                                       JOIN `opendsa_exercise`
                                                       ON `opendsa_userexerciselog`.`exercise_id` = `opendsa_exercise`.`id`
                                                       WHERE `opendsa_exercise`.`ex_type`='pe'
                                                       GROUP BY date
                                                       ORDER BY date ASC''')
    all_daily_logs=[]
    for day in day_list:
        ex_logs={}
        ex_logs['dt'] = day.date.strftime('%Y-%m-%d')
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


        all_daily_logs.append(ex_logs)         
        
    #write data into a file
    try:
        ffile = open(settings.MEDIA_ROOT + 'daily_stats1.json')
        fall12_data = ffile.readlines()
        ffile.close()
        all_daily_logs = fall12_data[0][1:-1] + ',' + str(all_daily_logs).replace("'",'"')[1:-1]
        all_daily_logs = all_daily_logs.replace("[","").replace("]","")
        all_daily_logs = '[' + all_daily_logs + ']' 
        
        ofile = open(settings.MEDIA_ROOT + 'daily_stats.json','w') #'ab+')
        ofile.writelines(str(all_daily_logs).replace("'",'"'))
        ofile.close
    except IOError as e:
        print "error ({0}) written file : {1}".format(e.errno, e.strerror)
    return all_daily_logs

