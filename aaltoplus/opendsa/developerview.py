# Python 
from icalendar import Calendar, Event 
 
# A+ 
from userprofile.models import UserProfile 
 
# OpenDSA 
from opendsa.models import Exercise, UserExercise, Module, UserModule, Books, BookModuleExercise, UserSummary, ExerciseModule, UserExerciseLog
 
# Django
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response 
from django.http import HttpResponse, HttpResponseForbidden 
from course.context import CourseContext 

#exeStat class: exercise, and average proficiency score
class exeStat:
    def __init__(self, exercise, score):
        
        self.exercise = exercise
        self.score = score

#function to display the statistics of exercises
#return the percentage of people that have achieved proficiency for each exercise
def exercises_stat(request):
    
    userExercise = UserExercise.objects.order_by('exercise').all();
        
    temp = ''   
    proficient =  0.0 #float fro division
    exercises = []
    
    for userExe in userExercise:
        if userExe.exercise == temp:
            if userExe.is_proficient():
                proficient = proficient + 1.0
        else:
            if not temp == '':
                exercises.append(exeStat(temp, round(proficient/60.0, 2)))
            proficient = 0.0
            temp = userExe.exercise;
                
    return render_to_response("developer_view/exercises_stat.html", {'exercises': exercises })

#function to display a graph for the statistics of exercises
#return the total number of proficiency achieved for each exercise
def exercises_bargraph(request):
    
    userExercise = UserExercise.objects.order_by('exercise').all();
        
    temp = ''   
    proficient =  0
    exercises = []
    
    for userExe in userExercise:
        if userExe.exercise == temp:
            if userExe.is_proficient():
                proficient = proficient + 1
        else:
            if not temp == '':
                exercises.append(exeStat(temp, proficient))
            proficient = 0
            temp = userExe.exercise;
                
    return render_to_response("developer_view/exercises_bargraph.html", {'exercises': exercises })

#function to display a time distribution graph for the statistics of exercises
#return the average time taken for an exercise
#TODO: debug
def exercises_time(request):
    
    userExerciseLog = UserExerciseLog.objects.order_by('exercise').all();
        
    temp = ''   
    time =  0
    exercises = []
    count = 0
    
    for userExeLog in userExerciseLog:
        if userExeLog.exercise == temp:
            time = time + userExeLog.time_taken
            count = count + 1;
        else:
            if not temp == '':
                exercises.append(exeStat(temp, round(time/count, 2)))
            count = 0
            time = 0.0
            temp = userExeLog.exercise;
                
    return render_to_response("developer_view/exercises_time.html", {'exercises': exercises })