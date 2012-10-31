# Python 
from icalendar import Calendar, Event 
 
# A+ 
from userprofile.models import UserProfile 
 
# OpenDSA 
from opendsa.models import Exercise, UserExercise, Module, UserModule, Books, BookModuleExercise, UserSummary
 
# Django
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response 
from django.http import HttpResponse, HttpResponseForbidden 
from course.context import CourseContext 



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
                             {'user_exerciseLst' : userOutputFinalVals, 'exercises' : exercises, 'tempval' : 0 })

class useruiExec:
	def __init__(self, exercise):
		
		self.exercise = exercise;
		self.prof = 0;

	def __init__(self, exercise,isprof):
		self.exercise = exercise
		if isprof:
			self.prof = 1;
		else:
			self.prof =-1;


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
				exerpresent = False;
				for userexer in userExercs:
					if exercise == userexer.exercise:
						self.userExecs.append(useruiExec(userexer,userexer.is_proficient()))
						exerpresent = True;
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
	takenExercs = []	
	profExecs = [];
	nontakenExercs = []
	for userexerc in userExercs:
		if userexerc.is_proficient():
			profExecs.append(userexerc);
		takenExercs.append(userexerc.exercise);

	nonProfExecs = [];
	for userexerc in userExercs:
		if userexerc not in profExecs:	
			nonProfExecs.append(useruiExec(userexerc, False));	
	for exercise in Exercise.objects.all():
		if exercise not in takenExercs:
			nontakenExercs.append(exercise);
		
	return render_to_response("student_view/module_list.html", 
                              {'modules' : userOutputModules , 'profExecs' : profExecs, 'nonProfExecs' : nonProfExecs, 'nontakenExercs' : nontakenExercs })
