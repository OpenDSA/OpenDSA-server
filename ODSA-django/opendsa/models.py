# Python
import datetime
from decimal import Decimal

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
from exercise.exercise_models import  CourseModule
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
    streak = models.DecimalField(default = 0, max_digits=5, decimal_places=2)

    def __unicode__(self):
       '''
       Returns a short representation of the book as an unicode string.
       '''
       return '%s:%s' %(self.id,self.name)

class Books(models.Model):
    book_name = models.CharField(max_length=50)
    book_url =  models.CharField(unique=False, max_length=80, blank=False,
                                               validators=[RegexValidator(regex="^[\w\-\.]*$")],
                                               help_text="Input an URL identifier for this book.")
    courses = models.ManyToManyField(CourseInstance)
    creation_date = models.DateTimeField()

    def __unicode__(self):
       '''
       Returns a short representation of the book as an unicode string.
       '''
       return self.book_url


class Assignments(models.Model):

    course_module = models.ForeignKey(CourseModule, unique=True)
    assignment_book = models.ForeignKey(Books)
    #list of exercises in the assignment
    assignment_exercises = models.CommaSeparatedIntegerField(
        'comma separated ints', max_length=255, blank=True,
        default=''
    )

    def add_exercise(self, exid):
        if len(self.assignment_exercises)==0:
            self.assignment_exercises += '%s' %exid
        else:
            self.assignment_exercises += ',%s' %exid
    def get_exercises_id(self):
        _ex =[]
        for ex in self.assignment_exercises.split(','):
            if ex.isdigit():
              _ex.append(int(ex))
        return _ex
    def get_exercises(self):
        _ex =[]
        for ex in self.assignment_exercises.split(','):
            if ex.isdigit():
              exer = Exercise.objects.get(id=ex)
              _ex.append(exer)
        return _ex



#A table to hold user status (proficient, started, not started) for each exercise.
#class UserSummary(models.Model):

#   grouping =  models.IntegerField()
#   key = models.CharField(max_length=50)
#   value = models.CharField(max_length=50)

#   @staticmethod
#   def GetUserSummaryByIds(userId, exerciseId):
#        cur = connection.cursor();
#        cur.callproc('GetUserSummaryByIds',[userId,exerciseId, ])
#        results = cur.fetchall()
#        cur.close()
#        return [UserSummary (*row) for row in results]

#   @staticmethod
#   def GetUserSummaryByExerciseId(exerciseId):
#       cur = connection.cursor()
#       cur.callproc('GetUserSummaryByExerciseId', [exerciseId, ])
#       results = cur.fetchall()
#       cur.close()
#       return [UserSummary (*row) for row in results]


#A map table between exercise and modules
#class ExerciseModule(models.Model):
#   exercise = models.CharField(max_length=50)
#   module = models.CharField(max_length=50)
#

#Table summarizing all students module activities
#class UserModuleSummary(models.Model):
#    user =  models.CharField(max_length=50)
#    module = models.CharField(max_length=60)
#    module_status =  models.CharField(max_length=3)
#    first_done = models.DateTimeField(default="1800-01-01 00:00:00")
#    last_done = models.DateTimeField(default="1800-01-01 00:00:00")
#    proficient_date = models.DateTimeField(default="1800-01-01 00:00:00")
#    proficient_exe =  models.TextField()
#    started_exe =  models.TextField()
#    notstarted_exe =  models.TextField()


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

     #function that returns list of id of exercises we get it from BookModuleExercise table
     #will be compared to student list of proficiency exercises
     def get_proficiency_model(self, book):
         mod_exe_data = BookModuleExercise.components.filter(book=book,module=self)
         if not mod_exe_data:
             return None
         else:
             ex_id_list = []
             for bme in  mod_exe_data:
                 ex_id_list.append(int(bme.exercise.id))
             return ex_id_list

#manager to get book's modules and exercise
class ModuleExerciseManager(models.Manager):
    def get_query_set(self):
        return super(ModuleExerciseManager,self).get_query_set()

    def get_book_list(self):
        book_list =[]
        for bme in super(ModuleExerciseManager,self).get_query_set():
            if bme not in book_list:
                book_list.append(bme.book)
        return book_list

    def get_module_list(self, book):
        module_list =[]
        for bme in super(ModuleExerciseManager,self).get_query_set().filter(book=book):
            module_list.append(bme.module)
        return module_list

    def get_exercise_list(self, book):
        exercise_list =[]
        for bme in super(ModuleExerciseManager,self).get_query_set().filter(book=book):
            exercise_list.append(bme.exercise)
        return exercise_list 

    def get_mod_exercise_list(self, book, mod):
        exercise_list =[]
        for bme in super(ModuleExerciseManager,self).get_query_set().filter(book=book,module=mod):
            if bme.points > Decimal(0):
                exercise_list.append(bme.exercise)
        return exercise_list


#A table to hold Book, modules , exercises data
class BookModuleExercise (models.Model):
    book = models.ForeignKey(Books)
    module = models.ForeignKey(Module)
    exercise = models.ForeignKey(Exercise)
    #points the exercise is worth
    points = models.DecimalField(default = 0, max_digits=5, decimal_places=2)
    #reference to manager 
    components = ModuleExerciseManager()
    class Meta:
        unique_together = (("book","module", "exercise"),)
    def __unicode__(self):
       '''
       Returns a short representation of the book as an unicode string.
       '''
       return self.book.book_url


class BookChapter (models.Model):
    book = models.ForeignKey(Books)
    name = models.CharField(max_length=100)
    module_list = models.TextField()
    class Meta:
        unique_together = (("book","name"),)
    def __unicode__(self):
       '''
       Returns a short representation of the book as an unicode string.
       '''
       return self.name


    def add_module(self, exid):
       if len(self.module_list)==0:
           self.module_list += '%s' %exid
       else:
           self.module_list += ',%s' %exid
    def get_modules_id(self):
       _mod =[]
       for mod in self.module_list.split(','):
           if mod.isdigit():
             _mod.append(int(mod))
       return _mod
    def get_modules(self):
       _mod =[]
       for mod in self.module_list.split(','):
           if mod.isdigit():
             cmod = Module.objects.get(id=mod)
             _mod.append(cmod)
       return _mod

class UserBook (models.Model):
    user = models.ForeignKey(User)
    book = models.ForeignKey(Books)
    grade = models.BooleanField(default = True) 
    class Meta:
        unique_together = (("user","book"),)



class UserButton(models.Model):
     user = models.ForeignKey(User)
     book = models.ForeignKey(Books)
     exercise = models.ForeignKey(Exercise)
     module =  models.ForeignKey(Module)
     name = models.CharField(max_length=50)
     description = models.TextField()
     action_time = models.DateTimeField(default="2000-01-01 00:00:00")
     uiid = models.BigIntegerField(default = 0)
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

    class Meta:
       unique_together = (("user", "book"),)


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
        for ex in self.all_proficient_exercises.split(','):
            if ex.isdigit() and int(ex) == exid.id:
                return True  
        return False

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
              prof_ex.append(int(ex))
        return prof_ex


    def get_started_list(self):
        start_ex =[]
        for ex in self.started_exercises.split(','):
            if ex.isdigit():
              start_ex.append(int(ex))
        return start_ex





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
    count_attempts = models.BigIntegerField(default = 0)
    ip_address = models.CharField(max_length=20)
    ex_question = models.CharField(max_length=50)

    def put(self):
        models.Model.put(self)



class UserProgLog(models.Model):
    problem_log =  models.ForeignKey(UserExerciseLog)
    student_code = models.TextField()
    feedback = models.TextField() 


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

