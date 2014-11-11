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
from opendsa.models import Exercise, UserExercise, Module, UserModule, Books, BookModuleExercise, UserData, UserExerciseLog, UserButton, UserBook, BookChapter
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
from django.db.models import Sum
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


#f
def create_book_file(book):
    #get chapters
    chapter_dict = {}
    book_list = []
    for chapter in BookChapter.objects.filter(book=book):
        #get exercises
        exe_dict = {}
        for c_mod in chapter.get_modules():
            for b_exe in BookModuleExercise.components.get_mod_exercise_list(book, c_mod):
               exe_dict[str(int(b_exe.id))]=str(b_exe.name)
        if len(exe_dict) > 0:
            chap_ = '%s-%s' %(str(chapter.name),chapter.id)
            chapter_dict[chap_] = exe_dict
    book_ = '%s-%s' %(book.book_url,book.id)
    book_list.append({str(book_).replace("'",'"'):chapter_dict})

    try:
          f_handle = open(settings.MEDIA_ROOT + book.book_name + '.json', 'w+')
          f_handle.writelines(str(book_list).replace("'",'"'))
          f_handle.close()
    except IOError as e:
          print "error ({0}) writing file : {1}".format(e.errno, e.strerror)


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
    old_logs = {}
    old_logs['users'] = 0 
    old_logs['exe'] = 0
    #get data from old databse
    try:
        old_handle = open(settings.MEDIA_ROOT + 'widget_stats1.json')
        old_logs = convert(json.load(old_handle))
        old_logs['exe'] = 573059
        old_logs['users'] = 1115
        old_handle.close
    except IOError as e:
        print "error ({0}) written file : {1}".format(e.errno, e.strerror)

    w_table = {}
    w_table['exercises'] = int(exe)  + int(old_logs['exe'])
    w_table['users'] = int(user) + int(old_logs['users']) 

    #write data into a file
    try:
        ofile = open(settings.MEDIA_ROOT + 'widget_stats.json','w') #'ab+')
        ofile.writelines(str(w_table).replace("'",'"'))
        ofile.close
    except IOError as e:
        print "error ({0}) written file : {1}".format(e.errno, e.strerror)


def post_proficiency():
    #detailed data on post proficiency

    users_pp_logs=[]

    #get books and courses
    all_books_courses = Books.objects.raw('''SELECT `id`, `books_id`, `courseinstance_id` 
                                             FROM `opendsa_books_courses` 
                                         ''' ) 


    for abc in all_books_courses:

        #get course instance
        book_course =  Books.objects.raw('''SELECT `id`, `instance_name`
                                             FROM `course_courseinstance` 
                                             WHERE `id`=%s
                                         ''', [abc.courseinstance_id] )


        #get exercises in the book
        exercise_book = Books.objects.raw('''SELECT id, exercise_id
                                                      FROM `opendsa_bookmoduleexercise`
                                                      WHERE `book_id`=%s
                                                   ''',[abc.books_id])

        #get students id
        user_book = UserBook.objects.raw('''SELECT `id`, `user_id` FROM `opendsa_userbook`
                                            WHERE `book_id`=%s
                                        ''',[abc.books_id]) 
        for ub in user_book:
            processed_exe = [] 
            for eb in exercise_book:
                if eb.exercise_id not in processed_exe:
                    processed_exe.append(eb.exercise_id)
                    exercise_data = Exercise.objects.raw('''SELECT `id`, `name`, `ex_type` 
                                                            FROM `opendsa_exercise`
                                                            WHERE `id`=%s
                                                         ''',[eb.exercise_id])

                    user_prof_date = UserExercise.objects.raw('''SELECT `id`, `proficient_date` FROM `opendsa_userexercise`
                                                                 WHERE `user_id`=%s AND `exercise_id`=%s
                                                              ''',[ub.user_id,eb.exercise_id])
                

                    for upd in user_prof_date:
                        pp_logs={}
                        pp_logs['book'] = ''
                        pp_logs['student'] = 0
                        pp_logs['exercise'] = ''
                        pp_logs['type'] = ''
                        pp_logs['prof_date']= ''
                        pp_logs['number_pp'] = 0

                        for bc in book_course:
                            pp_logs['book'] = str(bc.instance_name)
 
                        pp_logs['student'] = int(ub.user_id)
                        for ed in exercise_data:
                            pp_logs['exercise'] = str(ed.name)
                            pp_logs['type'] = str(ed.ex_type)

                        pp_logs['prof_date']= str(upd.proficient_date)
       
                        exe_prof_data = UserExerciseLog.objects.raw('''SELECT `id`, COUNT( * ) AS numb_pp
                                                                    FROM  `opendsa_userexerciselog`
                                                                    WHERE `user_id`=%s and `exercise_id`=%s
                                                                           and `time_done`>%s 
                                                                    ''',[ub.user_id,eb.exercise_id,upd.proficient_date])
                        for epd in exe_prof_data:
                            pp_logs['number_pp'] = int(epd.numb_pp)


                        users_pp_logs.append(pp_logs)

        #write data into a file
    try:
        users_pp_logs = str(users_pp_logs).replace("'",'"')
        users_pp_logs = users_pp_logs.replace("[","").replace("]","")
        users_pp_logs = '[' + users_pp_logs + ']'
        ofile = open(settings.MEDIA_ROOT + 'proficiency_stats.json','w') #'ab+')
        ofile.writelines(str(users_pp_logs).replace("'",'"'))
        ofile.close
    except IOError as e:
        print "error ({0}) written file : {1}".format(e.errno, e.strerror)
    return users_pp_logs


def devices_analysis():
    #mobile devices analysis
    pc_only_users = User.objects.raw('''SELECT  `id` , COUNT( * ) AS pc_only
                                        FROM  `auth_user` 
                                        WHERE  `id` NOT 
                                        IN (
                                             SELECT  `id` 
                                             FROM  `opendsa_userbutton` 
                                             WHERE  `device` !=  'PC'
                                        )''')

    pc_mob_users = UserButton.objects.raw('''SELECT id, COUNT(DISTINCT user_id) As mob_users
                                                  FROM opendsa_userbutton
                                                  WHERE device != 'PC'
                                                  ''')

    pc_actions_total = UserButton.objects.raw('''SELECT id, COUNT(*) As volume
                                                   FROM opendsa_userbutton
                                                   WHERE device = 'PC'
                                                   ''')

    mobile_actions_total  = UserButton.objects.raw('''SELECT id, COUNT(*) As volume
                                                   FROM opendsa_userbutton
                                                   WHERE device != 'PC'
                                                   ''')

    day_list = UserButton.objects.raw('''SELECT id, DATE(action_time) As date
                                                  FROM opendsa_userbutton
                                                  GROUP BY date
                                                  ORDER BY date ASC''')

    all_users_day =  UserButton.objects.raw('''SELECT id, COUNT(DISTINCT user_id) As users,
                                                  DATE(action_time) As date
                                                  FROM opendsa_userbutton
                                                  WHERE device = 'PC'
                                                  GROUP BY date
                                                  ORDER BY date ASC''')

    mobile_users_day =  UserButton.objects.raw('''SELECT id, COUNT(DISTINCT user_id) As users,
                                                  DATE(action_time) As date
                                                  FROM opendsa_userbutton
                                                  WHERE device != 'PC'
                                                  GROUP BY date
                                                  ORDER BY date ASC''')

    all_actions_day = UserButton.objects.raw('''SELECT id, COUNT(*) As volume,
                                                   DATE(action_time) As date
                                                   FROM opendsa_userbutton
                                                   WHERE device = 'PC'
                                                   GROUP BY date
                                                   ORDER BY date ASC ''')

    mobile_actions_day = UserButton.objects.raw('''SELECT id, COUNT(*) As volume,
                                                   DATE(action_time) As date
                                                   FROM opendsa_userbutton
                                                   WHERE device != 'PC'
                                                   GROUP BY date
                                                   ORDER BY date ASC ''')


    jsav_actions_day = UserButton.objects.raw('''SELECT id, COUNT(*) As volume,
                                                   DATE(action_time) As date
                                                   FROM opendsa_userbutton
                                                   WHERE device != 'PC' AND
                                                   name LIKE '%%jsav%%'
                                                   GROUP BY date
                                                   ORDER BY date ASC ''')

    jsav_distinct_users_day = UserButton.objects.raw('''SELECT id, COUNT(DISTINCT user_id) As volume,
                                                        DATE(action_time) As date
                                                        FROM opendsa_userbutton
                                                        WHERE device != 'PC' AND
                                                        name LIKE '%%jsav%%'
                                                        GROUP BY date
                                                        ORDER BY date ASC ''')

    dates = []
    all_users = []
    mobile_users = []
    all_actions = []
    mobile_actions = []
    jsav_actions = []
    jsav_distinct_users = []
    interactions_dict = {}

    for  pou in pc_only_users:
        interactions_dict['pc_only_users'] = int(pou.pc_only)
    for pmu in pc_mob_users:
        interactions_dict['pc_mob_users'] = int(pmu.mob_users)
    for pat in pc_actions_total:
        interactions_dict['pc_actions'] = int(pat.volume)
    for mat in mobile_actions_total:
        interactions_dict['mobile_actions'] = int(mat.volume)

    for day in day_list:
        dates.append(str(day.date.strftime('%Y-%m-%d')))
        all_users.append(0)
        mobile_users.append(0)
        all_actions.append(0)
        mobile_actions.append(0)
        jsav_actions.append(0)
        jsav_distinct_users.append(0)
        for aud in all_users_day:
            if (day.date == aud.date):
                all_users.pop()
                all_users.append(int(aud.users)) 
        for mud in mobile_users_day:
            if (day.date == mud.date):
                mobile_users.pop()
                mobile_users.append(int(mud.users))       
        for aad in all_actions_day:
            if (day.date == aad.date):
                all_actions.pop()
                all_actions.append(int(aad.volume))
        for mad in mobile_actions_day:
            if (day.date == mad.date):
                mobile_actions.pop()
                mobile_actions.append(int(mad.volume))
        for jad in jsav_actions_day:
            if (day.date == jad.date):
                jsav_actions.pop()
                jsav_actions.append(int(jad.volume))
        for jdu in jsav_distinct_users_day:
            if (day.date == jdu.date):
                jsav_distinct_users.pop()
                jsav_distinct_users.append(int(jdu.volume))

    interactions_dict['days'] = dates
    interactions_dict['users'] = all_users
    interactions_dict['mobile_users'] = mobile_users
    interactions_dict['interactions'] = all_actions
    interactions_dict['mobile_interactions'] = mobile_actions
    interactions_dict['mobile_jsav'] = jsav_actions
    interactions_dict['mobile_jsav_distinct_users'] = jsav_distinct_users

    #write data into a file
    try:
        #all_daily_logs = str(all_daily_logs).replace("'",'"')#[1:-1]
        #all_daily_logs = all_daily_logs.replace("[","").replace("]","")
        #all_daily_logs = '[' + all_daily_logs + ']'

        ofile = open(settings.MEDIA_ROOT + 'device_stats.json','w') #'ab+')
        ofile.writelines(str(interactions_dict).replace("'",'"'))
        ofile.close
    except IOError as e:
        print "error ({0}) written file : {1}".format(e.errno, e.strerror)

    return interactions_dict

 
def exercises_logs( course=None):

    clause_1 = "" 
    clause_2 = ""
    clause_3 = ""
    clause_4 = ""
    clause_5 = ""
    if course is not None:
      # get book_id from course
      obj_course = CourseInstance.objects.get(instance_name=course)
      obj_book = Books.objects.filter(courses=obj_course)
      if obj_book:
        book_ = obj_book[0]
        clause_1 = " WHERE user_id in (SELECT user_id FROM opendsa_userbook WHERE book_id=%s AND grade=1)" %int(book_.id)      
        clause_2 = "WHERE id in (SELECT user_id FROM opendsa_userbook WHERE book_id=%s AND grade=1)" %int(book_.id)
        clause_3 = "WHERE book_id =%s" %int(book_.id)
        clause_4 = "AND user_id in (SELECT user_id FROM opendsa_userbook WHERE book_id=%s AND grade=1)" %int(book_.id)
        clause_5 = " AND `opendsa_userexerciselog`.`user_id` in (SELECT user_id FROM opendsa_userbook WHERE book_id=%s AND grade=1)" %int(book_.id)
    #days rage, now all dayys the book was used
    day_list = UserExerciseLog.objects.raw('''SELECT id, DATE(action_time) As date
                                                  FROM opendsa_userbutton {0}
                                                  GROUP BY date
                                                  ORDER BY date ASC'''.format(clause_3))

    #distinct user exercise attempts
    user_day_log = UserExerciseLog.objects.raw('''SELECT id, COUNT(DISTINCT user_id) As users,
                                                         DATE(time_done) As date
                                                  FROM opendsa_userexerciselog {0} GROUP BY date
                                                  ORDER BY date ASC'''.format(clause_1))
    #user registration per day 
    user_reg_log = User.objects.raw('''SELECT id, COUNT(id) As regs,
                                                         DATE(date_joined) As date
                                                  FROM auth_user {0}
                                                  GROUP BY date
                                                  ORDER BY date ASC'''.format(clause_2))
    #user usage per day (interactions)
    user_use_log = UserButton.objects.raw('''SELECT id, COUNT(user_id) As users,
                                                         DATE(action_time) As date
                                                  FROM opendsa_userbutton {0}
                                                  GROUP BY date
                                                  ORDER BY date ASC'''.format(clause_3))
    #distinct all proficiency per day per exercise
    all_prof_log = UserExerciseLog.objects.raw('''SELECT id, user_id, COUNT(earned_proficiency) AS profs,
                                                          DATE(time_done) AS date
                                                   FROM  opendsa_userexerciselog 
                                                   WHERE earned_proficiency = 1 {0}
                                                   GROUP BY date   
                                                   ORDER BY date ASC'''.format(clause_4))
    #number of exercises attempted
    all_exe_log = UserExerciseLog.objects.raw('''SELECT id, user_id, COUNT(exercise_id) AS exe, 
                                                             DATE(time_done) AS date
                                                      FROM  opendsa_userexerciselog {0}
                                                      GROUP BY date 
                                                      ORDER BY date ASC'''.format(clause_1))
    #total number of ss 
    all_ss_log = UserExerciseLog.objects.raw('''SELECT `opendsa_userexerciselog`.`id`,`opendsa_userexerciselog`.`user_id`, COUNT(`opendsa_userexerciselog`.`exercise_id`) AS ss_exe,
                                                       DATE(`opendsa_userexerciselog`.`time_done`)  AS date 
                                                       FROM `opendsa_userexerciselog`
                                                       JOIN `opendsa_exercise`
                                                       ON `opendsa_userexerciselog`.`exercise_id` = `opendsa_exercise`.`id`
                                                       WHERE `opendsa_exercise`.`ex_type`='ss' {0}
                                                       GROUP BY date
                                                       ORDER BY date ASC'''.format(clause_5))
    #total number of ka 
    all_ka_log = UserExerciseLog.objects.raw('''SELECT `opendsa_userexerciselog`.`id`,`opendsa_userexerciselog`.`user_id`, COUNT(`opendsa_userexerciselog`.`exercise_id`) AS ka_exe,
                                                       DATE(`opendsa_userexerciselog`.`time_done`)  AS date 
                                                       FROM `opendsa_userexerciselog`
                                                       JOIN `opendsa_exercise`
                                                       ON `opendsa_userexerciselog`.`exercise_id` = `opendsa_exercise`.`id`
                                                       WHERE `opendsa_exercise`.`ex_type`='ka' {0}
                                                       GROUP BY date
                                                       ORDER BY date ASC'''.format(clause_5))    
    #total number of pe 
    all_pe_log = UserExerciseLog.objects.raw('''SELECT `opendsa_userexerciselog`.`id`, `opendsa_userexerciselog`.`user_id`, COUNT(`opendsa_userexerciselog`.`exercise_id`) AS pe_exe,
                                                       DATE(`opendsa_userexerciselog`.`time_done`)  AS date 
                                                       FROM `opendsa_userexerciselog`
                                                       JOIN `opendsa_exercise`
                                                       ON `opendsa_userexerciselog`.`exercise_id` = `opendsa_exercise`.`id`
                                                       WHERE `opendsa_exercise`.`ex_type`='pe' {0}
                                                       GROUP BY date
                                                       ORDER BY date ASC'''.format(clause_5))
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
        #ffile = open(settings.MEDIA_ROOT + 'daily_stats1.json')
        #fall12_data = ffile.readlines()
        #ffile.close()
        #all_daily_logs = fall12_data[0][1:-1] + ',' + str(all_daily_logs).replace("'",'"')[1:-1]
        the_file = 'daily_stats.json'
        if course is not None:
           the_file = 'daily_stats_%s.json' %course.lower()
        
        all_daily_logs = str(all_daily_logs).replace("'",'"')#[1:-1]
        all_daily_logs = all_daily_logs.replace("[","").replace("]","")
        all_daily_logs = '[' + all_daily_logs + ']' 
        
        ofile = open(settings.MEDIA_ROOT + the_file,'w') 
        ofile.writelines(str(all_daily_logs).replace("'",'"'))
        ofile.close
    except IOError as e:
        print "error ({0}) written file : {1}".format(e.errno, e.strerror)
    return all_daily_logs


def interaction_timeseries(course = None):
  if course is not None:
    # get book_id from course
    obj_course = CourseInstance.objects.get(instance_name=course)
    obj_book = Books.objects.filter(courses=obj_course) 
    #days rage, now all dayys the book was used
    clause_1 = " WHERE action_time BETWEEN '%s' AND '%s' " %(obj_course.starting_time, obj_course.ending_time)
    day_list = UserExerciseLog.objects.raw('''SELECT id, DATE(action_time) As date
                                                  FROM opendsa_userbutton {0}
                                                  GROUP BY date
                                                  ORDER BY date ASC'''.format(clause_1))

    print day_list
    #get course students
    ubook = UserBook.objects.filter(book=obj_book)
    all_daily_logs=[]
    class_data = {}
    class_headers = ['id']
    for day in day_list:
      class_headers.append(day.date.strftime('%Y-%m-%d'))
      for ub in ubook:
         if int(ub.user.id) not in class_data:
           class_data[int(ub.user.id)] = [int(ub.user.id)]
         today_min = datetime.datetime.combine(day.date, datetime.time.min)
         today_max = datetime.datetime.combine(day.date, datetime.time.max)
         #act_count =  UserButton.objects.filter(user=ub.user,book=obj_book, action_time__range=(today_min, today_max)).count()  
         act_count =  UserExerciseLog.objects.filter(user=ub.user,time_done__range=(today_min, today_max),earned_proficiency=True).count()
         #interactions_d = UserButton.objects.filter(user=ub.user,book=obj_book, action_time__range=(today_min, today_max))
         #actions = ''
         #for inter_d in interactions_d:
             #try: 
             #tmp = json.loads(str(inter_d.description))
             #print "==========================\n %s +++++++ \n  %s" %(tmp,tmp['msg'])
             #actions = actions + str(tmp['msg'])
             #except ValueError, e:
             #print "XXXXXXXXXXXXXXXXXX \n %s " %str(inter_d.description)
             #actions = actions + ',' + str(inter_d.name)
         class_data[int(ub.user.id)].append(act_count)
         #class_data[int(ub.user.id)].append(actions)
     #put all data in the output list
    output_list = []
    for key, value in class_data.iteritems():
      output_list.append(value)
  
    try:
        the_file = 'interactionsTS_stats.json'
        if course is not None:
           the_file = 'interactionsTS_stats_%s.json' %course.lower()


        ofile = open(settings.MEDIA_ROOT + the_file,'w')
        ofile.writelines(str(output_list).replace("'",'"'))
        ofile.close
    except IOError as e:
        print "error ({0}) written file : {1}".format(e.errno, e.strerror)
    return class_headers, output_list

  return None, None


def interaction_logs(course = None):
  if course is not None:
    # get book_id from course
    obj_course = CourseInstance.objects.get(instance_name=course)
    obj_book = Books.objects.filter(courses=obj_course)
    #get course students
    ubook = UserBook.objects.filter(book=obj_book)
    #get all interaction type\
    actions = UserButton.objects.values('name').distinct()
    class_data = {}
    class_headers = ['id'] 
    for act in actions:
      class_headers.append(act['name']) 
      for ub in ubook:
         if int(ub.user.id) not in class_data:
           class_data[int(ub.user.id)] = [int(ub.user.id)]
         act_count =  UserButton.objects.filter(user=ub.user,book=obj_book, name=act['name']).count()
         class_data[int(ub.user.id)].append(act_count)
    #put all data in the output list
    output_list = []
    for key, value in class_data.iteritems(): 
      output_list.append(value)
    try:
        the_file = 'interactions_stats.json'
        if course is not None:
           the_file = 'interactions_stats_%s.json' %course.lower()


        ofile = open(settings.MEDIA_ROOT + the_file,'w')
        ofile.writelines(str(output_list).replace("'",'"'))
        ofile.close
    except IOError as e:
        print "error ({0}) written file : {1}".format(e.errno, e.strerror)
    return class_headers, output_list

  return None, None
  





def glossary_logs(course=None):
  if course is not None:
    # get book_id from course
    obj_course = CourseInstance.objects.get(instance_name=course)
    obj_book = Books.objects.filter(courses=obj_course)

    glo_data = []
    #number of book users
    ubook = UserBook.objects.filter(book=obj_book).count()
    #module page views
    moduless = UserButton.objects.filter(book=obj_book, name='document-ready').count()
    #glossary click
    glo_mod = Module.objects.get(name='Glossary')
    glossaries = UserButton.objects.filter(book=obj_book, name='glossary-term-clicked').count()
    #within glossary pages clicks
    glossariesw = UserButton.objects.filter(book=obj_book, name='glossary-term-clicked', module=glo_mod).count() 
    glo_data.append(ubook)
    glo_data.append(moduless)
    glo_data.append(glossaries)
    glo_data.append(glossariesw)
    glo_logs = []
    glo_logs.append(glo_data)
    return glo_logs
  return None

def terms_logs(course=None):
  if course is not None:
    # get book_id from course
    obj_course = CourseInstance.objects.get(instance_name=course)
    obj_book = Books.objects.filter(courses=obj_course)

    glo_logs = []
    glo_data = {}
    #number of book users
    ubook = UserBook.objects.filter(book=obj_book).count()
    #glossary click
    #glo_mod = Module.objects.get(name='Glossary')
    glossaries = UserButton.objects.filter(book=obj_book, name='glossary-term-clicked')
    for glo in glossaries:
      json_data = json.loads(str(glo.description))
      term = json_data['msg']
      if term not in glo_data:
        glo_data[str(term)] = 1
      else:
         glo_data[str(term)] = glo_data[term] + 1

    word_array = [] 
    #convert glo_data to list 
    word_array = []
    for key, value in glo_data.iteritems():
      temp = [key,value]
      glo_logs.append(temp)
      word_array.append({"text":key,"weight":value})
    return glo_logs, word_array
  return None



def students_logs( course=None):

  if course is not None:
    # get book_id from course
    obj_course = CourseInstance.objects.get(instance_name=course)
    obj_book = Books.objects.filter(courses=obj_course)

   ##### CS3114 F13
   #Midterm 1: Tuesday, October 1
   #Midterm 2: Tuesday, November 12
   #Final: Tuesday, December 12



    ka_exe_av = [8,23,29,31,36,38,43,45,52,71,73,76,78,81,85,88,90,94,136,137,155,179,182,183,184,185,189,190,191,192]
    other_exe = [203, 214, 220]
    students_ilogs = []
    ubook = UserBook.objects.filter(book=obj_book)
    for ub in ubook:
      stud_data = [] 
      total_correct_ka = 0
      total_correct_kav = 0
      total_correct_pe = 0
      total_correct_ss = 0 
      total_done_ka = 0
      total_done_kav = 0
      total_done_pe = 0
      total_done_ss = 0  
      stud_data.append(int(ub.user.id))
      #uxe = UserExercise.objects.filter(user=ub.user) , proficient_date__gt=datetime.date(2013, 10, 1), proficient_date__lt=datetime.date(2013, 11, 12))

      #CS3114 F13 M1
      uxel_m1 = UserExerciseLog.objects.filter(user=ub.user, time_done__lt=datetime.date(2013, 10, 1), time_done__gt=datetime.date(2013, 8, 26), earned_proficiency=True).count()
      #CS3114 F13 M2
      uxel_m2 = UserExerciseLog.objects.filter(user=ub.user, time_done__lt=datetime.date(2013, 11, 12), time_done__gt=datetime.date(2013, 10, 2), earned_proficiency=True).count()
      #CS3114 F13 F
      uxel_f = UserExerciseLog.objects.filter(user=ub.user, time_done__lt=datetime.date(2013, 12, 12), time_done__gt=datetime.date(2013, 11, 13), earned_proficiency=True).count()

      stud_data.append(uxel_m1)
      stud_data.append(uxel_m2)
      stud_data.append(uxel_f)



#      for ux_row in uxe:
#        if ux_row.exercise.ex_type=="ka" and ux_row.exercise.id not in ka_exe_av and ux_row.exercise.id not in other_exe:
#          total_correct_ka = total_correct_ka + int(ux_row.progress)
#          total_done_ka = total_done_ka +  UserExerciseLog.objects.filter(user=ub.user, exercise=ux_row.exercise).count() #, time_done__gt=datetime.date(2013, 10, 1), time_done__lt=datetime.date(2013, 11, 12)).count()
#        if ux_row.exercise.id in ka_exe_av:
#          total_correct_kav = total_correct_kav + int(ux_row.progress)
#          total_done_kav = total_done_kav +  UserExerciseLog.objects.filter(user=ub.user, exercise=ux_row.exercise).count() #, time_done__gt=datetime.date(2013, 10, 1), time_done__lt=datetime.date(2013, 11, 12)).count()
#        if ux_row.exercise.ex_type=="pe":
#          total_correct_pe = total_correct_pe + int(ux_row.total_correct)
#          total_done_pe = total_done_pe + int(ux_row.total_done) 
#        if ux_row.exercise.ex_type=="ss":
#          total_correct_ss = total_correct_ss + int(ux_row.total_correct)
#          total_done_ss = total_done_ss + int(ux_row.total_done)

#      stud_data.append(total_done_ka)
#      stud_data.append(total_correct_ka)
#      stud_data.append(total_done_kav)
#      stud_data.append(total_correct_kav)
#      stud_data.append(total_done_pe)
#      stud_data.append(total_correct_pe)
#      stud_data.append(total_done_ss)
#      stud_data.append(total_correct_ss)

      #ux = uxe.aggregate(total=Sum('total_done'))
      #uxl = uxel.aggregate(total=Sum('time_done'))
      #uxe1 = UserExercise.objects.filter(user=ub.user)
      #uxel1 = UserExerciseLog.objects.filter(user=ub.user, earned_proficiency=True,time_done__lt=datetime.date(2014, 5, 13), time_done__gt=datetime.date(2014, 4, 23))
      #ux1 = uxe1.aggregate(correct=Sum('total_correct'))
      #uxl1 = uxel1.aggregate(correct=Sum('total_correct'))
      #stud_data.append( int(UserButton.objects.filter(user=ub.user, action_time__lt=datetime.date(2014, 5, 13), action_time__gt=datetime.date(2014, 4, 23)).count()) )

      #stud_data.append(int(uxel.count()))
      #stud_data.append(int(uxel1.count()))
      #if  ux.get('total',0):
      #  stud_data.append( uxl.get('total',0) )
      #else:
      #   stud_data.append( 0 )
      #if ux1.get('correct',0):
      #  stud_data.append( uxl1.get('correct',0) )
      #else:
      #  stud_data.append( 0 )

      students_ilogs.append(stud_data)
    return students_ilogs
  return None
