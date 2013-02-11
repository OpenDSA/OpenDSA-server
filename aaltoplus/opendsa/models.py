# Python
import datetime

# Django
from django.db import models
from django.db import connection
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db import transaction
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User

#A+
from course.models import Course, CourseInstance
import consts
#from decorator import clamp 

# Create your models here.




class Exercise(models.Model):

    name = models.CharField(max_length=50)
    description = models.TextField() 
    covers = models.TextField()
    author = models.CharField(max_length=50)
    ex_type = models.CharField(max_length=50)
    description = models.TextField()
    streak = models.IntegerField()


class Books(models.Model):
    book_name = models.CharField(max_length=50)
    book_url =  models.CharField(unique=False, max_length=80, blank=False,
                                               validators=[RegexValidator(regex="^[\w\-\.]*$")],
                                               help_text="Input an URL identifier for this book.") 
    courses = models.ManyToManyField(CourseInstance)


#A table to hold user status (proficient, started, not started) for each exercise.
class UserSummary(models.Model):

   grouping =  models.IntegerField()
   key = models.CharField(max_length=50)
   value = models.CharField(max_length=50)

   @staticmethod
   def GetUserSummaryByIds(userId, exerciseId):
        cur = connection.cursor();
	cur.callproc('GetUserSummaryByIds',[userId,exerciseId, ])
	results = cur.fetchall()
	cur.close()
	return [UserSummary (*row) for row in results]

   @staticmethod
   def GetUserSummaryByExerciseId(exerciseId):
       cur = connection.cursor()
       cur.callproc('GetUserSummaryByExerciseId', [exerciseId, ])
       results = cur.fetchall()
       cur.close()
       return [UserSummary (*row) for row in results]


#A map table between exercise and modules
class ExerciseModule(models.Model):
   exercise = models.CharField(max_length=50)
   module = models.CharField(max_length=50)


#Table summarizing all students module activities
class UserModuleSummary(models.Model): 

    user =  models.CharField(max_length=50)
    module = models.CharField(max_length=60)
    module_status =  models.CharField(max_length=3)
    first_done = models.DateTimeField(default="1800-01-01 00:00:00")
    last_done = models.DateTimeField(default="1800-01-01 00:00:00")
    proficient_date = models.DateTimeField(default="1800-01-01 00:00:00")
    proficient_exe =  models.TextField()
    started_exe =  models.TextField()
    notstarted_exe =  models.TextField()


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

     def add_required_exercise(self, exid):
         if exid not in self.exercise_list.split(','):
             if len(self.exercise_list) == 0:
                 self.exercise_list += '%s' %exid
             else:
                 self.exercise_list += ',%s' %exid

     #function that returns list of id of exercises
     #will be compared to student list of proficiency exercises 
     def get_proficiency_model(self):
         if self.exercise_list != None and len(self.exercise_list)>1: 
            ex_list = self.exercise_list.split(',') 
            ex_id_list = []
            for ex in ex_list:
                if len(Exercise.objects.filter(id = ex))==1:
                    #ex_id = Exercise.objects.get(name=ex)
                    ex_id_list.append(int(ex))
                #else:
                #    ex_id_list.append(0)
            return ex_id_list
         return None

     def get_required_exercises(self):
         if self.exercise_list != None and len(self.exercise_list)>0:
            ex_list = self.exercise_list.split(',')
            ex_id_list = []
            for ex in ex_list:
                if ex.isdigit():
                    if len(Exercise.objects.filter(id= ex))==1:
                        ex_ = Exercise.objects.get(id=ex)
                        ex_id_list.append(ex_)
            return ex_id_list
         return []  


#A table to hold Book, modules , exercises data
class BookModuleExercise (models.Model):
    book = models.ForeignKey(Books)
    module = models.ForeignKey(Module)
    exercise = models.ForeignKey(Exercise) 
    #points the exercise is worth
    points = models.DecimalField(default = 0, max_digits=5, decimal_places=2) 
    class Meta:
        unique_together = (("book","module", "exercise"),)


class UserBook (models.Model):
    user = models.ForeignKey(User)
    book = models.ForeignKey(Books)
    class Meta:
        unique_together = (("user","book"),)



class UserButton(models.Model):
     user = models.ForeignKey(User) 
     exercise = models.ForeignKey(Exercise)
     module =  models.ForeignKey(Module)
     name = models.CharField(max_length=50)
     description = models.TextField() 
     action_time = models.DateTimeField(default="2000-01-01 00:00:00")
     browser_family = models.CharField(max_length=20)
     browser_version = models.CharField(max_length=20)
     os_family = models.CharField(max_length=50)
     os_version = models.CharField(max_length=20)
     device = models.CharField(max_length=50)
     ip_address = models.CharField(max_length=20)



class UserModule(models.Model):

    user = models.ForeignKey(User)
    book = models.ForeignKey(Books)
    module =  models.ForeignKey(Module) #models.CharField(max_length=60)
    first_done = models.DateTimeField(auto_now_add=True)
    last_done = models.DateTimeField(auto_now_add=True)
    proficient_date = models.DateTimeField(default="2012-01-01 00:00:00") 
    
    class Meta:
       unique_together = (("user","book", "module"),)

    @staticmethod
    def GetUserModuleByUserId(userId):
        cur = connection.cursor();
	cur.callproc('GetUserModuleByUser_Id',[userId,])
	results = cur.fetchall()
	cur.close()
	return [UserModule(*row) for row in results]

    def is_proficient_at(self):
        return (self.proficient_date != datetime.datetime.strptime('2012-01-01 00:00:00','%Y-%m-%d %H:%M:%S'))  



class UserData(models.Model):
    # Canonical reference to the user entity. 
    user =   models.ForeignKey(User)

    book = models.ForeignKey(Books) 
    # ids of exercises started
    started_exercises = models.TextField()  

    # ids of all exercises in which the user is proficient
    all_proficient_exercises = models.TextField() 

    points = models.DecimalField(default = 0, max_digits=5, decimal_places=2) 



    def earned_proficiency(self, exid):
        if len(self.all_proficient_exercises)==0:
            self.all_proficient_exercises += '%s' %exid
        else:
            self.all_proficient_exercises += ',%s' %exid  

    def started(self, exid):
        if len(self.started_exercises) ==0:
            self.started_exercises += '%s' %exid
        else:
            self.started_exercises += ',%s' %exid

    def is_proficient_at(self, exid):
        if self.all_proficient_exercises is None or len(self.all_proficient_exercises)==0:
            return False
        prof_ex =[]
        for ex in self.all_proficient_exercises.split(','):
            if ex.isdigit():
              number = int(ex)
              prof_ex.append(int(ex))
        return (exid.id in prof_ex)

    def has_started(self, exid):
        if self.started_exercises is None or len(self.started_exercises)==0:
            return False
        started_ex =[]
        for ex in self.started_exercises.split(','):
            if ex.isdigit():
              number = int(ex)
              started_ex.append(int(ex))
        return (exid.id in started_ex)


    def get_prof_list(self):
        prof_ex =[] 
        for ex in self.all_proficient_exercises.split(','):
            if ex.isdigit():
              number = int(ex)
              prof_ex.append(int(ex))
        return prof_ex

 
    def add_points(self, points):
        self.points += points




class UserExerciseLog(models.Model):

    user =  models.ForeignKey(User)
    exercise =  models.ForeignKey(Exercise)
    correct = models.BooleanField(default = False)
    time_done = models.DateTimeField(auto_now_add=True)
    time_taken = models.IntegerField(default = 0)
    count_hints = models.IntegerField(default = 0)
    hint_used = models.BooleanField(default = False)
    points_earned = models.DecimalField(default = 0, max_digits=5, decimal_places=2)  
    earned_proficiency = models.BooleanField(default = False) # True if proficiency was earned on this problem
    count_attempts = models.IntegerField(default = 0)
    ip_address = models.CharField(max_length=20)


    def put(self):
        models.Model.put(self)




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
    progress = models.DecimalField(default = 0, max_digits=5, decimal_places=2) 
    class Meta:
       unique_together = (("user", "exercise"),)

    def update_proficiency_ka(self, correct, ubook):
        exercise = Exercise.objects.get(pk=self.exercise_id)
        user_data = UserData.objects.get(user=self.user,book=ubook)
        dt_now = datetime.datetime.now() 
        if correct and (self.longest_streak >= exercise.streak):
           self.proficient_date = dt_now
           
           user_data.save() 
           return True
        return False 
     
    
    def update_proficiency_pe(self, correct,ubook):
        exercise = Exercise.objects.get(pk=self.exercise_id)
        user_data = UserData.objects.get(user=self.user,book=ubook)
        dt_now = datetime.datetime.now()
        if correct:
           self.proficient_date = dt_now

           if len(user_data.all_proficient_exercises)==0:
               user_data.all_proficient_exercises += "%s" %self.exercise_id 
           else:
               user_data.all_proficient_exercises += ",%s" %self.exercise_id
           user_data.save()
           return True
        return False
   
    def is_proficient(self):
        return (self.proficient_date != datetime.datetime.strptime('2012-01-01 00:00:00','%Y-%m-%d %H:%M:%S'))
  
