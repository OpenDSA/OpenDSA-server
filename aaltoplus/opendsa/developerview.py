# Python 
from icalendar import Calendar, Event 
 
#Django
from django.contrib.auth.models import User

# A+ 
from userprofile.models import UserProfile 
 
# OpenDSA 
from opendsa.models import Exercise, UserExercise, Module, UserModule, Books, BookModuleExercise, UserSummary, ExerciseModule, UserExerciseLog, UserButton
 
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

def student_list(request):
    users = UserProfile.objects.all();
    
    students = []
    
    for user in users:
        if not user.user.is_staff:
            if not user.user.is_superuser:
               # print(user.user.id)
                students.append(user.user)
    
    return render_to_response("developer_view/student_list.html", {'students': students })

class document_ready_activity:
    def __init__(self, module, activity_num):
        
        self.module = module
        self.activity_num = activity_num
     
    def update_activity(self):
        self.activity_num = self.activity_num + 1

def student_exercise(request, student):
    userButtons = UserButton.objects.filter(user=student)

    activities = []
    max = 0
    
    for userButton in userButtons:
        flag = 0
        if userButton.name == 'document-ready':
            for activity in activities:
                if activity.module == userButton.module:
                    activity.update_activity()
                    if max < activity.activity_num:
                        max = activity.activity_num
                    flag = 1
                    break
            if flag == 0:
                doc_activity = document_ready_activity(userButton.module, 1)
                activities.append(doc_activity)
        #else:
         #   if userButton.name == 'jsav-forward' or userButton.name == 'jsav-backward':
         #       doc_activity.update_activity()
    
    number = len(activities)
        
    return render_to_response("developer_view/student_exercise.html", {'activities': activities, 'number': number, 'max': max, 'student': student })

def exercise_list(request, student, module):
    userButtons = UserButton.objects.filter(user=student).filter(module=module)
    
    exercises = []
    
    for userButton in userButtons:
        flag = 0
        for exercise in exercises:
            if userButton.exercise == exercise:
                flag = 1
                break
        if flag == 0 and not userButton.exercise.id == 50 :
            exercises.append(userButton.exercise)
        
    return render_to_response("developer_view/exercise_list.html", {'exercises': exercises, 'student': student, 'module':module })

class exercise_step:
    def __init__(self, step_num, time, is_backward):
        
        self.step_num = step_num
        self.time = time
        self.is_backward = is_backward

def exercise_detail(request, student, module, exercise):
    userButtons = UserButton.objects.filter(user=student).filter(module=module).filter(exercise=exercise)

    max = 0

    exe_steps = []
    current_time = 0
    current_step = 0

    for userButton in userButtons:
        flag = 0

        if userButton.name == 'jsav-forward':
            step = int(userButton.description[:userButton.description.find('/')])

            if current_time == 0 or userButton.action_time < current_time or not step - current_step == 1:
                current_time = userButton.action_time
                current_step = step
                continue

            for exe_step in exe_steps:
                if exe_step.step_num == step:
                    exe_step.time = exe_step.time + int((userButton.action_time - current_time).total_seconds())
                    flag = 1
                    current_time = userButton.action_time
                    current_step = step
                    if max < exe_step.time:
                        max = exe_step.time
                    break
                
            if flag == 0:
                time_diff = int((userButton.action_time - current_time).total_seconds())
                exe_steps.append(exercise_step(step, time_diff, 'false'))
                if max < time_diff:
                     max = time_diff                
                current_time = userButton.action_time
                current_step = step
                
        if userButton.name == 'jsav-backward':
            step = int(userButton.description[:userButton.description.find('/')])

            if current_time == 0 or userButton.action_time < current_time or not step - current_step == -1:
                current_time = userButton.action_time
                current_step = step
                continue            
            
            for exe_step in exe_steps:
                if exe_step.step_num == step:
                    exe_step.time = exe_step.time + int((userButton.action_time - current_time).total_seconds())
                    if max < exe_step.time:
                        max = exe_step.time                    
                    exe_step.is_backward = 'true'
                    flag = 1
                    current_time = userButton.action_time
                    current_step = step
                    break
                
            if flag == 0:
                time_diff = int((userButton.action_time - current_time).total_seconds())                
                exe_steps.append(exercise_step(step, time_diff, 'true'))  
                if max < time_diff:
                     max = time_diff
                current_time = userButton.action_time
                current_step = step
        
    number = len(exe_steps)
                  
    #print(max)
    
    userExercises = UserExercise.objects.filter(user=student).filter(exercise=exercise)
    
    review_dates = []
    
    if len(userExercises) == 1:
        
        proficient_date = userExercises[0].proficient_date
    
        userButtons = UserButton.objects.filter(action_time__gt = proficient_date).filter(user=student).filter(exercise=exercise)
        
        #print(userButtons)
        
        for userButton in userButtons:
            if proficient_date.date() < userButton.action_time.date():
                print(userButton.user_id)
                review_dates.append(userButton.action_time.date())
                
        proficient_date = proficient_date.date()
        
    else:
        proficient_date = 'not_proficient'

    
    review_dates = list(set(review_dates))
    
    #print(proficificent_date)
    
    return render_to_response("developer_view/exercise_detail.html", {'exe_steps': exe_steps, 'number':number, 'max': max, 'proficient_date': proficient_date, 'review_dates':review_dates })

