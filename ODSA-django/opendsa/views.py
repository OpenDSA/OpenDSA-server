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
from course.views import _get_course_instance
from  exercise.exercise_models import CourseModule
# OpenDSA 
from opendsa.models import Exercise, UserExercise, Module, UserModule, Books, BookModuleExercise, UserData, UserExerciseLog, UserButton, Assignments, BookChapter, UserBook   #UserSummary
from opendsa.statistics import is_authorized, get_active_exercises,convert,is_file_old_enough, get_widget_data, exercises_logs, display_grade,create_book_file 
from opendsa.exercises import get_due_date, get_assignment
from opendsa.forms import AssignmentForm, StudentsForm

# Django
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
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
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.forms.formsets import formset_factory
from django.forms.models import model_to_dict, modelformset_factory
from django import forms
import jsonpickle
import datetime
from django.conf import settings
import os



def home(request):
    open_instances = CourseInstance.objects.all() #filter(ending_time__gte=datetime.now())
    context = RequestContext(request, {"open_instances": open_instances})
    return render_to_response("opendsa/home.html", context)




def widget_data(request):

    if is_file_old_enough('widget_stats.json', 3600):
        get_widget_data()

    try:
          f_handle = open(settings.MEDIA_ROOT + 'widget_stats.json')
          logs = convert(json.load(f_handle))
          f_handle.close()
    except IOError as e:
          print "error ({0}) reading file : {1}".format(e.errno, e.strerror)

    context = RequestContext(request, {'exercises':logs['exercises'], 'users':logs['users']})
    return render_to_response("opendsa/widget.html", context)



def student_management(request, module_id):
    course_module = CourseModule.objects.get(id=module_id)
    book = None
    for bk in  Books.objects.filter(courses=course_module.course_instance):
        book = bk
    if is_authorized(request.user,book.book_name,course_module.course_instance.instance_name): 
        return class_students(request, module_id)
    return HttpResponseForbidden('<h1>No class activity</h1>')


@login_required
def rebuild_book_assignments(request, module_id):
    course_module = CourseModule.objects.get(id=module_id)
    #retrieve books
    book =  Books.objects.filter(courses=course_module.course_instance)[0]
    create_book_file(book)
    messages.success(request, _('Book was updated successfully.'))
#    return HttpResponse()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def class_students(request, module_id):
    course_module = CourseModule.objects.get(id=module_id)
    course_books = []
    course_students = []
    course_books =  list(Books.objects.filter(courses=course_module.course_instance))
    book = course_books[0]
    qs0 =  UserBook.objects.prefetch_related('user').filter(book=book).order_by('user__username') 
    usr_bk =[]

    StudentsFormSet = modelformset_factory(UserBook,form=StudentsForm, extra=0)
    if request.method == "POST":
        formset = StudentsFormSet(request.POST, queryset = qs0)
        if formset.is_valid():
            stud = formset.save()
            messages.success(request, _('Students information were saved successfully.'))
    else:
        formset = StudentsFormSet(queryset = qs0)
    return render_to_response("course/edit_students.html",
                              CourseContext(request, course_instance=course_module.course_instance,
                                                     module=course_module,
                                                     formset=formset
                                             ))





@login_required  
def add_or_edit_assignment(request, module_id):
    """
    This page can be used by teachers to add new modules and edit existing ones.

    @param request: the Django HttpRequest object
    """
    course_module = CourseModule.objects.get(id=module_id)
    #course_books = []
    assignment = None
    #retrieve books
    book =  Books.objects.filter(courses=course_module.course_instance)[0]
    #    if cb not in course_books:
    #        course_books.append(cb)
    #retrieve exercises
    #book_list = []
    #for book in course_books:
    #    #get chapters
    #    chapter_dict = {}
    #    for chapter in BookChapter.objects.filter(book=book):
            #get exercises
    #        exe_dict = {} 
    #        for c_mod in chapter.get_modules():
    #            for b_exe in BookModuleExercise.components.get_mod_exercise_list(book, c_mod):
    #               exe_dict[str(int(b_exe.id))]=str(b_exe.name)
    #        chap_ = '%s-%s' %(str(chapter.name),chapter.id)
    #        chapter_dict[chap_] = exe_dict  
    #    book_ = '%s-%s' %(book.book_url,book.id)
    #    book_list.append({str(book_).replace("'",'"'):chapter_dict})

    #    try:
    #          f_handle = open(settings.MEDIA_ROOT + course_module.course_instance.instance_name + '.json', 'w+')
    #          f_handle.writelines(str(book_list).replace("'",'"'))
    #          f_handle.close()
    #    except IOError as e:
    #         print "error ({0}) writing file : {1}".format(e.errno, e.strerror)

    if Assignments.objects.filter(course_module=course_module).count()>0:
        assignment = get_object_or_404(Assignments, course_module=course_module)
    if request.method == "POST":
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            assignment = form.save()
            messages.success(request, _('The assignment module was saved successfully.'))
    else:
        if not assignment:
            assignment = Assignments(course_module = course_module)
        form = AssignmentForm(instance=assignment)
    return render_to_response("course/edit_module.html",
                              CourseContext(request, course_instance=course_module.course_instance,
                                                     module=course_module,
                                                     form=form,
                                                     book_name = book.book_name
                                             ))

@login_required
def daily_summary(request):
    #exercises_logs()
    context = RequestContext(request, {'daily_stats': str(settings.MEDIA_URL + 'daily_stats.json')})
    return render_to_response("opendsa/daily-ex-stats.html", context)

def all_statistics(request):
    #we only run the whole computaion if the statistic file is older than an hour
    now = datetime.datetime.now()
    stat_file = str(settings.MEDIA_ROOT + 'daily_stats.json')
    statbuf = os.stat(stat_file)
    last_modif = datetime.datetime.fromtimestamp(statbuf.st_mtime)
    diff = now - last_modif
    data = [] 
    if diff > datetime.timedelta(0, 86400, 0): 
        stats =  exercises_logs()
        context = RequestContext(request, {'daily_stats': stats})
    else:
        try:
          f_handle = open(stat_file)
          logs = convert(json.load(f_handle))
          for t in logs:
              data_0 = []
              for key, value in t.iteritems():
                  data_0.append(value)
              data.append(data_0)
          f_handle.close()
        except IOError as e:
          print "error ({0}) reading file : {1}".format(e.errno, e.strerror)

        context = RequestContext(request, {'daily_stats': data})
    return render_to_response("opendsa/all-stats.html", context) 


@login_required
def exercise_summary(request, book, course):
    if is_authorized(request.user,book,course):
        obj_book = Books.objects.get(book_name=book)
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
        assignments_list = list(Assignments.objects.select_related().filter(assignment_book=obj_book).order_by('course_module__closing_time'))
        assignments_points_list = []
        students_assignment_points = []
        for assignment in assignments_list:
            columns_list.append({"sTitle":str(assignment.course_module.name)})
            columns_list1.append({"sTitle":str(assignment.course_module.name)})
            for exercise in assignment.get_exercises():
                for bexe in BookModuleExercise.components.select_related().filter(book=obj_book, exercise = exercise):
                    columns_list.append({"sTitle":str(bexe.exercise.name)+'('+str(bexe.points)+')'+'<span class="details" style="display:inline;" data-type="'+str(bexe.exercise.description)+'"></span>',"sClass": "center" })
        userData = UserData.objects.select_related().filter(book=obj_book, user__is_staff=0).order_by('user')
        users = []
        for userdata in userData:
            if not userdata.user.is_staff and display_grade(userdata.user,obj_book):
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
                    for exercise in assignment.get_exercises():
                        bexe = BookModuleExercise.components.select_related().filter(book=obj_book, exercise = exercise)[0]
                        u_ex = None
                        if UserExercise.objects.filter(user=userdata.user,exercise=exercise).count() > 0: 
                            u_ex = UserExercise.objects.get(user=userdata.user,exercise=exercise)
                        assignment_points += Decimal(bexe.points)
                        exe_str = ''
                        if exercise.id in userdata.get_prof_list():
                            u_points += Decimal(bexe.points) 
                            students_assignment_points += Decimal(bexe.points)                         
                            if u_ex.proficient_date <= assignment.course_module.closing_time:
                                exe_str = '<span class="details" style="display:inline;" data-type="First done:%s, Last done:%s, Total done:%i, Total correct:%i, Proficiency date:%s">Done</span>' %(str(u_ex.first_done),str(u_ex.last_done),int(u_ex.total_done),int(u_ex.total_correct),str(u_ex.proficient_date))
                            else:
                                exe_str = '<span class="details" style="display:inline;" data-type="First done:%s, Last done:%s, Total done:%i, Total correct:%i, Proficiency date:%s">Late</span>' %(str(u_ex.first_done),str(u_ex.last_done),int(u_ex.total_done),int(u_ex.total_correct),str(u_ex.proficient_date))
                        if exercise.id in userdata.get_started_list() and exercise.id not in userdata.get_prof_list():    
                            exe_str = '<span class="details" style="visibility: hidden; display:inline;" data-type="First done:%s, Last done:%s, Total done:%i, Total correct:%i, Proficiency date:%s">Started</span>' %(str(u_ex.first_done),str(u_ex.last_done),int(u_ex.total_done),int(u_ex.total_correct),str(u_ex.proficient_date))  

                        u_assign.append(exe_str)
                    u_assign[0] =  str(students_assignment_points)
                    u_data = u_data + u_assign
                    u_data1.append(str(students_assignment_points))
                u_data[2] = str(u_points )
                udata_list.append(u_data)
                u_data1[2] = str(u_points )
                udata_list1.append(u_data1) 

        context = RequestContext(request, {'book':book,'course':course,'udata_list': udata_list, 'columns_list':columns_list, 'udata_list1': udata_list1, 'columns_list1':columns_list1}) 
        return render_to_response("opendsa/class_summary.html", context)
    else:
        return  HttpResponseForbidden('<h1>Page Forbidden</h1>')



def get_class_activity(request, module_id):
    course_module = CourseModule.objects.get(id=module_id)
    for cb in  Books.objects.filter(courses=course_module.course_instance):
        return exercise_summary(request, cb.book_name, course_module.course_instance.instance_name)
    return HttpResponseForbidden('<h1>No class activity</h1>') 


class exerciseProgress:
        def __init__(self, name):
                self.name = name
                self.proficientUsers = []
                self.inproficientUsers = []
                self.notStartedUsers = []
        def append(self, value, user):
                if value == 1:
                        self.proficientUsers.append(user)
                if value == -1:
                        self.inproficientUsers.append(user)
                if value == 0:
                        self.notStartedUsers.append(user)

@login_required
def progress_summary(request):
        exercises = []
        BookModExercises = BookModuleExercise.components.order_by('book', 'module').all()
        for bookmodex in BookModExercises:
                exercises.append(bookmodex.exercise)

        userData = UserData.objects.order_by('user').all()
        userSummaries = UserSummary.objects.order_by('grouping').all()

        progList = []
        for exercise in exercises:
                exProg = exerciseProgress(exercise.name)
                exKey = str(exercise.id)
                exSummaries = userSummaries.filter(key=exKey)
                for exSummary in exSummaries:
                        userD = userData.get(user__id=exSummary.grouping)
                        user = userD.user
                        if exSummary.value == '0':
                                exProg.append(0, user)
                        if exSummary.value == '1':
                                exProg.append(1, user)
                        if exSummary.value == '-1':
                                exProg.append(-1, user)
                progList.append(exProg)

        context = RequestContext(request, {'progList': progList})

        return render_to_response("teacher_view/progress_summary.html", context)




class useruiExec:
	def __init__(self, exercise, exectype,books):
		if exectype == 0 :
			self.exercise = exercise;
			self.prof = 0;
		else:
			self.userexercise = exercise
			if self.userexercise.is_proficient():
				self.prof = 1;
				for book in books:
					if self.userexercise.exercise.ex_type == 'ka':
						self.points = book.ka_points;
					if self.userexercise.exercise.ex_type == 'ss':
						self.points =  book.ss_points;
					if self.userexercise.exercise.ex_type == 'pe':
						self.points =  book.pe_points;
					if self.userexercise.exercise.ex_type == 'pr':
						self.points =  book.pr_points;
					if self.userexercise.exercise.ex_type == 'ot':
						self.points = book.ot_points;
					break;
			else:
				self.prof =-1;

	
class profUIExec:
  	def __init__(self,userExerc,books):
		self.userexercise= userExerc;
		for book in books:
			if userExerc.exercise.ex_type == 'ka':
				self.points = book.ka_points;
			if userExerc.exercise.ex_type == 'ss':
				self.points =  book.ss_points;
			if userExerc.exercise.ex_type == 'pe':
				self.points =  book.pe_points;
			if userExerc.exercise.ex_type == 'pr':
				self.points =  book.pr_points;
			if userExerc.exercise.ex_type == 'ot':
				self.points = book.ot_points;
			break;

	

class userOutputModule:
	
            def __init__(self, mod,userExercs,books):

                self.name = mod.short_display_name
		self.covers = mod.covers
		self.author = mod.author
		self.prof = 0;
		self.prerequisites = mod.prerequisites
		execvals = mod.exercise_list.split(',');
                self.userExecs = [];
		countExec = 0	
		if execvals.count > 0:	
			for exercise in Exercise.objects.all():
				if exercise.name in execvals:
					if exercise.name != '':
						countExec = countExec + 1;
						exerpresent = False;
						for userexer in userExercs:
							if exercise == userexer.exercise:
								self.userExecs.append(useruiExec(userexer,1,books))
								exerpresent = True;
						if not exerpresent:
							self.userExecs.append(useruiExec(exercise,0,books))
		self.countExec = countExec;		
	    def setprof(self, prof):
		self.prof = prof	


def GetModuleDetails(request):

	userName= request.META.get('USER')
	modules = Module.objects.all();

	userExercs = []
	userScore = 0;
	for userdata in UserData.objects.all():
		if userdata.user.username == userName:
			userScore = userdata.points;
	for userexerc in UserExercise.objects.all():
		if userexerc.user.username == userName:
			userExercs.append(userexerc);
	for module in modules:
		outputMod = userOutputModule(module,userExercs,0);

#	data = serializers.serialize('json',outputMod)	
#	json = simplejson.dumps(data);
#	return_str =  render_to_response({"UserModule" : outputMod })
	return HttpResponse(yaml.dump(outputMod));

def xhr_test(request):
    if request.is_ajax():
        message = "Hello AJAX"
    else:
        message = "Hello"
    return HttpResponse(message);



@login_required
def student_activity(request, student, book):

    book = Books.objects.get(book_name=book)
    user = User.objects.get(username=student)
    userExercs = UserExercise.objects.filter(user=user) #GetUserExerciseByUserId(userId)
    BookModExercises = BookModuleExercise.components.select_related().filter(book=book)
    userDataObjects = UserData.objects.get(user=user,book=book)  #GetUserDataByUserId(userId)
    UserModules = UserModule.objects.select_related().filter(user=user,book=book)
    modules = []
    details = []
    for bme in BookModExercises:
        u_mod = {}
        u_mod['module'] = bme.module.name
        if (UserModule.objects.filter(user=user, module= bme.module).count() > 0) :
            user_module = UserModule.objects.get(user=user, module= bme.module)
            u_mod['first_done'] = user_module.first_done
            u_mod['last_done'] = user_module.last_done
            u_mod['proficiency'] = user_module.proficient_date
            u_exercises = []
            for exerc_id in bme.module.get_required_exercises():
                ex = Exercise.objects.get(id=exerc_id)
                u_exer = UserExercise.objects.get(user=user,exercise=ex)
                u_exercises.append({'exercise':ex.name, 'first_done':u_exer.first_done, 'last_done':u_exer.last_done,'total_done':u_exer.total_done,'total_correct':u_exer.total_correct,'proficiency':u_exer.proficient_date })
            u_mod['exer_mod'] = u_exercises
        else:
            u_mod['first_done'] = 'Not Started'
            u_mod['last_done'] = 'Not Started'
            u_mod['proficiency'] = 'Not Started'
            u_exercises = []
            for exerc_id in bme.module.get_required_exercises():
                ex = Exercise.objects.get(id=exerc_id)
                u_exer = UserExercise.objects.get(user=user,exercise=ex)
                u_exercises.append({'exercise':ex.name, 'first_done':'Not Started', 'last_done':'Not Started','total_done':'Not Started','total_correct':'Not Started','proficiency':'Not Started' })
            u_mod['exer_mod'] = u_exercises

        modules.append(u_mod)

    context = RequestContext(request, {'book':book,'course':course,'udata_list': udata_list, 'columns_list':columns_list})
    return render_to_response("student_view/module_list.html",context)



@login_required
def module_list(request, student, book):
     	book = Books.objects.get(book_name=book)
        user = User.objects.get(username=student)

        userName= request.META.get('USER')
	
	#currentUserVals = User.objects.filter(username = userName);
        #modules = Module.objects.all();
	#usermodules = UserModule.objects.all();
	#userId = 0
	
        #if 'sessionid' in request.COOKIES:
        #    s = Session.objects.get(pk=request.COOKIES['sessionid'])
        #    if '_auth_user_id' in s.get_decoded():
        #        u = User.objects.get(id=s.get_decoded()['_auth_user_id'])
        #        userId = u.id
        	
	
	userExercs = UserExercise.objects.filter(user=user) #GetUserExerciseByUserId(userId)
        BookModExercises = BookModuleExercise.components.select_related().filter(book=book)
	userDataObjects = UserData.objects.get(user=user,book=book)  #GetUserDataByUserId(userId)

	#for userdata in userDataObjects:
	#	if userdata.user.id == userId:
	#		userScore = userdata.points;
	#		break;

	UserModuleDict = dict()
	UserModules = UserModule.objects.select_related().filter(user=user,book=book)  #GetUserModuleByUserId(userId);
	for usermod in UserModules:
		UserModuleDict[usermod.module] =  usermod;

	userOutputModules = []
	for bme in BookModExercises:
                module = bme.module
		if module.get_proficiency_model() and len(bme.module.get_proficiency_model()) > 0:
			userOptMod = userOutputModule(module,userExercs,book)
			if userOptMod.countExec > 0:
				moduleexist = False;
				if module in UserModuleDict.keys():
					if UserModuleDict[module].is_proficient_at():
						userOptMod.setprof(1)
					else:
						userOptMod.setprof(-1)
				userOutputModules.append(userOptMod);	
	takenExercs = []	
	profExecs = [];
	nontakenExercs = []
        profUIExecs = []
	nonProfExecs = [];
	for userexerc in userExercs:
		if userexerc.is_proficient():
			profExecs.append(userexerc);
			profUIExecs.append(profUIExec(userexerc,book));
		takenExercs.append(userexerc.exercise);

	
	for userexerc in userExercs:
		if userexerc not in profExecs:	
			nonProfExecs.append(useruiExec(userexerc, False,book));	
	for exercise in Exercise.objects.all():
		if exercise not in takenExercs:
			nontakenExercs.append(exercise);
	
	return render_to_response("student_view/module_list.html",
                              {'modules' : userOutputModules , 'profExecs' : profUIExecs, 'nonProfExecs' : nonProfExecs, 'nontakenExercs':nontakenExercs,'total':userScore });


