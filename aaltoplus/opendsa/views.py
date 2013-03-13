# Python 
from icalendar import Calendar, Event 
import json
import csv
import array 
from collections import OrderedDict

# A+ 
from userprofile.models import UserProfile 
from course.models import Course, CourseInstance
 
# OpenDSA 
from opendsa.models import Exercise, UserExercise, Module, UserModule, Books, BookModuleExercise, UserSummary, UserData
 
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



 
def is_authorized(user, book, course):
    obj_book = Books.objects.select_related().get(book_name=book)
    user_prof = UserProfile.objects.get(user=user)
    obj_course = CourseInstance.objects.get(instance_name=course)
    if obj_course in obj_book.courses.all(): 
        return obj_course.is_staff(user_prof)
    else:
        return False


@login_required
def exercise_summary(request, book, course): 
    if is_authorized(request.user,book,course): 
        obj_book = Books.objects.get(book_name=book)
        exercises = []
        BookModExercises = BookModuleExercise.components.select_related().filter(book=obj_book) 
        exercise_table = {}
        #we preparing the data for datatables jquery plugin
        #List containing users data: [["username","points","exercise1 score", "exercise1 score",...]]
        udata_list = []
        columns_list = []
        columns_list.append({"sTitle":"Username"})
        columns_list.append({"sTitle":"Points"})        

        for bookmodex in BookModExercises:
            exercises.append(bookmodex.exercise)
            columns_list.append({"sTitle":str(bookmodex.exercise.name)+'<span class="details" style="display:inline;" data-type="'+str(bookmodex.exercise.description)+'"></span>',"sClass": "center" }) 
        #remove duplicates
        exercises = list(OrderedDict.fromkeys(exercises))
        userData = UserData.objects.select_related().order_by('user').filter(book=obj_book)
        users = []
        for userdata in userData:
            u_data = [] 
            u_data.append(str(userdata.user.username))
            u_data.append(float(userdata.points))
            values = ['--<span class="details" style="display:inline;" data-type="Not Started"></span>' for j in range(len(exercises))]
            prof_ex = userdata.get_prof_list()
            started_ex = userdata.get_started_list()
            for p_ex in prof_ex:
                exercise_t = Exercise.objects.get(id=p_ex)
                if exercise_t in exercises:
                    #get detailed information
                    u_ex = UserExercise.objects.get(user=userdata.user,exercise=exercise_t)
                    values[exercises.index(exercise_t)]= 'Done<span class="details" style="display:inline;" data-type="First done:%s, Last done:%s, Total done:%i, Total correct:%i, Proficiency date:%s"></span>' %(str(u_ex.first_done),str(u_ex.last_done),int(u_ex.total_done),int(u_ex.total_correct),str(u_ex.proficient_date))
            for s_ex in started_ex:
                if Exercise.objects.get(id=s_ex) in exercises and s_ex not in  prof_ex:   
                    exercise_t = Exercise.objects.get(id=s_ex)
                    #get detailed information
                    u_ex = UserExercise.objects.get(user=userdata.user,exercise=exercise_t)
                    values[exercises.index(exercise_t)]= 'Started<span class="details" style="visibility: hidden; display:inline;" data-type="First done:%s, Last done:%s, Total done:%i, Total correct:%i, Proficiency date:%s"></span>' %(str(u_ex.first_done),str(u_ex.last_done),int(u_ex.total_done),int(u_ex.total_correct),str(u_ex.proficient_date))
            u_data = u_data + values
            udata_list.append(u_data)
        context = RequestContext(request, {'book':book,'course':course,'udata_list': udata_list, 'columns_list':columns_list}) 
        return render_to_response("opendsa/class_summary.html", context)
    else:
        return  HttpResponseForbidden('<h1>Page Forbidden</h1>')   

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
       

