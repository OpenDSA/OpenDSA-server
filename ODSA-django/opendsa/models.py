"""
OpenDSA database model 
"""

# Python
import datetime
from decimal import Decimal

# Django
from django.db import models
from django.db import connection
from django.db.models.signals import post_save, m2m_changed
#from django.core.validators import RegexValidator
from django.contrib.auth.models import User

#A+
from course.models import CourseInstance
from exercise.exercise_models import  CourseModule
#from decorator import clamp

# Create your models here.




class Exercise(models.Model):
    """
    Exercise table
    """
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
        return '%s:%s' % (self.id, self.name)

class Books(models.Model):
    """
    Books table
    """
    book_name = models.CharField(max_length=50)
    book_url =  models.CharField(max_length=80) 
                   #(unique=False, max_length=80, blank=False,
                   #validators=[RegexValidator(regex="^[\w\-\.]*$")],
                   #help_text="Input an URL identifier for this book.")
    courses = models.ManyToManyField(CourseInstance)
    creation_date = models.DateTimeField()

    def __unicode__(self):
        '''
        Returns a short representation of the book as an unicode string.
        '''
        return self.book_url

    def isType(self):
        """
        Returns the type of the model object
        """
        return "books"


def create_course_module(sender, instance, action, pk_set, **kwargs):
    '''
    This function automatically creates a course module when a book is associated to a course .

    @param sender: the signal(?) that invoked the function
    @param instance: the User object that was just created
    '''
    if action == "post_add":
        name_ = "Assignment_%s" % datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        c_i = 0 
        for ci in pk_set:
            c_i = ci
        course_i = CourseInstance.objects.get(id = c_i)
        CourseModule.objects.create(name=name_, course_instance=course_i)

m2m_changed.connect(create_course_module, sender=Books.courses.through)




class Assignments(models.Model):
    """
    Assignment table
    """

    course_module = models.ForeignKey(CourseModule, unique=True)
    assignment_book = models.ForeignKey(Books)
    #list of exercises in the assignment
    assignment_exercises = models.CommaSeparatedIntegerField(
        'comma separated ints', max_length=255, blank=True,
        default=''
    )

    def add_exercise(self, exid):
        """
        Adds exercise to the assignment 
        """
        if len(self.assignment_exercises)==0:
            self.assignment_exercises += '%s' % exid
        else:
            self.assignment_exercises += ',%s' % exid
    def get_exercises_id(self):
        """
        returns a list of ids of the exercises in the assignment 
        """
        _ex = []
        for ex in self.assignment_exercises.split(','):
            if ex.isdigit():
                _ex.append(int(ex))
        return _ex
    def get_exercises(self):
        """
        returns a list of exercises objects in the assignment 
        """
        _ex = []
        for ex in self.assignment_exercises.split(','):
            if ex.isdigit():
                if Exercise.objects.filter(id=ex).count() > 0: 
                    exer = Exercise.objects.get(id=ex)
                    _ex.append(exer)
        return _ex
    def isType(self):
        """
        returns the type of the model object 
        """
        return "assignments"




class Module(models.Model):
    """
    Module table 
    """
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

    def get_proficiency_model(self, book):
        """
        function that returns list of id of exercises 
        we get it from BookModuleExercise table
        will be compared to student list of proficiency exercises
        """
        mod_exe_data = BookModuleExercise.components.filter( \
                                                      book = book, \
                                                      module = self)
        if not mod_exe_data:
            return None
        else:
            ex_id_list = []
            for bme in  mod_exe_data:
                ex_id_list.append(int(bme.exercise.id))
            return ex_id_list

class ModuleExerciseManager(models.Manager):
    """
    Manager class for the BookModuleExercise model
    it is used to get book's modules and exercise
    """
    def get_query_set(self):
        """
        constructs the manager queryset
        """
        return super(ModuleExerciseManager, self).get_query_set()

    def get_book_list(self):
        """
        Returns a list of all the books in teh table
        """
        book_list = []
        for bme in super(ModuleExerciseManager, self).get_query_set():
            if bme not in book_list:
                book_list.append(bme.book)
        return book_list

    def get_module_list(self, book):
        """
        Returns a list of all the modules in a specific book
        """
        module_list = []
        for bme in super(ModuleExerciseManager, self).get_query_set().filter( \
                                                                 book = book):
            module_list.append(bme.module)
        return module_list

    def get_exercise_list(self, book):
        """
        Returns a list of all the exercises in a specific book
        """
        exercise_list = []
        for bme in super(ModuleExerciseManager, \
                         self).get_query_set().filter(book = book):
            exercise_list.append(bme.exercise)
        return exercise_list 

    def get_mod_exercise_list(self, book, mod):
        """
        Returns a list of all the exercises in a specific book and module
        We return only required exercises
        """
        exercise_list = []
        for bme in super(ModuleExerciseManager, self).get_query_set().filter( \
                                                     book = book, \
                                                     module = mod):
            if bme.points > Decimal(0):
                exercise_list.append(bme.exercise)
        return exercise_list


class BookModuleExercise (models.Model):
    """
    A table to hold Book, modules , exercises data
    """
    book = models.ForeignKey(Books)
    module = models.ForeignKey(Module)
    exercise = models.ForeignKey(Exercise)
    #points the exercise is worth
    points = models.DecimalField(default = 0, max_digits=5, decimal_places=2)
    #reference to manager 
    components = ModuleExerciseManager()
    class Meta:
        unique_together = (("book", "module", "exercise"),)
    def __unicode__(self):
        '''
        Returns a short representation of the book as an unicode string.
        '''
        return self.book.book_url


class BookChapter (models.Model):
    """
    A table to store all the chapters  in a book
    """
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
        """
        Adds a module to a chapter
        """
        if len(self.module_list)==0:
            self.module_list += '%s' % exid
        else:
            if exid not in self.module_list.split(','):
                self.module_list += ',%s' % exid
    def get_modules_id(self):
        """
        Returns a list of the ids of all the modules in a chapter
        """
        _mod = []
        for mod in self.module_list.split(','):
            if mod.isdigit():
                _mod.append(int(mod))
        return _mod
    def get_modules(self):
        """
        Returns a list of modules objects in a chapter
        """
        _mod = []
        for mod in self.module_list.split(','):
            if mod.isdigit():
                cmod = Module.objects.get(id=mod)
                _mod.append(cmod)
        return _mod

class UserBook (models.Model):
    """
    A table to record  the  student use of  a book
    """
    user = models.ForeignKey(User)
    book = models.ForeignKey(Books)
    grade = models.BooleanField(default = True) 
    class Meta:
        unique_together = (("user","book"),)



class UserButton(models.Model):
    """
    Table recording all books interactions data
    """
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
    """
    Table recording a summary of a student activity on a module
    """
    user = models.ForeignKey(User)
    book = models.ForeignKey(Books)
    module =  models.ForeignKey(Module) #models.CharField(max_length=60)
    first_done = models.DateTimeField(auto_now_add=True)
    last_done = models.DateTimeField(auto_now_add=True)
    proficient_date = models.DateTimeField(default="2012-01-01 00:00:00")

    class Meta:
        unique_together = (("user", "book", "module"),)

    @staticmethod
    def GetUserModuleByUserId(userId):
        """
        returns all module activity for a specific student
        """
        cur = connection.cursor()
        cur.callproc('GetUserModuleByUser_Id', [userId,])
        results = cur.fetchall()
        cur.close()
        return [UserModule(*row) for row in results]

    def is_proficient_at(self):
        """
        Returns if the student earned module proficiency or not 
        """
        return (self.proficient_date != datetime.datetime.strptime( \
                                '2012-01-01 00:00:00','%Y-%m-%d %H:%M:%S'))



class UserData(models.Model):
    """
    A table storing a summary of user/exercises activity:
    started exercises and proficient exercises 
    """
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
        """
        Adds an exercise to the list of proficient exercises
        """
        if len(self.all_proficient_exercises) == 0:
            self.all_proficient_exercises += '%s' % exid
        else:
            self.all_proficient_exercises += ',%s' % exid

    def started(self, exid):
        """
        Adds an exercise to the list of started exercises
        """
        if len(self.started_exercises) == 0:
            self.started_exercises += '%s' % exid
        else:
            self.started_exercises += ',%s' % exid

    def is_proficient_at(self, exid):
        """
        returns if the student earned proficiency on a specific exercise
        """ 
        if self.all_proficient_exercises is None or \
           len(self.all_proficient_exercises) == 0:
            return False
        for ex in self.all_proficient_exercises.split(','):
            if ex.isdigit() and int(ex) == exid.id:
                return True  
        return False

    def has_started(self, exid):
        """
        returns if the student has started a specific exercise
        """
        if self.started_exercises is None or len(self.started_exercises) == 0:
            return False
        started_ex = []
        for ex in self.started_exercises.split(','):
            if ex.isdigit():
                number = int(ex)
                started_ex.append(int(ex))
        return (exid.id in started_ex)


    def get_prof_list(self):
        """
        returns the of all proficient exercises
        """
        prof_ex = []
        for ex in self.all_proficient_exercises.split(','):
            if ex.isdigit():
                prof_ex.append(int(ex))
        return prof_ex


    def get_started_list(self):
        """
        returns the of all started exercises
        """
        start_ex = []
        for ex in self.started_exercises.split(','):
            if ex.isdigit():
                start_ex.append(int(ex))
        return start_ex





class UserExerciseLog(models.Model):
    """
    Table storing all the information about each exercise attempt
    """
    user =  models.ForeignKey(User)
    exercise =  models.ForeignKey(Exercise)
    correct = models.BooleanField(default = False)
    time_done = models.DateTimeField(auto_now_add=True)
    time_taken = models.IntegerField(default = 0)
    count_hints = models.IntegerField(default = 0)
    hint_used = models.BooleanField(default = False)
    points_earned = models.DecimalField(default = 0, \
                                        max_digits = 5, \
                                        decimal_places = 2)
    earned_proficiency = models.BooleanField(default = False) 
              # True if proficiency was earned on this problem
    count_attempts = models.BigIntegerField(default = 0)
    ip_address = models.CharField(max_length=20)
    ex_question = models.CharField(max_length=50)

    def put(self):
        """
        Adds a record to the table
        """
        models.Model.put(self)



class UserProgLog(models.Model):
    """
    Table storing all the additional information 
    about each programing exercise attempt
    """
    problem_log =  models.ForeignKey(UserExerciseLog)
    student_code = models.TextField()
    feedback = models.TextField() 


class UserProfExerciseLog(models.Model):
    """
    Table storing all the additional information 
    about each JSAV proficiency exercise attempt
    """
    problem_log =  models.ForeignKey(UserExerciseLog)
    student =  models.IntegerField(default = 0)
    correct =  models.IntegerField(default = 0)
    fix =  models.IntegerField(default = 0)
    undo =  models.IntegerField(default = 0)
    total =  models.IntegerField(default = 0)


class UserExercise(models.Model):
    """
    Table recording statistics about student attempts
    each record contains the data related to one student and one 
    exercise
    """
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
        """
        update statistics (correct/proficient/etc.) for KA exercises
        """
        exercise = Exercise.objects.get(pk=self.exercise_id)
        user_data = UserData.objects.get(user=self.user, book=ubook)
        dt_now = datetime.datetime.now()
        if correct and (self.longest_streak >= exercise.streak):
            self.proficient_date = dt_now

            user_data.save()
            return True
        return False

    def update_proficiency_pe(self, correct, ubook):
        """
        update statistics (correct/proficient/etc.) for 
        JSAV Proficiency exercises
        """
        exercise = Exercise.objects.get(pk=self.exercise_id)
        user_data = UserData.objects.get(user=self.user, book=ubook)
        dt_now = datetime.datetime.now()
        if correct:
            self.proficient_date = dt_now

            if len(user_data.all_proficient_exercises) == 0:
                user_data.all_proficient_exercises += "%s" % self.exercise_id
            else:
                user_data.all_proficient_exercises += ",%s" % self.exercise_id
            user_data.save()
            return True
        return False

    def is_proficient(self):
        """
        returns if the user already earned proficiency 
        """
        return (self.proficient_date != datetime.datetime.strptime( \
                                   '2012-01-01 00:00:00','%Y-%m-%d %H:%M:%S'))

class Bugs(models.Model):
    """
    Table to store bugs reported by users.
    Bugs have user information, user computer and bugs information.
    """
    user = models.ForeignKey(User)
    os_family = models.CharField(max_length=50)
    browser_family = models.CharField(max_length=20)
    title = models.CharField(max_length=50)
    description = models.TextField() 
    screenshot = models.ImageField(upload_to='bugs/%Y_%m_%d/', null=True, blank=True)
