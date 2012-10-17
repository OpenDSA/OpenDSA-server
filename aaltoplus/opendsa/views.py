# Python 
from icalendar import Calendar, Event 
 
# A+ 
from userprofile.models import UserProfile 
 
# OpenDSA 
from opendsa.models import Exercise, UserExercise, Module , UserModule
 
# Django 
from django.shortcuts import get_object_or_404, render_to_response 
from django.http import HttpResponse, HttpResponseForbidden 
from course.context import CourseContext 



class userExec:
	def __init__(self, exercise,long_streak,argtype):
		
		self.longest_streak = long_streak
                self.exercise = exercise
		exerexist = False
		if argtype == 0 :
			self.prof= 0
                else:	
			for exerc in Exercise.objects.all():
				if exerc == exercise: 
					if long_streak >= exerc.streak:
						self.prof = 1
					else:
						self.prof = -1
			

class userOutput:
    def __init__(self, name):

 	   self.name = name
	   self.userExecs = []
    
    def append(self, exercise,long_streak):
           self.userExecs.append(userExec(exercise,long_streak,1)); 
    
    def append(self, exercise,long_streak,argType):
           self.userExecs.append(userExec(exercise,long_streak,argType));  

def exercise_summary(request): 
    exercises = Exercise.objects.all() 
    user_exercises = UserExercise.objects.order_by('user', 'exercise').all() 

    userOutputVals = []
    for user_exercise in user_exercises:
            userexist = False;
            for uservals in userOutputVals:
                if uservals.name == user_exercise.user:
                       userexist=True;
                       exerexist =False;
                       for exerc in uservals.userExecs:
                                if user_exercise.exercise == exerc:
                                    exerexist = True;
                    
                       if not exerexist:
                  		uservals.append(user_exercise.exercise , user_exercise.longest_streak,1);  
            if not userexist:
                userOutputVal = userOutput(user_exercise.user);
                userOutputVal.append(user_exercise.exercise, user_exercise.longest_streak,1)
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
				userOutputFinVal.append(userExe.exercise, userExe.longest_streak,1)
		if not execExist:
			userOutputFinVal.append(exercise,0,0)
			execExist = True;
	userOutputFinalVals.append(userOutputFinVal);
				
 
    return render_to_response("teacher_view/exercise_summary.html", 
                              {'user_exerciseLst' : userOutputFinalVals, 'exercises' : exercises, 'tempval' : 0 })

class useruiExec:
	def __init__(self, exercise,userExercs):
		
		self.exercise = exercise
		if (exercise.proficient_date == datetime.datetime.strptime('2012-01-01 00:00:00','%Y-%m-%d %H:%M:%S')):
			self.prof= -1
                else:	
			self.prof = 1

	def __init__(self, exercise,prof):
		self.exercise = exercise
		self.prof = 0

class userOutputModule:
	     
            def __init__(self, mod,userExercs):

                self.name = mod.short_display_name
		self.covers = mod.covers
		self.author = mod.author
		self.prerequisites = mod.prerequisites
		self.prof = 0
		execvals = mod.exercise_list.split(',');
                self.userExecs = []
		for exercise in Exercise.objects.all():
			if exercise.name in execvals:
				if exercise in userExercs:
					self.userExecs.append(useruiExec(exercise,userExercs))
				else:
					self.userExecs.append(useruiExec(exercise,0))
    	
	    def setprof(self, prof):
		self.prof = prof	
            
            def append(self, exercise,long_streak):
                self.userExecs.append(userExec(exercise,long_streak,1)); 

	    def append(self, exercise,long_streak,argType):
                self.userExecs.append(userExec(exercise,long_streak,argType));

def module_list(request):
	modules = Module.objects.all();
	usermodules = UserModule.objects.all();
	userExercs = []
	for userexerc in UserExercise.objects.all():
		if userexerc.user.username == request.META.get('USER'):
			userExercs.append(userexerc);
	userOutputModules = []
	for module in modules:
		userOptMod = userOutputModule(module,userExercs)
		moduleexist = False;
		for usermod in usermodules:
			if usermod.user.username == request.META.get('USER') : 
				if module == usermod.module:
					if usermod.is_proficient_at():
						userOptMod.setprof(-1)
					else:
						userOptMod.setprof(1)
		userOutputModules.append(userOptMod);	
		
	return render_to_response("student_view/module_list.html", 
                              {'modules' : userOutputModules })
