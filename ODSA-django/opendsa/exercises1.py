"""
Module containing methods needed by the API modules
"""


import datetime
from decimal import Decimal

from opendsa.models import Exercise, UserExerciseLog, \
                           UserData, UserButton, UserModule, Module, \
                           BookModuleExercise, Assignments
from exercise.models import CourseModule
from django.db import transaction
from course.models import CourseInstance

def diff(list_a, list_b):
    """
    methods to get the difference between two sets
    """
    list_b = set(list_b)
    return [aa for aa in list_a if aa not in list_b]

def str2bool(str_var):
    """
    Converts string to boolean
    """
    return str_var.lower() in ("yes", "true", "t", "1")


def get_pe_name_from_referer(referer):
    """
    Returns the proficiency exercise name based on URL
    """
    tab = referer.split('/')
    return tab[len(tab)-1].split('.')[0]

def date_from_timestamp(tstamp):
    """
    Converts a timestamp to date
    """
    date = datetime.datetime.fromtimestamp(tstamp/1000)
    return date.strftime('%Y-%m-%d %H:%M:%S')

def make_wrong_attempt(user_data, user_exercise):
    """
    Updates user exercise proficiency when a wrong answer is provided
    Not used anymore since most of the evaluation is done by the frontend
    """
    if user_exercise and user_exercise.belongs_to(user_data):
        user_exercise.update_proficiency_model(correct=False)
        user_exercise.put()

        return user_exercise


def getUserExercise(user, user_exe_list):
    """
    Finds a userexercise instance based of user
    """
    for ue in user_exe_list:
        if user == ue.user:
            return ue
    return None



def get_due_date(book, exercise):
    """
    Returns assignment due date
    """
    assignments_list = Assignments.objects.select_related().filter(\
                                               assignment_book=book)
    for assignment in assignments_list:
        if int(exercise.id) in assignment.get_exercises_id():
            return assignment.course_module.closing_time
    return None 
    

def get_assignment(book, exercise):
    """
    Returns assignment given the book and an exercise.
    Used to check if an exercise is part of an assignment
    """
    assignments_list = Assignments.objects.select_related().filter(\
                                                assignment_book=book)
    for assignment in assignments_list:
        if int(exercise.id) in assignment.get_exercises_id():
            return assignment
    return None

def student_grade_all(user, book):
    """
    Returns students score on all the exercises and assignements.
    The data sent are used to genarate the grabook page.
    """
    #prof_list = user_data.get_prof_list()
    student_data_id = UserData.objects.select_related().get(\
                                              user = user,book=book)
    proficient_exercises = student_data_id.get_prof_list()
    all_exercises = Exercise.objects.all()
    all_exercises_id = []
    for aexer in all_exercises:
        all_exercises_id.append(aexer.id)
    #list of non proficient exercises
    #not_proficient_exercises = diff (set(all_exercises_id), \
    #                                      set(proficient_exercises))
    user_grade = {}
    grade = []
    modules = []
    checked_modules = []
    assignments = []
    exe_assign = []

    #get book's open courses
    currentCourse = CourseInstance.objects.filter(Books__in=[book], ending_time__gte = datetime.datetime.now())    
    #get open assignments for the book
    #we get open exercises_course_modules
    course_mods = CourseModule.objects.filter(\
                                opening_time__lte = datetime.datetime.now(),\
                                opening_time__gte = currentCourse.starting_time)
    assignments_list = Assignments.objects.select_related().all().filter(\
                                            assignment_book=book).filter(\
                                            course_module__in = course_mods)
    for assignment in assignments_list:
        ass_l = []
        exe_assign.append(assignment.get_exercises())
        for exercise in assignment.get_exercises():
            ass_l.append({\
                          'name':exercise.name, \
                          'exercise':exercise.description, \
                          'points':0})
        assignments.append({\
                   'assignment':assignment.course_module.name, \
                   'due_date':str(\
                   assignment.course_module.closing_time.date().strftime(\
                                                            '%b %d,%Y')), \
                   'exercises':ass_l})

    bme_list = BookModuleExercise.components.select_related().filter(book=book)

    for bme in bme_list:
        if bme.exercise.id in proficient_exercises:
            grade.append({'exercise':bme.exercise.name, \
                          'description':bme.exercise.description, \
                          'type':bme.exercise.ex_type, \
                          'points':bme.points, \
                          'module':bme.module.name})
        else:
            grade.append({'exercise':bme.exercise.name, \
                          'description':bme.exercise.description, \
                          'type':bme.exercise.ex_type, \
                          'points':0, \
                          'module':bme.module.name})
        if bme.module not in checked_modules:
            checked_modules.append(bme.module)
            if UserModule.objects.filter(user = user, \
                                         book=bme.book, \
                                         module = bme.module).count()>0:
                user_mod = UserModule.objects.get(user = user, \
                                                  book=bme.book, \
                                                  module = bme.module)
                modules.append({'module':bme.module.name, \
                                'proficient':user_mod.is_proficient_at()})
            else:
                modules.append({'module':bme.module.name, 'proficient':False})

    user_grade['modules'] = modules
    user_grade['grades'] = grade
    user_grade['assignments'] = assignments 
    return user_grade



def update_module_proficiency(user_data, module, exercise):
    """
    Updates student module proficiency status
    """
    db_module = Module.objects.get(name=module)
    module_ex_list = db_module.get_proficiency_model(user_data.book)
    user_prof = user_data.get_prof_list()
    with transaction.commit_on_success():
        user_module, exist =  UserModule.objects.get_or_create(\
                                         user=user_data.user, \
                                         book = user_data.book, \
                                         module=db_module)
    dt_now = datetime.datetime.now()
    if user_module:
        if user_module.first_done == None:
            user_module.first_done = dt_now
        user_module.last_done = dt_now
        is_last_exercise = False
        if user_module.proficient_date == datetime.datetime.strptime(\
                                '2012-01-01 00:00:00','%Y-%m-%d %H:%M:%S'):
            if user_prof is None:  
                user_prof = []
            if module_ex_list is None:
                module_ex_list = []
            diff_ex = diff(set(module_ex_list), set(user_prof))
            if exercise is not None and diff_ex is not None:
                if diff_ex == exercise:
                    is_last_exercise = True
            if (set(module_ex_list).issubset(set(user_prof))) \
                                                     or is_last_exercise:
                user_module.proficient_date = dt_now
                user_module.save()
                return True
            else:
                user_module.save()
                return False
        else:
            return True
    return False



def attempt_problem(user_data, user_exercise, attempt_number,
    completed, count_hints, time_taken, attempt_content, module,   
    ex_question, ip_address):
    """
    Stores data related to a KA exercise attempt
    """

    if user_exercise:   # and user_exercise.belongs_to(user_data):
        dt_now = datetime.datetime.now()
        #exercise = user_exercise.exercise
        user_exercise.last_done = dt_now
        # Build up problem log for deferred put
        problem_log = UserExerciseLog(
                user=user_data.user,
                exercise=user_exercise.exercise,
                time_taken=time_taken,
                time_done=dt_now,
                count_hints=count_hints,
                hint_used=int(count_hints) > 0,
                correct=str2bool(completed) and (int(count_hints)==0) \
                                            and (int(attempt_number) == 1),
                count_attempts=attempt_number,
                ex_question=ex_question,
                ip_address=ip_address,
        )


        first_response = (attempt_number == 1 and count_hints == 0) or \
                         (count_hints == 1 and attempt_number == 0)

        #if user_exercise.total_done > 0 and user_exercise.streak == 0 \
        #                                and first_response:
            #bingo('hints_keep_going_after_wrong')

        #just_earned_proficiency = False
        #update list of started exercises
        if not user_data.has_started(user_exercise.exercise):
            user_data.started(user_exercise.exercise.id)

        proficient = user_data.is_proficient_at(user_exercise.exercise)
        if str2bool(completed):

            user_exercise.total_done += 1
            if problem_log.correct:

                # Streak only increments if problem was 
                #solved correctly (on first attempt)
                user_exercise.total_correct += 1
                user_exercise.streak += 1
                user_exercise.longest_streak = max(\
                                               user_exercise.longest_streak, \
                                               user_exercise.streak)
                user_exercise.progress = Decimal(user_exercise.streak)/\
                                         Decimal(user_exercise.exercise.streak)
                if not proficient:
                    problem_log.earned_proficiency = \
                         user_exercise.update_proficiency_ka(\
                                  correct = True, \
                                  ubook = user_data.book)
                    if user_exercise.progress >= 1:
                        if len(user_data.all_proficient_exercises) == 0:
                            user_data.all_proficient_exercises += \
                                         "%s" % user_exercise.exercise.id
                        else:
                            user_data.all_proficient_exercises += \
                                        ",%s" % user_exercise.exercise.id
            else:
                user_exercise.progress = Decimal(user_exercise.streak)/\
                                         Decimal(user_exercise.exercise.streak)
        else:
            if (int(count_hints) ==0) and (attempt_content!='hint') \
                                      and (int(attempt_number) == 1):
            # Only count wrong answer at most once per problem
                if user_exercise.streak - 1 > 0:
                    user_exercise.streak = user_exercise.streak - 1
                else:
                    user_exercise.streak = 0
            user_exercise.progress = Decimal(user_exercise.streak)/\
                                     Decimal(user_exercise.exercise.streak)
            if first_response:
                user_exercise.update_proficiency_model(correct=False)

        problem_log.save()
        user_exercise.save()
        user_data.save()
        if proficient or problem_log.earned_proficiency:
            update_module_proficiency(user_data, \
                                      module, \
                                      user_exercise.exercise)
        return user_exercise, True      #, user_exercise_graph, goals_updated



def attempt_problem_pe(user_data, user_exercise, attempt_number,
    submit_time, time_taken, threshold, score,      
    module, ip_address):
    """
    Stores data related to a PE exercise attempt
    """

    if user_exercise:   # and user_exercise.belongs_to(user_data):
        dt_now =  date_from_timestamp(submit_time)   #datetime.datetime.now()
        exercise = user_exercise.exercise
        user_exercise.last_done = dt_now
        count_hints = 0
        # Build up problem log
        problem_log = UserExerciseLog(
                user=user_data.user,
                exercise=user_exercise.exercise,
                time_taken=int(round(int(time_taken)/1000)),
                time_done=dt_now,
                count_hints=count_hints,
                hint_used=int(count_hints) > 0,
                correct=score>= threshold,
                count_attempts=attempt_number,
                ip_address=ip_address,
        )

        #update list of started exercises
        if not user_data.has_started(exercise):
            user_data.started(exercise.id)

        #just_earned_proficiency = False
        
        user_exercise.total_done += 1
        value = False
        proficient = user_data.is_proficient_at(user_exercise.exercise)
        if problem_log.correct:
            user_exercise.total_correct += 1
            user_exercise.longest_streak = 0 
            value = True
            if not proficient:
                problem_log.earned_proficiency =  \
                            user_exercise.update_proficiency_pe(\
                                          correct = True, \
                                          ubook = user_data.book)
                user_data.earned_proficiency(exercise.id)
                user_data.save()
        problem_log.save()
        user_exercise.save()
        if (proficient or problem_log.earned_proficiency): # and required:
            update_module_proficiency(user_data, module, \
                                                 user_exercise.exercise)
        return user_exercise, value



def log_button_action( user, exercise, module, book, name, \
                       description, action_time, uiid, \
                       browser_family, browser_version, \
                       os_family, os_version, device, ip_address):
    """
    Stores interactions data
    """
    if device is None:
        device = 'PC'
    #update list of started exercises
    user_data, created = UserData.objects.get_or_create(\
                                          user = user, book = book)
    if not user_data.has_started(exercise):
        user_data.started(exercise.id)
    button_log = UserButton( \
                        user = user,
                        exercise = exercise,
                        module = module,
                        book = book,
                        name = name,
                        description = description,
                        action_time =  date_from_timestamp(action_time),
                        uiid = uiid,
                        browser_family = browser_family,
                        browser_version = browser_version,
                        os_family = os_family,
                        os_version = os_version,
                        device = device,
                        ip_address = ip_address)

    return button_log.save(), True

