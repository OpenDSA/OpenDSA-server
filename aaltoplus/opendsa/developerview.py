# Python 
from icalendar import Calendar, Event 
 
#Django
from django.contrib.auth.models import User

# A+ 
from userprofile.models import UserProfile 
 
# OpenDSA 
from opendsa.models import Exercise, UserExercise, Module, UserModule, Books, BookModuleExercise, UserSummary, ExerciseModule, UserExerciseLog, UserButton, UserData
 
# Django
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, render_to_response 
from django.http import HttpResponse, HttpResponseForbidden 
from course.context import CourseContext 
from collections import OrderedDict
import time

#exeStat class: exercise, and average proficiency score
class exeStat:
    def __init__(self, exercise, score):
        self.exercise = exercise
        self.score = score

#function to display the statistics of exercises
#return the percentage of people that have achieved proficiency for each exercise
@staff_member_required
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
@staff_member_required
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
@staff_member_required
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

#This function responds student list (not staff or super user)
#The student information includes id(in the database), user name, and email, etc
@staff_member_required
def student_list(request):
    userProfiles = UserProfile.objects.all();
    
    students = []
    
    for profile in userProfiles:
        if not profile.user.is_staff and not profile.user.is_superuser:
                students.append(profile.user)
    
    return render_to_response("developer_view/student_list.html", {'students': students })

class document_ready_activity:
    def __init__(self, module, activity_num, max):
        
        self.module = module
        self.activity_num = activity_num
        self.max = max
     
    def update_activity(self):
        self.activity_num = self.activity_num + 1
        
    def set_max(self, max):
        self.max = max
        
    def get_activity_num_print(self):
        return float(self.activity_num)/float(self.max)*1000.0
    
class proficient_exercises:
    def __init__(self, date, exercises, number):
        self.date = date
        self.exercises = exercises
        self.number = number
        
    def add_exercise(self,exercise):
        self.exercises.append(exercise)
        self.number = self.number + 1

    def get_number_print(self):
        return self.number*20

@staff_member_required
def student_exercise(request, student):
    userButtons = UserButton.objects.filter(user=student, name='document-ready')

    activities = []
    max = 0
    
    for userButton in userButtons:
        flag = 0
        for activity in activities:
            if activity.module == userButton.module:
                activity.update_activity()
                if max < activity.activity_num:
                    max = activity.activity_num
                flag = 1
                break
        if flag == 0:
            doc_activity = document_ready_activity(userButton.module, 1, 0)
            if max < doc_activity.activity_num:
                max = doc_activity.activity_num
            activities.append(doc_activity)
        #else:
         #   if userButton.name == 'jsav-forward' or userButton.name == 'jsav-backward':
         #       doc_activity.update_activity()
    
    #number = len(activities)
    
    for activity in activities:
        activity.set_max(max)
    
    userExercises = UserExercise.objects.filter(user=student).order_by('proficient_date')
    
    exercises = []
    
    for userExercise in userExercises:
        if userExercise.is_proficient():
            flag = 0
            date = userExercise.proficient_date.date()
            for exercise in exercises:
                if date == exercise.date:
                    exercise.add_exercise(userExercise.exercise)
                    flag = 1
                    break
            if flag == 0:
                temp = [userExercise.exercise]
                exercises.append(proficient_exercises(date, temp, 1))
        
    return render_to_response("developer_view/student_exercise.html", {'activities': activities, 'student': student, 'exercises': exercises, 'max': max })

@staff_member_required
def exercise_list(request, student):
  interesting_events = ['jsav-end', 'jsav-forward', 'jsav-array-click', 'odsa-award-credit']
  
  userButtons = UserButton.objects.filter(user=student, name__in=interesting_events).only('exercise', 'module', 'name', 'action_time').order_by('action_time')
  
  user_exercises = dict(UserExercise.objects.filter(user=student).values_list('exercise', 'proficient_date'))
  
  print userButtons.query
  
  exercises = OrderedDict()
  
  for userButton in userButtons:
    if userButton.exercise.name not in exercises:
      #print userButton.exercise
      exercises[userButton.exercise.name] = {}
      exercises[userButton.exercise.name]['id'] = userButton.exercise.id
      exercises[userButton.exercise.name]['module'] = userButton.module.name
      exercises[userButton.exercise.name]['type'] = userButton.exercise.ex_type
      exercises[userButton.exercise.name]['start_time'] = userButton.action_time
      if userButton.exercise.id in user_exercises:
        exercises[userButton.exercise.name]['proficient_time'] = user_exercises[userButton.exercise.id]
      else:
        exercises[userButton.exercise.name]['proficient_time'] = ''
  
  #print [ u.exercise.name for u in userButtons]
  #print exercises

  return render_to_response("developer_view/exercise_list.html", {'exercises': exercises, 'student': student})

@staff_member_required
def non_required_exercise_use(request):
  # Get all slideshow exercises (the ones that are not required)
  exercises = Exercise.objects.filter(ex_type='ss')
  exer_ids = [x.id for x in exercises]
  
  user_exer_data = OrderedDict()
  
  for user_data in UserData.objects.filter(book=5):
    started_exer_ids = UserButton.objects.filter(user=user_data.user, exercise__ex_type='ss').values_list('exercise_id', flat=True)
    
    # Eliminate duplicates
    seen = set()
    seen_add = seen.add
    started_exer_ids = [ x for x in started_exer_ids if x not in seen and not seen_add(x)]
    
    prof_exer_ids = []
    
    for exer_id in user_data.all_proficient_exercises.split(','):
      if exer_id.isdigit() and long(exer_id) in exer_ids:
        prof_exer_ids.append(int(exer_id))
    
    user_exer_data[user_data.user.id] = {}
    user_exer_data[user_data.user.id]['started_exers'] = started_exer_ids
    user_exer_data[user_data.user.id]['prof_exers'] = prof_exer_ids
  
  return render_to_response("developer_view/non_req_exercises.html", {'exercises': exercises, 'user_exer_data': user_exer_data})

@staff_member_required
def slideshow_cheating(request, student):
  # Count of how many times the student completed each slideshow
  exer_count = OrderedDict()
  
  # Maps an exercise ID to the uiid of the first instance of the exercise where the student obtained proficiency
  exer_uiids = OrderedDict()
  cheated_exer_names = []
  
  # Filter UserExerciseLog by user and slideshows where the user gained proficiency
  # Possible to also limit by a time threshold (to reduce the number of results that require processing, but then we can't determine the total number of completions (time_taken__lte=2)
  user_exercise_logs = UserExerciseLog.objects.filter(user=student, exercise__ex_type='ss', earned_proficiency=1).order_by('time_done').only('exercise', 'time_taken', 'count_attempts')
  
  #print user_exercise_logs.query
  #print 'Count: ' + str(user_exercise_logs.count())
  #print user_exercise_logs.values('id', 'time_taken')
  
  for uel in user_exercise_logs:
    # We only care about the first time a user gets proficiency with an exercise
    if uel.exercise.name not in exer_uiids.keys():
      # Initialize the completion counter for the exercise
      exer_count[uel.exercise.name] = 0
      
      # Get the uiid of the exercise instance where the user first obtained proficiency
      exer_uiids[uel.exercise.name] = uel.count_attempts
    
    exer_count[uel.exercise.name] += 1
    
  # Load a single user's slideshow event data (limited to the exercises and uiids found above)
  ss_events = UserButton.objects.filter(user=student, name__in=['jsav-forward', 'jsav-backward', 'jsav-begin', 'jsav-end'], exercise__name__in=exer_uiids.keys(), uiid__in=exer_uiids.values()).order_by('action_time')
  
  for exer_name, uiid in exer_uiids.items():
    # Get the descriptions of events from a specific exercise instance
    descriptions = ss_events.filter(exercise__name=exer_name, uiid=uiid).values_list('description', flat=True)
    
    print descriptions
    
    if len(descriptions) > 0:
      # Parse the total number of slides from the description
      num_slides = descriptions[0].split(' / ')[1]
      
      # Ensure every slide was viewed
      for i in range(1, int(num_slides) + 1):
        if str(i) + ' / ' + num_slides not in descriptions:
          cheated_exer_names.append(exer_name)
          print 'CHEAT'
          break
    
    print '\n\n'
  
  return render_to_response("developer_view/slideshow_cheating.html", {'exer_count': exer_count, 'exer_uiids': exer_uiids, 'cheated_exer_names': cheated_exer_names})



@staff_member_required
def total_module_time(request):
  events = ['document-ready', 'window-unload', 'window-blur', 'window-focus']
  
  user_data = OrderedDict()
  
  modules = []
  
  # Loop through all students
  for ud in UserData.objects.filter(book__in=[5, 6]):
    user_buttons = UserButton.objects.filter(user=ud.user, name__in=events).order_by('action_time')
    
    uid = ud.user.id
    
    user_data[uid] = {}
    
    for i in range(0, len(user_buttons)):
      if user_buttons[i].name == 'document-ready':
        mod_name = user_buttons[i].module.name
        
        if mod_name not in modules:
          modules.append(mod_name)
      
        # Initialize the module time
        if mod_name not in user_data[uid]:
          user_data[uid][mod_name] = 0
        
        last_event_time = user_buttons[i].action_time
        
        # Look ahead for a matching 'window-unload' event, subtracting time when the module doesn't have focus
        for j in range(i, len(user_buttons)):
          if user_buttons[j].module.name == mod_name:
            if user_buttons[j].name in ['window-blur', 'window-unload']:
              # Calculate the difference (in seconds) between the time of this event and the previous one
              user_data[uid][mod_name] += time.mktime(user_buttons[j].action_time.timetuple()) - time.mktime(last_event_time.timetuple())
              
              # Break out of the look-ahead loop when a matching 'window-unload' event has been found
              if user_buttons[j].name == 'window-unload':
                break
            elif user_buttons[j].name == 'window-focus':
              last_event_time = user_buttons[j].action_time
  
  return render_to_response("developer_view/total_module_time.html", {'modules': modules, 'user_data': user_data})

    
    
    
    
        
      
  

  # Loop through all users, for each user get UserButton objects document-ready and window-unload, for a document-ready object look ahead until a matching window-unload object is found
  user_buttons = UserButton.objects.filter()
  



#class of detailed exercise steps
class exercise_step:
    def __init__(self, step_num, time, click_num, is_backward):
        
        self.step_num = step_num
        self.click_num = click_num
        self.time = time
        self.is_backward = is_backward
        
    def set_max_time(self, max_time):
        self.max_time = max_time
        
    def set_max_click(self, max_click):
        self.max_click = max_click
        
    def get_time_print(self):
        return float(self.time)/float(self.max_time)*500.0
    
    def get_click_num_print(self):
        return float(self.click_num)/float(self.max_click)*500.0


@staff_member_required    
def exercise_detail(request, student, exercise):
    #The activities of a user and an exercise
    userButtons = UserButton.objects.filter(user=student).filter(exercise=exercise)
    #filter(module=module).
    max_time = 0
    max_click = 0

    exe_steps = []
    current_time = 0
    current_step = 0
    lines = []
    line = []

    #only jsav-forward and jsav-backward actions are handled
    for userButton in userButtons:
        flag = 0

        if userButton.name == 'jsav-forward' and not userButton.description == 'description':
            step = int(userButton.description[:userButton.description.find('/')])

            if current_time == 0 or userButton.action_time < current_time or not step - current_step == 1:
                current_time = userButton.action_time
                current_step = step
                if line:
                    if not len(line) == 1:
                        lines.append(line)
                    line = []
                line.append(current_step)
                continue

            for exe_step in exe_steps:
                if exe_step.step_num == step:
                    exe_step.time = exe_step.time + int((userButton.action_time - current_time).total_seconds())
                    exe_step.click_num = exe_step.click_num + 1
                    flag = 1
                    current_time = userButton.action_time
                    current_step = step
                    line.append(current_step)
                    if max_time < exe_step.time:
                        max_time = exe_step.time
                    if max_click < exe_step.click_num:
                        max_click = exe_step.click_num
                    break
                
            if flag == 0:
                time_diff = int((userButton.action_time - current_time).total_seconds())
                exe_steps.append(exercise_step(step, time_diff, 1, 'false'))
                if max_time < time_diff:
                     max_time = time_diff           
                if max_click < 1:
                    max_click = 1
                current_time = userButton.action_time
                current_step = step
                line.append(current_step)
                
        if userButton.name == 'jsav-backward' and not userButton.description == 'description':
            step = int(userButton.description[:userButton.description.find('/')])

            if current_time == 0 or userButton.action_time < current_time or not step - current_step == -1:
                current_time = userButton.action_time
                current_step = step
                if line:
                    if not len(line) == 1:
                        lines.append(line)
                    line = []
                line.append(current_step)
                continue            
            
            for exe_step in exe_steps:
                if exe_step.step_num == step:
                    exe_step.time = exe_step.time + int((userButton.action_time - current_time).total_seconds())
                    exe_step.click_num = exe_step.click_num + 1
                    if max_time < exe_step.time:
                        max_time = exe_step.time          
                    if max_click < exe_step.click_num:
                        max_click = exe_step.click_num
                    exe_step.is_backward = 'true'
                    flag = 1
                    current_time = userButton.action_time
                    current_step = step
                    line.append(current_step)
                    break
                
            if flag == 0:
                time_diff = int((userButton.action_time - current_time).total_seconds())                
                exe_steps.append(exercise_step(step, time_diff, 1, 'true'))  
                if max_time < time_diff:
                     max_time = time_diff
                     
                if max_click < 1:
                    max_click = 1
                    
                current_time = userButton.action_time
                current_step = step
                line.append(current_step)
                
    if line and not len(line) == 1:
        lines.append(line)
        
    for exe_step in exe_steps:
        exe_step.set_max_time(max_time)
        exe_step.set_max_click(max_click)
    #number = len(exe_steps)
    
    exe_steps = sorted(exe_steps, key=lambda exercise_step:exercise_step.step_num)
                  
    #print(max)
    
    userExercises = UserExercise.objects.filter(user=student).filter(exercise=exercise)
    
    review_dates = []
    
    if len(userExercises) == 1 and userExercises[0].is_proficient():
        
        proficient_date = userExercises[0].proficient_date
        
        exercise = userExercises[0].exercise
    
        userButtons = UserButton.objects.filter(action_time__gt = proficient_date).filter(user=student).filter(exercise=exercise)
        
        #print(userButtons)
        
        for userButton in userButtons:
            if proficient_date.date() < userButton.action_time.date():
                #print(userButton.user_id)
                review_dates.append(userButton.action_time.date())
                
        proficient_date = proficient_date.date()
        
    else:
        proficient_date = 'not_proficient'
        exercise = ''
    
    review_dates = list(set(review_dates))
    
    #print(proficificent_date)
    
    return render_to_response("developer_view/exercise_detail.html", {'exe_steps': exe_steps, 'proficient_date': proficient_date, 'review_dates':review_dates, 'lines': lines, 'exercise':exercise })

#The class to keep document ready event
class docready_event():
    def __init__(self, year, month, day, module):
        self.year = year
        self.month = month
        self.day = day
        self.module = module
        
    def equals(self, year, month, day, module):
        if self.year == year and self.month == month and self.day == day and self.module == module:
            return 1;
        return 0;

#The first time line model
@staff_member_required
def timeline_sum(request, student):
    #This query fetches the document ready activities of a user
    userButtons = UserButton.objects.filter(user=student).filter(name='document-ready')
    
    events = []

    for userButton in userButtons:
        flag = 0
        for event in events:
            if event.equals(userButton.action_time.year, userButton.action_time.month, userButton.action_time.day, userButton.module) == 1:
                flag = 1
                break
        
        if flag == 0:
            events.append(docready_event(userButton.action_time.year, userButton.action_time.month, userButton.action_time.day, userButton.module))

    #events = list(set(events))
    for event in events:
        print(event.month)

    return render_to_response("developer_view/timeline_sum.html", {'events': events, 'student':student})

#the event class to keep for the timeline detail view
class general_event():
    def __init__(self, year, month, day, hour, minute, second, exercise, description):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.exercise = exercise
        self.description = description
        

#time line detail model
@staff_member_required
def timeline_detail(request, student, module, year, month, day):
    
    #This query fetches the activities of a user, a model, an action date except the document ready actions
    userButtons = UserButton.objects.filter(user=student).filter(module__name=module).filter(action_time__year=year).filter(action_time__month=month).filter(action_time__day=day).exclude(name='document-ready')

    events = []

    for userButton in userButtons:
        events.append(general_event(userButton.action_time.year, userButton.action_time.month, userButton.action_time.day, userButton.action_time.hour, userButton.action_time.minute, userButton.action_time.second, userButton.exercise, userButton.description))

    return render_to_response("developer_view/timeline_detail.html", {'events':events})
