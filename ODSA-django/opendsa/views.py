"""This file contains code defining 
   the views of the  OpenDSA data collection server.
"""


# Python
import json
from decimal import Decimal

# A+
from course.models import CourseInstance
from  exercise.exercise_models import CourseModule
# OpenDSA 
from opendsa.models import Exercise, UserExercise, Books, \
                           BookModuleExercise, UserData, \
                           Assignments, UserBook   
from opendsa.statistics import is_authorized, convert, \
                               is_file_old_enough, get_widget_data, \
                               exercises_logs, display_grade,create_book_file, \
                               devices_analysis,  post_proficiency, students_logs, \
                               glossary_logs, terms_logs, interaction_logs, \
                               interaction_timeseries   
from opendsa.forms import AssignmentForm, StudentsForm, \
                          DelAssignmentForm, AccountsCreationForm, \
                          AccountsUploadForm

from opendsa.exercises import getUserExercise
# Django
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseForbidden, \
                        HttpResponseRedirect
from course.context import CourseContext
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.forms.models import modelformset_factory
from django.db.models import Q
import datetime
from django.conf import settings
import os, random, string, csv
from django.core.mail import send_mail


def home(request):
    """
    The homepage view
    """
    open_instances = CourseInstance.objects.filter(ending_time__gte = \
                                                   datetime.datetime.now())
    context = RequestContext(request, {"open_instances": open_instances})
    return render_to_response("opendsa/home.html", context)




def widget_data(request):
    """
    View to display widget containing OpenDSA statistics
    """
    if is_file_old_enough('widget_stats.json', 3600):
        get_widget_data()

    try:
        f_handle = open(settings.MEDIA_ROOT + 'widget_stats.json')
        logs = convert(json.load(f_handle))
        f_handle.close()
    except IOError as ferror:
        print "error ({0}) reading file : {1}".format(ferror.errno, \
                                                     ferror.strerror)

    context = RequestContext(request, {'exercises':logs['exercises'], \
                                       'users':logs['users']})
    return render_to_response("opendsa/widget.html", context)



def mobile_devices(request):

    mobile_data = None
    if is_file_old_enough('device_stats.json', 43200):
        mobile_data = devices_analysis()

    if mobile_data is None:
        try:
            f_handle = open(settings.MEDIA_ROOT + 'device_stats.json')
            mobile_data = convert(json.load(f_handle))
            f_handle.close()
        except IOError as ferror:
            print "error ({0}) reading file : {1}".format(ferror.errno, \
                                                     ferror.strerror)

    context = RequestContext(request, \
              {'categories':mobile_data['days'], \
               'pc_users':mobile_data['pc_only_users'], \
               'pc_mob_users':mobile_data['pc_mob_users'], \
               'pc_actions':mobile_data['pc_actions'], \
               'mobile_actions':mobile_data['mobile_actions'], \
               'users':mobile_data['users'], \
               'mobile_users':mobile_data['mobile_users'], \
               'interactions':mobile_data['interactions'], \
               'mobile_interactions':mobile_data['mobile_interactions'], \
               'mobile_jsav':mobile_data['mobile_jsav'], \
               'mobile_jsav_distinct_users':mobile_data['mobile_jsav_distinct_users']})

    return render_to_response("opendsa/mobilesdata.html", context)

def student_management(request, module_id):
    """
    View to dsplay all the students enrolled.
    It is used by the instructor to filter the 
    accounts he wants to be shown in the class spreadsheet
    """
    course_module = CourseModule.objects.get(id=module_id)
    book = None
    for i_bk in  Books.objects.filter(courses=course_module.course_instance):
        book = i_bk
    if is_authorized(request.user, book.book_name, \
                     course_module.course_instance.instance_name): 
        return class_students(request, module_id)
    return HttpResponseForbidden('<h1>No class activity</h1>')


@login_required
def rebuild_book_assignments(request, module_id):
    """
    Views responsable of building the list of exercises
    in the book. The JSON file created is used to populate
    the exercise on the add_exercise_to_assignment page.
    """
    course_module = CourseModule.objects.get(id=module_id)
    #retrieve books
    book =  Books.objects.filter(courses=course_module.course_instance)[0]
    create_book_file(book)
    messages.success(request, _('Book was updated successfully.'))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def class_students(request, module_id):
    """
    View which aloow the instructor to edit student's information
    """
    course_module = CourseModule.objects.get(id=module_id)
    course_books = []
    course_books =  list(Books.objects.filter(courses = \
                                              course_module.course_instance))
    book = course_books[0]
    qs0 =  UserBook.objects.prefetch_related('user').filter(book = \
                                             book).order_by('user__username') 

    studentsFormSet = modelformset_factory(UserBook, form=StudentsForm, \
                                                                 extra=0)
    if request.method == "POST":
        formset = studentsFormSet(request.POST, queryset = qs0)
        if formset.is_valid():
            formset.save()
            messages.success(request, \
                     _('Students information were saved successfully.'))
    else:
        formset = studentsFormSet(queryset = qs0)
    return render_to_response("course/edit_students.html",
                              CourseContext(request, \
                              course_instance=course_module.course_instance,
                                                     module=course_module,
                                                     formset=formset
                                             ))





@login_required  
def add_or_edit_assignment(request, module_id):
    """
    This page can be used by teachers to add new 
    modules and edit existing ones.

    @param request: the Django HttpRequest object
    """
    course_module = CourseModule.objects.get(id=module_id)
    #course_books = []
    assignment = None
    #retrieve books
    book =  Books.objects.filter(courses=course_module.course_instance)[0]

    if Assignments.objects.filter(course_module=course_module).count()>0:
        assignment = get_object_or_404(Assignments, \
                                       course_module=course_module)
    if request.method == "POST":
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            assignment = form.save()
            messages.success(request, \
                           _('The assignment module was saved successfully.'))
    else:
        if not assignment:
            assignment = Assignments(course_module = course_module, assignment_book = book)
        form = AssignmentForm(instance=assignment)
    return render_to_response("course/set_exercises.html",
                              CourseContext(request, course_instance = \
                                                course_module.course_instance,
                                                module=course_module,
                                                form=form,
                                                book_name = book.book_name
                                             ))

@login_required
def delete_assignment(request, module_id):
    """
    This page can be used by teachers to delete existing assignments.

    @param request: the Django HttpRequest object
    """
    
    course_module = CourseModule.objects.get(id=module_id)
  
    assignment = None
    if Assignments.objects.filter(course_module = course_module).count()>0: 
        assignment = Assignments.objects.filter(course_module=course_module)[0]
    #retrieve books
    book =  Books.objects.filter(courses=course_module.course_instance)[0]

    #create redirection url that is the teachers' view
    next_url = "/course/%s/%s/teachers/" % ( \
                       course_module.course_instance.course.url, \
                       course_module.course_instance.url)

    if Assignments.objects.filter(course_module = course_module).count()>0:
        assignment = get_object_or_404(Assignments, course_module = \
                                                    course_module)

    if Assignments.objects.filter(assignment_book = book).count() == 1:
        messages.warning(request, \
                 _('There should be at least one assignment in the course.'))
        return HttpResponseRedirect(next_url)
    if request.method == "POST":
        form = DelAssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            assignment.delete()
            course_module.delete()
            messages.success(request, \
                         _('The assignment module was deleted successfully.'))
            return HttpResponseRedirect(next_url)
        else:
            if assignment is not None:
                assignment.delete()
            if course_module is not None:  
                course_module.delete()

            messages.success(request, \
                         _('The assignment module was deleted successfully.'))
            return HttpResponseRedirect(next_url)  
    else:
        if not assignment:
            assignment = Assignments(course_module = course_module)
        form = DelAssignmentForm(instance=assignment)


    return render_to_response("opendsa/edit_assignments.html",
                              CourseContext(request, course_instance = \
                                            course_module.course_instance, \
                                            module=course_module, \
                                            form=form, \
                                             ))



@login_required
def daily_summary(request, course_instance=None):
    """
    Daily statictics view
    """
    courses_intances = CourseInstance.objects.all()

    ci_List = []
    for ci in courses_intances:
      ci_List.append(str(ci.instance_name))

    exercises_logs(course_instance)
   
 
    context = RequestContext(request, {'courses': ci_List, 'instance': course_instance,'daily_stats': str(settings.MEDIA_URL \
                                                      + 'daily_stats.json')})
    return render_to_response("opendsa/daily-ex-stats.html", context)


def prof_statistics(request):
    """
    we only run the whole stats computaion if the statistic
    file is older than an hour
    """
    stat_file = str(settings.MEDIA_ROOT + 'proficiency_stats.json')
    statbuf = os.stat(stat_file)
    last_modif = datetime.datetime.fromtimestamp(statbuf.st_mtime)
    diff = datetime.datetime.now() - last_modif
    data = []
    post_proficiency()
    if  diff > datetime.timedelta(0, 86400, 0):
        context = RequestContext(request, {'daily_stats': post_proficiency() })
    else:
        try:
            f_handle = open(stat_file)
            logs = convert(json.load(f_handle))
            for t_log in logs:
                data_0 = []
                for key, value in t_log.iteritems():
                    data_0.append(value)
                data.append(data_0)
            f_handle.close()
        except IOError as f_error:
            print "error ({0}) reading file : {1}".format(f_error.errno, \
                                                          f_error.strerror)

        context = RequestContext(request, {'daily_stats': data})
    return render_to_response("opendsa/prof-stats.html", context)


def all_statistics(request):
    """
    we only run the whole stats computaion if the statistic 
    file is older than an hour
    """
    stat_file = str(settings.MEDIA_ROOT + 'daily_stats.json')
    statbuf = os.stat(stat_file)
    last_modif = datetime.datetime.fromtimestamp(statbuf.st_mtime)
    diff = datetime.datetime.now() - last_modif
    data = [] 
    if diff > datetime.timedelta(0, 86400, 0): 
        context = RequestContext(request, {'daily_stats': exercises_logs() })
    else:
        try:
            f_handle = open(stat_file)
            logs = convert(json.load(f_handle))
            for t_log in logs:
                data_0 = []
                for key, value in t_log.iteritems():
                    data_0.append(value)
                data.append(data_0)
            f_handle.close()
        except IOError as f_error:
            print "error ({0}) reading file : {1}".format(f_error.errno, \
                                                          f_error.strerror)

        context = RequestContext(request, {'daily_stats': data})
    return render_to_response("opendsa/all-stats.html", context) 


def get_all_student_data(udata, udatas):
    """
    Utility function that retrieves student information
    """
    occurrences = []
    for u_data in udatas:
        if udata.user.username == u_data.user.username:
            occurrences.append(u_data)
    return occurrences

def get_all_prof(udata):
    """
    Returns a list of exercises
    where the student earned proficiency
    """
    profs = []
    for u_data in udata:
        for ex_id in u_data.get_prof_list():
            if ex_id not in profs:
                profs.append(ex_id)
    return profs

def get_all_started(udata):
    """
    Returns all exercises started by the student
    """
    started = []
    for u_data in udata:
        for ex_id in u_data.get_started_list():
            if ex_id not in started:
                started.append(ex_id)
    return started



@login_required
def merged_book(request, book, book1):
    """
    Sepcial method to merge the CS3114AM and CS3114PM sections
    during Fall 2013
    """
    obj_book = Books.objects.get(id = book)
    obj_book1 = Books.objects.get(id = book1)
    udata_list = []
    udata_list1 = []
    columns_list = []
    columns_list1 = []
    columns_list_exe = []  #for exercises
    columns_list.append({"sTitle":"Id"})
    columns_list.append({"sTitle":"Username"})
    columns_list.append({"sTitle":"Points"})
    columns_list1.append({"sTitle":"Id"})
    columns_list1.append({"sTitle":"Username"})
    columns_list1.append({"sTitle":"Points"})

    #get list of book assignments
    assignments_list = Assignments.objects.select_related().filter( \
                                  assignment_book = obj_book).order_by( \
                                  'course_module__closing_time')
    assignments_points_list = []
    students_assignment_points = []
    for assignment in assignments_list:
        columns_list.append({"sTitle":str(assignment.course_module.name)})
        columns_list1.append({"sTitle":str(assignment.course_module.name)})
        for exercise in assignment.get_exercises():
            for bexe in BookModuleExercise.components.filter(book = obj_book, \
                                                         exercise = exercise):
                columns_list.append({"sTitle":str(exercise.name)+ \
                        '('+str(bexe.points)+')' + \
                        '<span class="details" style="display:inline;" \
                        data-type="' + \
                        str(exercise.description) + \
                        '"></span>',"sClass": "center" })

    userData = UserData.objects.select_related().filter(Q(book=obj_book) | \
                                      Q(book=obj_book1)).order_by('user')
    users = []
    exe_bme = {}
    exercises_ = {}
    marked_student = []
    for userdata in userData:
        if not userdata.user.is_staff \
                             and (userdata.user not in marked_student) \
                             and (display_grade(userdata.user,obj_book) \
                             or display_grade(userdata.user,obj_book1)):
            marked_student.append(userdata.user)
            student_activity = get_all_student_data(userdata, userData)
            u_points = 0
            u_data = []
            u_data.append(0)
            u_data.append(str(userdata.user.username))
            u_data.append(0)
            u_data1 = []
            u_data1.append(0)
            u_data1.append(str(userdata.user.username))
            u_data1.append(0)

            for assignment in assignments_list:
                #get points of exercises
                assignment_points = 0
                students_assignment_points = 0
                u_assign = []
                u_assign1 = []
                u_assign.append(0)
                for exercise_id in assignment.get_exercises_id():
                    if exercise_id not in exercises_:
                        exercises_[exercise_id] = Exercise.objects.get( \
                                                        id=exercise_id)
                    exercise = exercises_[exercise_id]
                    if exercise.name not in exe_bme:
                        exe_bme[exercise.name] = \
                             BookModuleExercise.components.filter( \
                                             book = obj_book, \
                                             exercise = exercise)[0]
                    bexe = exe_bme[exercise.name]
                    u_ex = None
                    user_exe = UserExercise.objects.filter(user=userdata.user, \
                                                            exercise=exercise)
                    if user_exe:
                        u_ex = user_exe[0]
                    assignment_points += Decimal(bexe.points)
                    exe_str = ''
                    if exercise.id in get_all_prof(student_activity): 
                        u_points += Decimal(bexe.points)
                        students_assignment_points += Decimal(bexe.points)
                        if u_ex.proficient_date <= \
                                assignment.course_module.closing_time:
                            exe_str = '<span class="details" style= \
                                       "display:inline;" data-type= \
                                       "First done:%s, Last done:%s, \
                                       Total done:%i, Total correct:%i, \
                                       Proficiency date:%s">Done</span>' \
                                       %(str(u_ex.first_done), \
                                       str(u_ex.last_done), \
                                       int(u_ex.total_done), \
                                       int(u_ex.total_correct), \
                                       str(u_ex.proficient_date))
                        else:
                            exe_str = '<span class="details" style= \
                                       "display:inline;" data-type= \
                                       "First done:%s, Last done:%s, \
                                       Total done:%i, Total correct:%i, \
                                       Proficiency date:%s">Late</span>' \
                                       %(str(u_ex.first_done), \
                                       str(u_ex.last_done), \
                                       int(u_ex.total_done), \
                                       int(u_ex.total_correct), \
                                       str(u_ex.proficient_date))
                    if exercise.id in  get_all_started(student_activity) \
                                   and exercise.id not in \
                                   get_all_prof(student_activity):    
                        exe_str = '<span class="details" style= \
                                 "visibility: hidden; display:inline;" \
                                 data-type="First done:%s, Last done:%s, \
                                 Total done:%i, Total correct:%i, \
                                 Proficiency date:%s">Started</span>' \
                                 %(str(u_ex.first_done), \
                                 str(u_ex.last_done), \
                                 int(u_ex.total_done), \
                                 int(u_ex.total_correct), \
                                 str(u_ex.proficient_date))
                    u_assign.append(exe_str)
                u_assign[0] = str(students_assignment_points)
                u_data = u_data + u_assign
                u_data1.append(str(students_assignment_points))

            u_data[2] = str(u_points )
            udata_list.append(u_data)
            u_data1[2] = str(u_points )
            udata_list1.append(u_data1)

    context = RequestContext(request, {'book':book,'course':'CS3114', \
                                       'udata_list': udata_list, \
                                       'columns_list':columns_list, \
                                       'udata_list1': udata_list1, \
                                       'columns_list1':columns_list1})
    return render_to_response("opendsa/class_summary.html", context)




@login_required
def class_summary(request, book, course):
    """
    View creating the data displayed in the class activity spreadsheet
    """
    if is_authorized(request.user, book, course):
        exe_bme = []
        obj_book = Books.objects.get(book_name = book)
        max_book_points = 0
        udata_list = []
        udata_list1 = []
        columns_list = []
        columns_list1 = []
        columns_list_exe = []  #for exercises
        columns_list.append({"sTitle":"Id"})
        columns_list.append({"sTitle":"Username"})
        columns_list.append({"sTitle":"Email"})
        columns_list.append({"sTitle":"Score(%)"})
        #get book instances required exercises
        for bexe in BookModuleExercise.components.filter( \
                                         book = obj_book):
            if Decimal(bexe.points) > Decimal(0):
                exe_bme.append(bexe)

                max_book_points += Decimal(bexe.points)

                columns_list.append({"sTitle":str(bexe.exercise.name)+ \
                                         '('+str(bexe.points)+')'+ \
                                         '<span class="details" \
                                         style="display:inline;" \
                                         data-type="' + \
                                         str(bexe.exercise.description) + \
                                         '"></span>',"sClass": "center" })
        userData = UserData.objects.select_related().filter( \
                                                     book = obj_book, \
                                                     user__is_staff = 0 \
                                                     ).order_by('user')


        users = []
        for userdata in userData:
            if not userdata.user.is_staff and display_grade( \
                                              userdata.user, obj_book):
                u_points = 0
                u_data = []
                u_data.append(0)
                u_data.append(str(userdata.user.username))
                u_data.append(str(userdata.user.email))
                u_data.append(0)
                u_assign = []
                for bexe in exe_bme:
                        u_ex = None
                        user_exe = UserExercise.objects.filter( \
                                                user = userdata.user, \
                                                exercise = bexe.exercise)
                        if not user_exe and (not bexe.exercise.id in userdata.get_prof_list()):
                            exe_str = ''
                            #continue 
                        else:
                            user_exe = user_exe[0]
                            u_ex = user_exe
                            #assignment_points += Decimal(bexe.points)
                            exe_str = ''
                            if bexe.exercise.id in userdata.get_prof_list():
                                u_points += Decimal(bexe.points)
                                #students_assignment_points += Decimal(bexe.points)
                                #if u_ex.proficient_date <= \
                                #    assignment.course_module.closing_time:
                                exe_str = '<span class="details" \
                                      style="display:inline;" \
                                      data-type="First done:%s, \
                                      Last done:%s, Total done:%i, \
                                      Total correct:%i, \
                                      Proficiency date:%s">Done</span>' \
                                      %(str(u_ex.first_done), \
                                      str(u_ex.last_done), \
                                      int(u_ex.total_done), \
                                      int(u_ex.total_correct), \
                                      str(u_ex.proficient_date))
                                #else:
                                #    exe_str = '<span class="details" \
                                #          style="display:inline;" \
                                #          data-type="First done:%s, \
                                #          Last done:%s, Total done:%i, \
                                #          Total correct:%i, \
                                #          Proficiency date:%s">Late</span>' \
                                #          %(str(u_ex.first_done), \
                                #          str(u_ex.last_done), \
                                #          int(u_ex.total_done), \
                                #          int(u_ex.total_correct), \
                                #          str(u_ex.proficient_date))
                            if bexe.exercise.id in userdata.get_started_list() and \
                                          bexe.exercise.id not in \
                                          userdata.get_prof_list():
                                exe_str = '<span class="details" \
                                      style="visibility: hidden; \
                                      display:inline;" \
                                      data-type="First done:%s, \
                                      Last done:%s, Total done:%i, \
                                      Total correct:%i, \
                                      Proficiency date:%s">Started</span>' \
                                      %(str(u_ex.first_done), \
                                      str(u_ex.last_done), \
                                      int(u_ex.total_done), \
                                      int(u_ex.total_correct), \
                                      str(u_ex.proficient_date))

                        u_assign.append(exe_str)
                    #u_assign[0] =  str(students_assignment_points)
                u_data = u_data + u_assign

                if max_book_points == 0:
                    max_book_points = 1
                u_points = (u_points * 100) / max_book_points
                u_data[3] = str("%.2f" % round(u_points,2))
                udata_list.append(u_data)


        context = RequestContext(request, {'book':book, \
                                           'max_points':max_book_points, \
                                           'course':course, \
                                           'udata_list': udata_list, \
                                           'columns_list':columns_list})
        return render_to_response("opendsa/all_summary.html", context)
    else:
        return  HttpResponseForbidden('<h1>Page Forbidden</h1>')



@login_required
def exercise_summary(request, book, course):
    """
    View creating the data displayed in the class assignments activity spreadsheet
    """
    if is_authorized(request.user, book, course):
        obj_book = Books.objects.get(book_name = book)
        udata_list = []
        udata_list1 = []
        wrong_exe = []
        columns_list = []
        columns_list1 = []
        columns_list_exe = []  #for exercises
        columns_list.append({"sTitle":"Id"})
        columns_list.append({"sTitle":"Username"})
        columns_list.append({"sTitle":"Email"})
        columns_list.append({"sTitle":"Score(%)"})
        columns_list1.append({"sTitle":"Id"})
        columns_list1.append({"sTitle":"Username"})
        columns_list1.append({"sTitle":"Email"})
        columns_list1.append({"sTitle":"Score(%)"})
        #get list of book assignments
        assignments_list = Assignments.objects.select_related().filter( \
                           assignment_book=obj_book).order_by( \
                                'course_module__closing_time')
        max_assignments_points = 0
        students_assignment_points = []
        u_book = UserBook.objects.filter(book = obj_book)
        exe_bme = {}
        assign_exe = {}
        assignments_list_tmp = []
        for assignment in assignments_list:
            if assignment.course_module.course_instance.instance_name == course:
                assignments_list_tmp.append(assignment)
                columns_list.append({"sTitle":str(assignment.course_module.name)})
                columns_list1.append({"sTitle":str(assignment.course_module.name)})
                assign_exe[assignment.course_module.name] = assignment.get_exercises()
                for exercise in assign_exe[assignment.course_module.name]:
                    if BookModuleExercise.components.filter( \
                                             book = obj_book, \
                                             exercise = exercise).count() == 0:
                        continue
                    bexe = BookModuleExercise.components.filter( \
                                               book = obj_book, \
                                               exercise = exercise)[0]
                    exe_bme[exercise.name] = bexe
  
                    max_assignments_points += Decimal(bexe.points)
  
                    columns_list.append({"sTitle":str(exercise.name)+ \
                                         '('+str(bexe.points)+')'+ \
                                         '<span class="details" \
                                         style="display:inline;" \
                                         data-type="' + \
                                         str(exercise.description) + \
                                         '"></span>',"sClass": "center" })

        #we only work assignments relevants to this course instance
        assignments_list = assignments_list_tmp
        userData = UserData.objects.select_related().filter( \
                                                     book = obj_book, \
                                                     user__is_staff = 0 \
                                                     ).order_by('user')
        
        users = []
        for userdata in userData:
            if not userdata.user.is_staff and display_grade( \
                                              userdata.user, obj_book):
                u_points = 0
                u_data = []
                u_data.append(0)
                u_data.append(str(userdata.user.username))
                u_data.append(str(userdata.user.email))
                u_data.append(0)
                u_data1 = []
                u_data1.append(0)
                u_data1.append(str(userdata.user.username))
                u_data1.append(str(userdata.user.email))
                u_data1.append(0)

                for assignment in assignments_list:
                    #get points of exercises
                    assignment_points = 0
                    students_assignment_points = 0
                    u_assign = []
                    u_assign1 = []
                    u_assign.append(0)

                    for exercise in assign_exe[assignment.course_module.name]:
                        if exercise.name not in  exe_bme:
                            if exercise.name not in wrong_exe:
                                wrong_exe.append(str(exercise.name))
                            continue

                        bexe = exe_bme[exercise.name]
                        u_ex = None
                        user_exe = UserExercise.objects.filter( \
                                                user = userdata.user, \
                                                exercise = exercise)
                        if not user_exe and (not exercise.id in userdata.get_prof_list()):
                            exe_str = ''
                            #continue 
                        else:
                            user_exe = user_exe[0]
                            u_ex = user_exe
                            assignment_points += Decimal(bexe.points)
                            exe_str = ''
                            if exercise.id in userdata.get_prof_list():
                                #u_points += Decimal(bexe.points) 
                                #students_assignment_points += Decimal(bexe.points) 
                                if u_ex.proficient_date <= \
                                    assignment.course_module.closing_time:
                                    u_points += Decimal(bexe.points)
                                    students_assignment_points += Decimal(bexe.points)
                                    exe_str = '<span class="details" \
                                          style="display:inline;" \
                                          data-type="First done:%s, \
                                          Last done:%s, Total done:%i, \
                                          Total correct:%i, \
                                          Proficiency date:%s">Done</span>' \
                                          %(str(u_ex.first_done), \
                                          str(u_ex.last_done), \
                                          int(u_ex.total_done), \
                                          int(u_ex.total_correct), \
                                          str(u_ex.proficient_date))
                                else:
                                    penalty = Decimal(bexe.points) * (Decimal(1)-Decimal(assignment.course_module.late_submission_penalty))
                                    u_points += Decimal(penalty)
                                    students_assignment_points += Decimal(penalty)
                                    exe_str = '<span class="details" \
                                          style="display:inline;" \
                                          data-type="First done:%s, \
                                          Last done:%s, Total done:%i, \
                                          Total correct:%i, \
                                          Proficiency date:%s">Late</span>' \
                                          %(str(u_ex.first_done), \
                                          str(u_ex.last_done), \
                                          int(u_ex.total_done), \
                                          int(u_ex.total_correct), \
                                          str(u_ex.proficient_date))
                            if exercise.id in userdata.get_started_list() and \
                                          exercise.id not in \
                                          userdata.get_prof_list():    
                                exe_str = '<span class="details" \
                                      style="visibility: hidden; \
                                      display:inline;" \
                                      data-type="First done:%s, \
                                      Last done:%s, Total done:%i, \
                                      Total correct:%i, \
                                      Proficiency date:%s">Started</span>' \
                                      %(str(u_ex.first_done), \
                                      str(u_ex.last_done), \
                                      int(u_ex.total_done), \
                                      int(u_ex.total_correct), \
                                      str(u_ex.proficient_date))  
                    
                        u_assign.append(exe_str)
                    u_assign[0] =  str(students_assignment_points)
                    u_data = u_data + u_assign
                    u_data1.append(str(students_assignment_points))
               
                if max_assignments_points == 0:
                    max_assignments_points = 1 
                u_points = (u_points * 100) / max_assignments_points 
                u_data[3] = str("%.2f" % round(u_points,2))
                udata_list.append(u_data)
                u_data1[3] = str("%.2f" % round(u_points,2))
                udata_list1.append(u_data1) 


        context = RequestContext(request, {'book':book, \
                                           'max_points':max_assignments_points, \
                                           'course':course, \
                                           'udata_list': udata_list, \
                                           'wrong_exe': str(wrong_exe).strip('[]'), \
                                           'columns_list':columns_list, \
                                           'udata_list1': udata_list1, \
                                           'columns_list1':columns_list1}) 
        return render_to_response("opendsa/class_summary.html", context)
    else:
        return  HttpResponseForbidden('<h1>Page Forbidden</h1>')



def get_class_activity(request, module_id):
    """
    efouh: Leaving this for now. 
    """
    if module_id:
        course_module = CourseModule.objects.get(id=module_id)
        for c_book in  Books.objects.filter(courses=course_module.course_instance):
            return exercise_summary(request, c_book.book_name, \
                   course_module.course_instance.instance_name)
        return HttpResponseForbidden('<h1>No class activity</h1>') 
    return HttpResponseForbidden('<h1>No class activity</h1>')


def get_all_activity(request, module_id):
    """
    efouh: Leaving this for now. 
    """
    if module_id:
        course_module = CourseModule.objects.get(id=module_id)
        for c_book in  Books.objects.filter(courses=course_module.course_instance):
            return class_summary(request, c_book.book_name, \
                   course_module.course_instance.instance_name)
        return HttpResponseForbidden('<h1>No class activity</h1>')
    return HttpResponseForbidden('<h1>No class activity</h1>')


def interactions_data_home(request):
    """
    The students interactions data home view
    """
    open_instances = CourseInstance.objects.all()
    context = RequestContext(request, {"open_instances": open_instances, \
                                         'data': "[]", \
                                         'headers':"[]", \
                                         'courseinstance':'None'})
    return render_to_response("opendsa/interactionsdata.html", context)



def interactionsts_data_home(request):
    """
    The students interactions data home view
    """
    open_instances = CourseInstance.objects.all()
    context = RequestContext(request, {"open_instances": open_instances, \
                                         'data': "[]", \
                                         'headers':"[]", \
                                         'courseinstance':'None'})
    return render_to_response("opendsa/interactionstsdata.html", context)


def interactionsts_data(request, course_instance=None):
  
  if course_instance:
    headers, interactions_activity = interaction_timeseries(course_instance)
    #print interactions_activity
    columns_list = []
    for title in headers:
      columns_list.append({"sTitle":str(title)})
    open_instances = CourseInstance.objects.all()

    context = RequestContext(request, {'courseinstance':course_instance, \
                                           'data': interactions_activity, \
                                           'headers':columns_list, \
                                           'open_instances': open_instances})
    return render_to_response("opendsa/interactionstsdata.html", context)
  else:
    return HttpResponseForbidden('<h1>No class activity</h1>')




def interactions_data(request, course_instance=None):

  if course_instance:
    headers, interactions_activity = interaction_logs(course_instance)
    #print interactions_activity
    columns_list = []
    for title in headers:
      columns_list.append({"sTitle":str(title)})
    open_instances = CourseInstance.objects.all()

    context = RequestContext(request, {'courseinstance':course_instance, \
                                           'data': interactions_activity, \
                                           'headers':columns_list, \
                                           'open_instances': open_instances})
    return render_to_response("opendsa/interactionsdata.html", context)
  else:
    return HttpResponseForbidden('<h1>No class activity</h1>')


def glossary_module_data_home(request):
    """
    The students data home view
    """
    open_instances = CourseInstance.objects.all()
    context = RequestContext(request, {"open_instances": open_instances, \
                                         'data': "[]", \
                                         'data1': "[]", \
                                         'headers':"[]", \
                                         'headers1':"[]", \
                                         'courseinstance':'None'})
    return render_to_response("opendsa/glossarydata.html", context)


def glossary_module_data(request, course_instance=None):

  if course_instance:
    columns_list = []
    columns_list.append({"sTitle":"Users"})
    columns_list.append({"sTitle":"Module views"})
    columns_list.append({"sTitle":"Glossary Terms Clicks"})
    columns_list.append({"sTitle":"Glossary Term Clicks (W)"})
    open_instances = CourseInstance.objects.all()

    columns_list1 = []
    columns_list1.append({"sTitle":"Terms"})
    columns_list1.append({"sTitle":"# Clicks"})

    glossary_activity = glossary_logs(course_instance)
    term_activity, word_array = terms_logs(course_instance)
    context = RequestContext(request, {'courseinstance':course_instance, \
                                           'data': glossary_activity, \
                                           'data1': term_activity, \
                                           'wordscount' : word_array, \
                                           'headers':columns_list, \
                                           'headers1':columns_list1, \
                                           'open_instances': open_instances})
    return render_to_response("opendsa/glossarydata.html", context)
  else:
    return HttpResponseForbidden('<h1>No class activity</h1>')




def student_work(request, course_instance=None):

  if course_instance:
    columns_list = []
    columns_list.append({"sTitle":"Id"})
    columns_list.append({"sTitle":"Exe M1"})
    columns_list.append({"sTitle":"Exe M2"})
    columns_list.append({"sTitle":"Exe F"})
    #columns_list.append({"sTitle":"Interactions"})
#    columns_list.append({"sTitle":"Total KA"})
#    columns_list.append({"sTitle":"Correct KA"})
#    columns_list.append({"sTitle":"Total KAV"})
#    columns_list.append({"sTitle":"Correct KAV"})
#    columns_list.append({"sTitle":"Total PE"})
#    columns_list.append({"sTitle":"Correct PE"})
#    columns_list.append({"sTitle":"Total SS"})
#    columns_list.append({"sTitle":"Correct SS"})
    open_instances = CourseInstance.objects.all()

    students_activity = students_logs(course_instance)
    context = RequestContext(request, {'courseinstance':course_instance, \
                                           'data': students_activity, \
                                           'headers':columns_list, \
                                           'open_instances': open_instances})
    return render_to_response("opendsa/studentsdata.html", context)
  else:
    return HttpResponseForbidden('<h1>No class activity</h1>')


def students_data_home(request):
    """
    The students data home view
    """
    open_instances = CourseInstance.objects.all()
    context = RequestContext(request, {"open_instances": open_instances, \
                                         'data': "[]", \
                                         'headers':"[]", \
                                         'courseinstance':'None'})
    return render_to_response("opendsa/studentsdata.html", context)



#utility function to generate passwords
#see http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
   return ''.join(random.choice(chars) for _ in range(size))

@login_required
def create_accounts(request, module_id):
    """
     Views responsible of creating students accounts
     An email is sent to the course teachers at 
     the end of the process
    """

    course_module = CourseModule.objects.get(id=module_id)

    form = None
    if request.method == 'POST':
        form = AccountsCreationForm(request.POST)
        current_user = request.user
        account_created = 0
        roster = 'username,password\n'
        if form.is_valid():
            for x in range(0, form.cleaned_data['account_number']):
                username = form.cleaned_data['account_prefix'] + str(x)
                password = id_generator()
                if User.objects.filter(username=username).count()==0:
                    User.objects.create_user( username, '', password)
                    account_created = account_created + 1
                    roster = roster + username + ',' + password + '\n'
            messages.success(request, \
                           _('%s account(s) created successfully. The roster has been emailed to %s.' %(account_created, current_user.email)))
            #send notification email
            subject = '[OpenDSA] Students accounts created'
            message = 'List of accounts created.\n\n\n\n' + roster
            send_mail(subject, message, 'noreply@opendsa.cc.vt.edu', [current_user.email], fail_silently=False)

    else:
        form = AccountsCreationForm()


    return render_to_response("opendsa/studentsaccounts.html",
                              CourseContext(request, course_instance = \
                                            course_module.course_instance, \
                                            module=course_module, \
                                            form=form, \
                                             ))



@login_required
def upload_accounts(request, module_id):
    """
     Views responsible of creating students accounts
     the instructor upload his course roaster
     An email is sent to each student 
    """

    course_module = CourseModule.objects.get(id=module_id)
    book =  Books.objects.filter(courses=course_module.course_instance)[0]

    form = None
    if request.method == 'POST':
        form = AccountsUploadForm(request.POST, request.FILES)
        #current_user = request.user
        if form.is_valid():
                account_created = 0
            #with open(request.FILES['classfile'], 'rb') as csvfile:
                csvfile = request.FILES['classfile']
                listreader = csv.reader(csvfile.read().splitlines())  #, delimiter=',', quotechar='|')
                for row in listreader:
                    username = row[0]
                    email = row[1]
                    password = id_generator()
                    if User.objects.filter(username=username).count()==0:
                        User.objects.create_user( username, email, password)
                        account_created = account_created + 1
                        #send notification email
                        subject = '[OpenDSA] account created'
                        message = 'Your OpenDSA account has been  created for the Book instance at %s.\n\n\n username: %s\n password:%s' %(book.book_url,username, password)
                        send_mail(subject, message, 'noreply@opendsa.cc.vt.edu', [email], fail_silently=False)


                messages.success(request, \
                           _('%s account(s) created successfully.' %account_created))

    else:
        form = AccountsUploadForm()


    return render_to_response("opendsa/studentsupload.html",
                              CourseContext(request, course_instance = \
                                            course_module.course_instance, \
                                            module=course_module, \
                                            form=form, \
                                             ))
