# Python 
from icalendar import Calendar, Event 
 
# A+ 
from userprofile.models import UserProfile 
 
# OpenDSA 
from opendsa.models import Exercise, UserExercise, Module 
 
# Django 
from django.shortcuts import get_object_or_404, render_to_response 
from django.http import HttpResponse, HttpResponseForbidden 
from course.context import CourseContext 

 
def exercise_summary(request): 
    """       
    Displays a summary of student's exercises. 
    """ 
 
    exercises = Exercise.objects.all() 
    user_exercises = UserExercise.objects.order_by('user', 'exercise').all() 
    
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
                
               
    userOutputVals = []
    for user_exercise in user_exercises:
            userexist = False;
            for uservals in userOutputVals:
                if uservals.name == user_exercise.user:
                       userexist=True;
                       exerexist =False;
                       for exerc in uservals.userExecs:
                                if user_exercise.exercise == exerc:
                                    exerexist = true;
                    
                if not exerexist:
                    uservals.append(user_exercise.exercise , user_exercise.longest_streak,1);  
            if not userexist:
                userOutputVal = userOutput(user_exercise.user);
                userOutputVal.append(user_exercise.exercise, user_exercise.longest_streak,1)
                userOutputVals.append(userOutputVal)

    userOutputFinalVals = []
    for useroutput in userOutputVals: 
	userOutputVal = userOutput(user_exercise.user);
	for exercise in exercises:
		execExist =False   		
		for userExe in useroutput.userExecs:
			if exercise == userExe.exercise:
				execExist = True;
				userOutputVal.append(userExe.exercise, userExe.longest_streak,1)
		if not execExist:
			userOutputVal.append(exercise,0,0)
	userOutputFinalVals.append(userOutputVal);
				
 
    return render_to_response("teacher_view/exercise_summary.html", 
                              {'user_exerciseLst' : userOutputFinalVals, 'exercises' : exercises, 'tempval' : 0 }) 


def module_view(request):
	modules = Module.objects.all();
	
	return render_to_response("student_view/module_view.html", 
                              {'modulelist' : modules}) 

