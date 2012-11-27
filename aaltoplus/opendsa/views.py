# Python 
from icalendar import Calendar, Event 
import json  
# A+ 
from userprofile.models import UserProfile 
 
# OpenDSA 
from opendsa.models import Exercise, UserExercise, Module, UserModule, Books, BookModuleExercise, UserSummary, UserData
 
# Django
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response 
from django.http import HttpResponse, HttpResponseForbidden 
from course.context import CourseContext 
from django.utils import simplejson
from django.core import serializers


class userExec:
	def __init__(self, exercise,prof):
		
		self.exercise = exercise
		exerexist = False
		self.prof = prof
			

class userOutput:
    def __init__(self, name):

 	   self.name = name
	   self.userExecs = []
    
    def append(self, exercise):
           self.userExecs.append(userExec(exercise, 0)); 
    
    def append(self, exercise, prof):
           self.userExecs.append(userExec(exercise,prof));  

@login_required
def exercise_summary(request): 
##    exercises = Exercise.objects.all()
    exercises = []
    BookModExercises = BookModuleExercise.objects.order_by('book', 'module').all()
    for bookmodex in BookModExercises:
            exercises.append(bookmodex.exercise)

    userData = UserData.objects.order_by('user').all()

    user_exercises = UserExercise.objects.order_by('user', 'exercise').all()

    userOutputVals = []
    for user_exercise in user_exercises:
            userexist = False;
            for uservals in userOutputVals:
                if uservals.name == user_exercise.user:
                       userexist=True;
		       if user_exercise.is_proficient():
                       		uservals.append(user_exercise.exercise, 1);
		       else:  
				uservals.append(user_exercise.exercise, -1); 
            if not userexist:
                userOutputVal = userOutput(user_exercise.user);
                if user_exercise.is_proficient():
                       		userOutputVal.append(user_exercise.exercise, 1);
		else:  
				userOutputVal.append(user_exercise.exercise, -1); 
                userOutputVals.append(userOutputVal)

    userOutputFinalVals = []
    
    for useroutput in userOutputVals: 
	userOutputFinVal = userOutput(useroutput.name);
	execExist =False 
	for exercise in exercises:
		execExist =False   		
		for userExe in useroutput.userExecs:
			if exercise == userExe.exercise:
				execExist = True;
				userOutputFinVal.append(userExe.exercise, userExe.prof)
		if not execExist:
			userOutputFinVal.append(exercise,0)
			execExist = True;
	userOutputFinalVals.append(userOutputFinVal);
				
    return render_to_response("teacher_view/exercise_summary.html", 
                             {'user_exerciseLst' : userOutputFinalVals, 'exercises' : exercises, 'userData' : userData })

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


def module_list(request):
     	book = Books.objects.all();
        username= request.META.get('USER')
        modules = Module.objects.all();
	usermodules = UserModule.objects.all();
	userExercs = []
	userScore = 0;
	userDataObjects = UserData.objects.all()
	UserExercises = UserExercise.objects.all()
	for userdata in userDataObjects:
		if userdata.user.username == username:
			userScore = userdata.points;
			break;
	for userexerc in UserExercises :
		if userexerc.user.username == username:
			userExercs.append(userexerc);
	UserModuleDict = dict()
	for usermod in usermodules:
		if usermod.user.username == username:
			UserModuleDict[usermod.module] =  usermod;

	userOutputModules = []
	for module in modules:
		if module.exercise_list.split(',').count > 0:
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
       

