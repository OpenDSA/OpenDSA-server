# Python
import datetime

# Django
from django.db import models
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db import transaction
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User


import consts
from decorators import clamp 

# Create your models here.




class Exercise(models.Model):

    name = models.CharField(max_length=50)
    description = models.TextField() 
    covers = models.TextField()
    author = models.CharField(max_length=50)
    ex_type = models.CharField(max_length=50)
    description = models.TextField()
    streak = models.IntegerField()



class Module(models.Model):

     short_display_name = models.CharField(max_length=50)  #name
     name = models.TextField()  #decription 
     covers = models.TextField() 
     author = models.CharField(max_length=50)  
     creation_date = models.DateTimeField(default="2012-01-01 00:00:00") 
     h_position = models.IntegerField(default = 0)
     v_position = models.IntegerField(default = 0) 
     last_modified = models.DateTimeField(default="2012-01-01 00:00:00") 
     prerequisites = models.TextField() 
     raw_html = models.TextField()   
     exercise_list = models.TextField() 


class UserButton(models.Model):
     user = models.ForeignKey(User) 
     exercise = models.ForeignKey(Exercise)
     module =  models.ForeignKey(Module)
     name = models.CharField(max_length=50)
     description = models.TextField() 
     action_time = models.DateTimeField(default="2000-01-01 00:00:00")
     ip_address = models.CharField(max_length=20)



class UserModule(models.Model):

    user = models.ForeignKey(User)
    module =  models.ForeignKey(Module) #models.CharField(max_length=60)
    first_done = models.DateTimeField(auto_now_add=True)
    last_done = models.DateTimeField(auto_now_add=True)
    proficient_date = models.DateTimeField(default="2012-01-01 00:00:00") 

class Feedback(models.Model):  
     
    name = models.CharField(max_length=100) 
    email = models.CharField(max_length=50) 
    subject = models.CharField(max_length=75)
    message = models.TextField()  

class UserData(models.Model):
    # Canonical reference to the user entity. Avoid referencing this directly
    # as the fields of this property can change; only the ID is stable and
    # user_id can be used as a unique identifier instead.
    user =   models.ForeignKey(User)

    # Names of exercises in which the user is *explicitly* proficient
    proficient_exercises = models.TextField()  #object_property.StringListCompatTsvField()

    # Names of all exercises in which the user is proficient
    all_proficient_exercises = models.TextField() # object_property.StringListCompatTsvField()

    points = models.IntegerField(default=0)

    #completed = models.IntegerField(default=-1)
    #last_daily_summary = models.DateTimeField()
    #last_badge_review = models.DateTimeField()
    #last_activity = models.DateTimeField()
    #start_consecutive_activity_date = models.DateTimeField()
    #count_feedback_notification = models.IntegerField(default=-1)
    #question_sort_order = models.IntegerField(default=-1)
    #uservideocss_version = models.IntegerField(default=0)
    #has_current_goals = models.BooleanField(default=False)



    def is_proficient_at(self, exid):
        if self.all_proficient_exercises is None:
            return False
        prof_ex =[]
        for ex in self.all_proficient_exercises.split(','):
            if ex.isdigit():
              number = int(ex)
              prof_ex.append(int(ex))
        return (exid.id in prof_ex)



    def add_points(self, points):
        if self.points is None:
            self.points = 0

        if not hasattr(self, "_original_points"):
            self._original_points = self.points

        # Check if we crossed an interval of 2500 points
        if self.points % 2500 > (self.points + points) % 2500:
            util_notify.update(self, user_exercise=None, threshold=True)
        self.points += points

    def original_points(self):
        return getattr(self, "_original_points", 0)



class UserExerciseLog(models.Model):

    user =  models.ForeignKey(UserData)
    exercise =  models.ForeignKey(Exercise)
    correct = models.BooleanField(default = False)
    time_done = models.DateTimeField(auto_now_add=True)
    time_taken = models.IntegerField(default = 0)
    count_hints = models.IntegerField(default = 0)
    hint_used = models.BooleanField(default = False)
    points_earned = models.IntegerField(default = 0)
    earned_proficiency = models.BooleanField(default = False) # True if proficiency was earned on this problem
    count_attempts = models.IntegerField(default = 0)
    ip_address = models.CharField(max_length=20)


    def put(self):
#        if self.random_float is None:
#            self.random_float = random.random()
        models.Model.put(self)

    def time_taken_capped_for_reporting(self):
        # For reporting's sake, we cap the amount of time that you can be considered to be
        # working on a single problem at 60 minutes. If you've left your browser open
        # longer, you're probably not actively working on the problem.
        return min(consts.MAX_WORKING_ON_PROBLEM_SECONDS, self.time_taken)

    def time_started(self):
        return self.time_done - datetime.timedelta(seconds = self.time_taken_capped_for_reporting())

    def time_ended(self):
        return self.time_done

    def minutes_spent(self):
        return util.minutes_between(self.time_started(), self.time_ended())

    # commit_problem_log is used by our deferred problem log insertion process
    def commit_problem_log(problem_log_source, user_data = None):
        try:
            if not problem_log_source or not problem_log_source.key().name:
                logging.critical("Skipping problem log commit due to missing problem_log_source or key().name")
                return
        except models.NotSavedError:
            # Handle special case during new exercise deploy
            logging.critical("Skipping problem log commit due to models.NotSavedError")
            return

        if problem_log_source.count_attempts > 1000:
            logging.info("Ignoring attempt to write problem log w/ attempts over 1000.")
            return
    # Committing transaction combines existing problem log with any followup attempts
    def txn():
        problem_log = UserExerciseLog.get_by_key_name(problem_log_source.key().name())

        if not problem_log:
            problem_log = UserExerciseLog(
                #key_name = problem_log_source.key().name(),
                user = problem_log_source.user,
                exercise = problem_log_source.exercise,
                correct = problem_log_source.correct,
                time_done = problem_log_source.time_done,
                #count_hints = problem_log_source.count_hints,
                ip_address = problem_log_source.ip_address,
        )

        problem_log.count_hints = max(problem_log.count_hints, problem_log_source.count_hints)
        problem_log.hint_used = problem_log.count_hints > 0
        index_attempt = max(0, problem_log_source.count_attempts - 1)

        # Bump up attempt count
        if problem_log_source.attempts[0] != "hint": # attempt
            if index_attempt < len(problem_log.time_taken_attempts) \
               and problem_log.time_taken_attempts[index_attempt] != -1:
                # This attempt has already been logged. Ignore this dupe taskqueue execution.
                logging.info("Skipping problem log commit due to dupe taskqueue\
                    execution for attempt: %s, key.name: %s" % \
                    (index_attempt, problem_log_source.key().name()))
                return

            problem_log.count_attempts += 1
            # Add time_taken for this individual attempt
            problem_log.time_taken += problem_log_source.time_taken
            #insert_in_position(index_attempt, problem_log.time_taken_attempts, problem_log_source.time_taken, filler=-1)
            # Add actual attempt content
            #insert_in_position(index_attempt, problem_log.attempts, problem_log_source.attempts[0], filler="")

            # Proficiency earned should never change per problem
            problem_log.earned_proficiency = problem_log.earned_proficiency or \
                problem_log_source.earned_proficiency

        else: # hint
            index_hint = max(0, problem_log_source.count_hints - 1)

            if index_hint < len(problem_log.hint_time_taken_list) \
               and problem_log.hint_time_taken_list[index_hint] != -1:
                # This attempt has already been logged. Ignore this dupe taskqueue execution.
                return

            # Add time taken for hint
            #insert_in_position(index_hint, problem_log.hint_time_taken_list, problem_log_source.time_taken, filler=-1)

            # Add attempt number this hint follows
            #insert_in_position(index_hint, problem_log.hint_after_attempt_list, problem_log_source.count_attempts, filler=-1)

        # Points should only be earned once per problem, regardless of attempt count
        problem_log.points_earned = max(problem_log.points_earned, problem_log_source.points_earned)
        # Correct cannot be changed from False to True after first attempt
        problem_log.correct = (problem_log_source.count_attempts == 1 or problem_log.correct) and problem_log_source.correct and not problem_log.count_hints

        logging.info(problem_log.time_ended())
        problem_log.put()


class UserProfExerciseLog(models.Model):

    problem_log =  models.ForeignKey(UserExerciseLog)
    student =  models.IntegerField(default = 0)
    correct =  models.IntegerField(default = 0)
    fix =  models.IntegerField(default = 0) 
    undo =  models.IntegerField(default = 0) 
    total =  models.IntegerField(default = 0) 


class UserExercise(models.Model):

    user = models.ForeignKey(User)
    exercise =  models.ForeignKey(Exercise) #models.CharField(max_length=60)
    streak = models.IntegerField(default = 0)
    longest_streak = models.IntegerField(default = 0)
    first_done = models.DateTimeField(auto_now_add=True)
    last_done = models.DateTimeField(auto_now_add=True)
    total_done = models.IntegerField(default = 0)
    total_correct = models.IntegerField(default = 0)
    proficient_date = models.DateTimeField(default="2012-01-01 00:00:00")

    def update_proficiency_ka(self, correct):
        exercise = Exercise.objects.get(pk=self.exercise_id)
        user_data = UserData.objects.get(user=self.user)
        dt_now = datetime.datetime.now() 
        if correct and (self.longest_streak >= exercise.streak):
           self.proficient_date = dt_now
           
           user_data.proficient_exercises += "%s," %self.exercise_id
           user_data.all_proficient_exercises += "%s," %self.exercise_id 
           user_data.save() 
           return True
        return False 

    def update_proficiency_pe(self, correct):
        exercise = Exercise.objects.get(pk=self.exercise_id)
        user_data = UserData.objects.get(user=self.user)
        dt_now = datetime.datetime.now()
        if correct:
           self.proficient_date = dt_now

           user_data.proficient_exercises += "%s," %self.exercise_id
           user_data.all_proficient_exercises += "%s," %self.exercise_id
           user_data.save()
           return True
        return False
 
