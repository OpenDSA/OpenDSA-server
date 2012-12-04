# Python 
from icalendar import Calendar, Event 
import json
import csv

# A+ 
from userprofile.models import UserProfile 
 
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

class userValue:
        def __init__(self, name, score):
                self.name = name
                self.score = score
                self.values = []
        def append(self, value):
                self.values.append(value)
        

@login_required
def exercise_summary(request): 

    exercises = []
    BookModExercises = BookModuleExercise.objects.order_by('book', 'module').all()
    for bookmodex in BookModExercises:
            exercises.append(bookmodex.exercise)

    userData = UserData.objects.order_by('user').all()
    userSummaries = UserSummary.objects.order_by('grouping').all()

    users = []  
    for userdata in userData:
            userVal = userValue(userdata.user, userdata.points)
            userid = userdata.user.id
            for exercise in exercises:
                    exKey = str(exercise.id)
                    value = 0
                    try:
                            userSum = userSummaries.get(grouping=userid, key=exKey)
                            value = int(userSum.value)
                    except UserSummary.DoesNotExist:
                            value = 0
                    userVal.append(value)                                    
            users.append(userVal)                  

    context = RequestContext(request, {'users': users, 'exercises':exercises})
     
    return render_to_response("teacher_view/exercise_summary.html", context)     

@login_required
def export_csv(request):

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename="summary.csv"'

    exercises = []
    BookModExercises = BookModuleExercise.objects.order_by('book', 'module').all()
    for bookmodex in BookModExercises:
            exercises.append(bookmodex.exercise)

    userData = UserData.objects.order_by('user').all()
    userSummaries = UserSummary.objects.order_by('grouping').all()

    users = []  
    for userdata in userData:
            userVal = userValue(userdata.user, userdata.points)
            userid = userdata.user.id
            for exercise in exercises:
                    exKey = str(exercise.id)
                    value = 0
                    try:
                            userSum = userSummaries.get(grouping=userid, key=exKey)
                            value = int(userSum.value)
                    except UserSummary.DoesNotExist:
                            value = 0
                    userVal.append(value)                                    
            users.append(userVal)                       
    	
    writer = csv.writer(response)
    exerciseNames = []
    exerciseNames.append('Username')
    exerciseNames.append('Score')
    for exer in exercises:
            exerciseNames.append(exer.name)
            
    writer.writerow(exerciseNames)

    for user in users:
            uservalue = []
            uservalue.append(user.name)
            uservalue.append(user.score)
            for userVal in user.values:
                    uservalue.append(userVal)
            writer.writerow(uservalue)

    return response

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
        BookModExercises = BookModuleExercise.objects.order_by('book', 'module').all()
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
def module_list(request):
     	book = Books.objects.all();
        userName= request.META.get('USER')
	
	currentUserVals = User.objects.filter(username = userName);
        modules = Module.objects.all();
	usermodules = UserModule.objects.all();
	userId = 0
	
        if 'sessionid' in request.COOKIES:
            s = Session.objects.get(pk=request.COOKIES['sessionid'])
            if '_auth_user_id' in s.get_decoded():
                u = User.objects.get(id=s.get_decoded()['_auth_user_id'])
                userId = u.id
        	
	
	userExercs = UserExercise.GetUserExerciseByUserId(userId)
	userScore = 0;
	userDataObjects = UserData.GetUserDataByUserId(userId)

	for userdata in userDataObjects:
		if userdata.user.id == userId:
			userScore = userdata.points;
			break;

	UserModuleDict = dict()
	UserModules = UserModule.GetUserModuleByUserId(userId);
	for usermod in UserModules:
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
       

