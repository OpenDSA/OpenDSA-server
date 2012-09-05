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


    @property
    def seconds_since_joined(self):
        return util.seconds_since(self.joined)

    @staticmethod
    #@request_cache.cache_with_key_fxn(lambda user_id: "UserData_user_id:%s" % user_id)
    def get_from_user_id(user_id):
        if not user_id:
            return None

        query = UserData.all()
        query.filter('user_id =', user_id)
        query.order('-points') # Temporary workaround for issue 289
        return query.get()

    @staticmethod
    def get_from_user_input_email(email):
        if not email:
            return None

        query = UserData.all()
        query.filter('user_email =', email)
        query.order('-points') # Temporary workaround for issue 289

        return query.get()

    @staticmethod
    def get_from_username(username):
        if not username:
            return None
        canonical_username = UniqueUsername.get_canonical(username)
        if not canonical_username:
            return None
        query = UserData.all()
        query.filter('username =', canonical_username.username)
        return query.get()

    @staticmethod
    def get_from_models_key_email(email):
        if not email:
            return None

        query = UserData.all()
        query.filter('user =', users.User(email))
        query.order('-points') # Temporary workaround for issue 289

        return query.get()

    @staticmethod
    def get_from_username_or_email(username_or_email):
        if not username_or_email:
            return None

        user_data = None

        if UniqueUsername.is_valid_username(username_or_email):
            user_data = UserData.get_from_username(username_or_email)
        else:
            user_data = UserData.get_possibly_current_user(username_or_email)

        return user_data


    def get_or_insert_exercise(self, exercise, allow_insert = True):
        if not exercise:
            return None

        exid = exercise.name
        userExercise = UserExercise.get_by_key_name(exid, parent=self)

        if not userExercise:
            # There are some old entities lying around that don't have keys.
            # We have to check for them here, but once we have reparented and rekeyed legacy entities,
            # this entire function can just be a call to .get_or_insert()
            query = UserExercise.all(keys_only = True)
            query.filter('user =', self.user)
            query.filter('exercise =', exid)
            query.order('-total_done') # Temporary workaround for issue 289

            # In order to guarantee consistency in the HR datastore, we need to query
            # via models.get for these old, parent-less entities.
            key_user_exercise = query.get()
            if key_user_exercise:
                userExercise = UserExercise.get(str(key_user_exercise))

        if allow_insert and not userExercise:
            userExercise = UserExercise.get_or_insert(
                key_name=exid,
                parent=self,
                user=self.user,
                exercise=exid,
                exercise_model=exercise,
                streak=0,
                _progress=0.0,
                longest_streak=0,
                first_done=datetime.datetime.now(),
                last_done=None,
                total_done=0,
                summative=exercise.summative,
                _accuracy_model=AccuracyModel(),
                )

        return userExercise



    def is_proficient_at(self, exid, exgraph=None):
        if self.all_proficient_exercises is None:
            return False
        return (exid in self.all_proficient_exercises.split(','))

    def is_explicitly_proficient_at(self, exid):
        return (exid in self.proficient_exercises)

    def is_suggested(self, exid):
        self.reassess_if_necessary()
        return (exid in self.suggested_exercises)

    def get_students_data(self):
        coach_email = self.key_email
        query = UserData.all().filter('coaches =', coach_email)
        students_data = [s for s in query.fetch(1000)]

        if coach_email.lower() != coach_email:
            students_set = set([s.key().id_or_name() for s in students_data])
            query = UserData.all().filter('coaches =', coach_email.lower())
            for student_data in query:
                if student_data.key().id_or_name() not in students_set:
                    students_data.append(student_data)
        return students_data

    def record_activity(self, dt_activity):

        # Make sure last_activity and start_consecutive_activity_date have values
        self.last_activity = self.last_activity or dt_activity
        self.start_consecutive_activity_date = self.start_consecutive_activity_date or dt_activity

        if dt_activity > self.last_activity:

            # If it has been over 40 hours since we last saw this user, restart
            # the consecutive activity streak.
            #
            # We allow for a lenient 40 hours in order to offer kinder timezone
            # interpretation.
            #
            # 36 hours wasn't quite enough. A user with activity at 8am on
            # Monday and 8:15pm on Tuesday would not have consecutive days of
            # activity.
            #
            # See http://meta.stackoverflow.com/questions/55483/proposed-consecutive-days-badge-tracking-change
            if util.hours_between(self.last_activity, dt_activity) >= 40:
                self.start_consecutive_activity_date = dt_activity

            self.last_activity = dt_activity

    def current_consecutive_activity_days(self):
        if not self.last_activity or not self.start_consecutive_activity_date:
            return 0
        dt_now = datetime.datetime.now()

        # If it has been over 40 hours since last activity, bail.
        if util.hours_between(self.last_activity, dt_now) >= 40:
            return 0

        return (self.last_activity - self.start_consecutive_activity_date).days

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

    @staticmethod
    def get_for_user_data_between_dts(user_data, dt_a, dt_b):
        query = UserExerciseLog.all()
        query.filter('user =', user_data.user)
        query.filter('time_done >=', dt_a)
        query.filter('time_done <', dt_b)

        query.order('time_done')

        return query
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
