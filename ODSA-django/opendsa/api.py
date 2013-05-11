import models
from decimal import Decimal
# Tastypie
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authentication import Authentication, OAuthAuthentication, ApiKeyAuthentication
from tastypie.authorization import DjangoAuthorization, ReadOnlyAuthorization, Authorization
from tastypie import fields
from tastypie.utils import trailing_slash
from tastypie.serializers import Serializer
from tastypie.http import HttpUnauthorized, HttpForbidden, HttpBadRequest
from tastypie.models import ApiKey
from tastypie.exceptions import NotRegistered, BadRequest


# ODSA
from opendsa.models import Exercise, UserExercise, UserExerciseLog, UserData, Module, UserModule, \
                           BookModuleExercise, Books, UserBook
from django.conf.urls.defaults import patterns, url
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.utils import simplejson
from django.contrib.sessions.models import Session
from django.http import HttpResponse
from django.db import transaction, IntegrityError
import jsonpickle

from exercises import attempt_problem, make_wrong_attempt, get_pe_name_from_referer, log_button_action, \
                      attempt_problem_pe, update_module_proficiency, student_grade_all, date_from_timestamp


# Key generation and verification
import hmac
import datetime
import time
try:
    from hashlib import sha1
except ImportError:
    import sha
    sha1 = sha.sha

# Utility functions
def create_key(username):
    key = str(username) + str(datetime.datetime.now())
    msg = 'opendsa.cc.vt.edu'
    hash_key = hmac.new(key, msg, sha1)
    return hash_key.digest().encode('hex')

def get_user_by_key(key):
    if  len(ApiKey.objects.filter(key=key)) != 1:
        return None
    else:
        return ApiKey.objects.get(key=key).user

# Safe accessor methods - these functions are designed to prevent the problem of duplicate entries being created
def get_username(key):
    if key == 'phantom-key':
        with transaction.commit_on_success():
            kusername, created = User.objects.get_or_create(username="phantom")
    else:
        kusername = get_user_by_key(key)

    return kusername

def get_book(name):
    if Books.objects.filter(book_name=name).count() == 1:
        book = Books.objects.get(book_name=name)
    elif Books.objects.filter(book_name=name).count() > 1:
        book = Books.objects.filter(book_name=name)[0]
    else:
        book = None

    return book

def get_module(name):
    if Module.objects.filter(name=name).count() == 1:
        module = Module.objects.get(name=name)
    elif Module.objects.filter(name=name).count() > 1:
        module = Module.objects.filter(name=name)[0]
    else:
        module = None

    return module

def get_exercise(exercise):
    if Exercise.objects.filter(name=exercise).count() == 1:
        exercise = Exercise.objects.get(name=exercise)
    elif Exercise.objects.filter(name=exercise).count() > 1:
        exercise = Exercise.objects.filter(name=exercise)[0]
    else:
        exercise = None

    return exercise

def get_user_book(user, book):
    if UserBook.objects.filter(user=user, book=book).count() == 1:
        ubook = UserBook.objects.get(user=user, book=book)
    elif UserBook.objects.filter(user=user, book=book).count() > 1:
        ubook = UserBook.objects.filter(user=user, book=book)[0]
    else:
        ubook = None

    return ubook

def get_user_module(user, book, module):
    if UserModule.objects.filter(user=user, book=book, module=module).count() == 1:
        umod = UserModule.objects.get(user=user, book=book, module=module)
    elif UserModule.objects.filter(user=user, book=book, module=module).count() > 1:
        umod = UserModule.objects.filter(user=user, book=book, module=module)[0]
    else:
        umod = None

    return umod

def get_user_exercise(user, exercise):
    if UserExercise.objects.filter(user=user, exercise=exercise).count() == 1:
        user_exercise = UserExercise.objects.get(user=user, exercise=exercise)
    elif UserExercise.objects.filter(user=user, exercise=exercise).count() > 1:
        user_exercise = UserExercise.objects.filter(user=user, exercise=exercise)[0]
    else:
        user_exercise = None

    return user_exercise




class OpendsaAuthentication(ApiKeyAuthentication):
    def is_authenticated(self, request, **kwargs):
        print '%s' %request
        try:
            user = User.objects.get(username=request.POST['username']) or  User.objects.get(username=request.GET['username'])
            key  = request.POST['key'] or  request.GET['key']
            user_key = ApiKey.objects.get(user=user)
            return user_key.key == key
        except:
            return self._unauthorized()

#create new user
class CreateUserResource(ModelResource):
    def determine_format(self, request):
        return "application/json"
    class Meta:
        allowed_methods = ['post']
        object_class = User
        resource_name   = 'newuser'
        authentication = Authentication()
        authorization = Authorization()
        include_resource_uri = False
        fields = ['username']

    def obj_create(self, bundle, request=None, **kwargs):
        try:
            bundle.obj = User.objects.create_user(bundle.data.get('username'), bundle.data.get('email'), bundle.data.get('password'))
            bundle.obj.save()
        except IntegrityError:
            raise BadRequest('That username already exists')
        return bundle


#user authentication and registration through the api
class UserResource(ModelResource):
    def determine_format(self, request):
        return "application/json"

    def is_authenticated(self, request, **kwargs):
        from django.contrib.sessions.models import Session
        if 'sessionid' in request.COOKIES:
            s = Session.objects.get(pk=request.COOKIES['sessionid'])
            if '_auth_user_id' in s.get_decoded():
                u = User.objects.get(id=s.get_decoded()['_auth_user_id'])
                request.user = u
                return True
        return False

    class Meta:
        queryset = User.objects.all()
        allowed_methods = ['get', 'post']
        resource_name   = 'users'
        excludes        = []
        serializer = Serializer(formats=['json'])

    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/login%s$" %(self._meta.resource_name, trailing_slash()),self.wrap_view('login'), name="api_signin"),
            url(r"^(?P<resource_name>%s)/logout%s$" %(self._meta.resource_name, trailing_slash()),self.wrap_view('logout'), name="api_signin"),
        ]

    def login(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        username = request.POST['username']
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                hash_key = create_key(username)
                with transaction.commit_on_success():
                    user_key, created = ApiKey.objects.get_or_create(user=user)
                user_key.key = hash_key
                user_key.save()
                return self.create_response(request, {'success': True, 'key':hash_key })
            else:
                # Return a 'disabled account' error message
                return self.create_response(request, {'success': False, 'reason': 'disabled',}, HttpForbidden)
        else:
            # Return an 'invalid login' error message.
            return self.create_response(request, {'success': False, 'reason': 'incorrect',}, HttpUnauthorized)

    def logout(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        if request.user and request.user.is_authenticated():
            logout(request)
            return self.create_response(request, {'success': True})
        else:
            return self.create_response(request, {'success': False}, HttpUnauthorized)



class ExerciseResource(ModelResource):
    #instances           = fields.ToManyField('course.api.CourseInstanceResource', 'instances')
    def determine_format(self, request):
        return "application/json"

    class Meta:
        queryset      = Exercise.objects.all()
        resource_name = 'exercises'
        excludes      = []

        # TODO: In this version, only GET requests are accepted and no
        # permissions are checked.
        allowed_methods = ['get']
        authentication  = Authentication()
        authorization   = ReadOnlyAuthorization()
        filtering = {
            'name': ('exact',),
        }

    def get_object_list(self, request):
        #Store KA exercise content load in UserButton table
        if request.GET['key']:
            kusername = get_username(request.GET['key'])
        if kusername:
            if  Exercise.objects.filter(name=request.GET['name']).count()==1:
                kexercise = Exercise.objects.get(name=request.GET['name'])

                with transaction.commit_on_success():
                    kbook = Books.objects.get(book_name= request.GET['book'])
                    user_data, created = UserData.objects.get_or_create(user=kusername,book=kbook)
                module = get_module(request.GET['module'])

                if kexercise and module:
                    with transaction.commit_on_success():
                        user_module, exist =  UserModule.objects.get_or_create(user=kusername, book=kbook,module=module)
                    text = 'User loaded %s exercise' %request.GET['name']
                    user_button,correct = log_button_action(
                        kusername,
                        kexercise,
                        module,
                        kbook,
                        'load-ka',
                        text,
                        time.time()*1000,
                        None,
                        request.user_agent.browser.family,
                        request.user_agent.browser.version_string,
                        request.user_agent.os.family,
                        request.user_agent.os.version_string,
                        request.user_agent.device.family,
                        request.META['REMOTE_ADDR'],
                        )

        return super(ExerciseResource, self).get_object_list(request)



class UserexerciseResource(ModelResource):
    #course_modules      = fields.ToManyField('exercise.api.CourseModuleResource', 'course_modules')

    #def dehydrate(self, bundle):
    #    bundle.data.update({"is_open": bundle.obj.is_open()})
    #    bundle.data.update({"browser_url": bundle.obj.get_absolute_url()})
    #    return bundle
    def determine_format(self, request):
        return "application/json"

    class Meta:
        queryset        = UserExercise.objects.all()
        resource_name   = 'user/exercise'
        excludes        = []

        allowed_methods = ['get','post']
        authentication  = Authentication()
        authorization   = ReadOnlyAuthorization()
    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/attempt%s$" %(self._meta.resource_name, trailing_slash()),self.wrap_view('logexercise'), name="api_logexe"),
            url(r"^(?P<resource_name>%s)/hint%s$" %(self._meta.resource_name, trailing_slash()),self.wrap_view('logexercisehint'), name="api_logexeh"),
            url(r"^(?P<resource_name>%s)/attemptpe%s$" %(self._meta.resource_name, trailing_slash()),self.wrap_view('logpeexercise'), name="api_logpeexe"), #return success and isproficient??
            url(r"^(?P<resource_name>%s)/avbutton%s$" %(self._meta.resource_name, trailing_slash()),self.wrap_view('logavbutton'), name="api_logavbutt"),
             url(r"^(?P<resource_name>%s)/getprogress%s$" %(self._meta.resource_name, trailing_slash()),self.wrap_view('getprogress'), name="api_getprogress"),
        ]

    def listlogs():
        return UserExercise.objects.all()

    def getprogress(self, request, **kwargs):
        if  request.POST['key']:
            kusername = get_username(request.POST['key'])
            kexercise = Exercise.objects.get(name=request.POST['exercise'])
            user_exercise = get_user_exercise(kusername, kexercise)

            if user_exercise is not None:
                return self.create_response(request, {'progress': user_exercise.progress})
        return self.create_response(request, {'progress': 0})

    def logavbutton(self, request, **kwargs):
        print request.POST
        if request.POST['key']:
            kusername = get_username(request.POST['key'])

        if kusername:
            actions = simplejson.loads(request.POST['actions'])
            number_logs = 0
            for act in actions:
                if 'score[total]' in request.POST:
                    streak = request.POST['score[total]']
                else:
                    streak = 0

                if  Exercise.objects.filter(name=act['av']).count()==1:
                    kexercise = Exercise.objects.get(name=act['av'])
                else:
                    with transaction.commit_on_success():
                        kexercise = Exercise(name=act['av'], streak=streak)
                        kexercise.save()

                with transaction.commit_on_success():
                    kbook = Books.objects.get(book_name= request.POST['book'])
                    user_data, created = UserData.objects.get_or_create(user=kusername,book=kbook)
                module = get_module(act['module'])

                if kexercise and module:
                    with transaction.commit_on_success():
                        user_module, exist =  UserModule.objects.get_or_create(user=kusername, book=kbook,module=module)
                    user_button,correct = log_button_action(
                        kusername,
                        kexercise,
                        module,
                        kbook,
                        act['type'],
                        act['desc'],
                        act['tstamp'],
                        act['uiid'],
                        request.user_agent.browser.family,
                        request.user_agent.browser.version_string,
                        request.user_agent.os.family,
                        request.user_agent.os.version_string,
                        request.user_agent.device.family,
                        request.META['REMOTE_ADDR'],
                        )
                    if correct:
                        number_logs += 1

            if number_logs == len(actions):
                return self.create_response(request, {'success': True, 'message': 'all button action logged'})
            else:
                return self.create_response(request, {'success': False, 'error': 'not all button action logged'}, HttpBadRequest)
        return self.create_response(request, {'success': False, 'error': 'unauthorized action'}, HttpUnauthorized)

    def logpeexercise(self, request, **kwargs):
        print request
        if request.POST['key']:
            kusername = get_username(request.POST['key'])
            dsa_book = get_book(request.POST['book'])
            kexercise = get_exercise(request.POST['exercise'])

            if kusername and kexercise:
                user_exercise = get_user_exercise(kusername, kexercise)

                # Create a new UserExercise object if necessary
                if user_exercise is None:
                    with transaction.commit_on_success():
                        user_exercise, exe_created = UserExercise.objects.get_or_create(user=kusername, exercise=kexercise, streak=0, first_done=date_from_timestamp(int(request.POST['tstamp'])))
            else:
                return self.create_response(request, {'error': 'attempt not logged'}, HttpUnauthorized)

            with transaction.commit_on_success():
                user_data, created = UserData.objects.get_or_create(user=kusername, book=dsa_book)

            ubook = get_user_book(kusername, dsa_book)
            module = get_module(request.POST['module'])
            if user_exercise and ubook:
                user_exercise,correct = attempt_problem_pe(
                    user_data,
                    user_exercise,
                    request.POST['uiid'],  #attempt_number
                    1, #completed
                    int(request.POST['tstamp']), #submit_time
                    request.POST['total_time'],   #time_taken
                    kexercise.streak, #threshold
                    Decimal(request.POST['score']), #score
                    request.POST['module'],
                    request.META['REMOTE_ADDR'],
                    )
                return self.create_response(request, {'success': True, 'proficient': user_exercise.is_proficient()})
            else:
                return  self.create_response(request, {'error': 'attempt not logged'}, HttpBadRequest)
        return self.create_response(request, {'error': 'unauthorized action'}, HttpUnauthorized)

    def logexercise(self, request, **kwargs):
        if request.POST['key']:
            kusername = get_username(request.POST['key'])
            kexercise = get_exercise(request.POST['sha1'])

            if kusername and kexercise:
                user_exercise = get_user_exercise(kusername, kexercise)

                if user_exercise is None:
                    with transaction.commit_on_success():
                        user_exercise, exe_created = UserExercise.objects.get_or_create(user=kusername, exercise=kexercise, streak=0)
            else:
                return self.create_response(request, {'error': 'attempt not logged'}, HttpUnauthorized)

            dsa_book = get_book(request.POST['book'])
            ubook = get_user_book(kusername, dsa_book)

            with transaction.commit_on_success():
                user_data, created = UserData.objects.get_or_create(user=kusername, book=dsa_book)

            module = get_module(request.POST['module_name'])

            if user_exercise and ubook:
                ex_question = request.POST['sha1']
                if 'non_summative' in request.POST:
                    ex_question = request.POST['non_summative']
                user_exercise,correct = attempt_problem(
                    user_data,  #kusername,
                    user_exercise,
                    request.POST['attempt_number'],
                    request.POST['complete'],
                    request.POST['count_hints'],
                    int(request.POST['time_taken']),
                    request.POST['attempt_content'],
                    request.POST['module_name'],
                    ex_question,
                    request.META['REMOTE_ADDR'],
                    )

                if correct:
                    print jsonpickle.encode(user_exercise)
                    return  self.create_response(request, jsonpickle.encode(user_exercise))
                else:
                    return  self.create_response(request, {'error': 'attempt not logged'}, HttpBadRequest)
        return self.create_response(request, {'error': 'unauthorized action'}, HttpUnauthorized)

    def logexercisehint(self, request, **kwargs):
        if request.POST['key']:
            kusername = get_username(request.POST['key'])
            kexercise = get_exercise(request.POST['sha1'])

            if kusername and kexercise:
                user_exercise = get_user_exercise(kusername, kexercise)

                if user_exercise is None:
                    with transaction.commit_on_success():
                        user_exercise, exe_created = UserExercise.objects.get_or_create(user=kusername, exercise=kexercise, streak=0)
            else:
                return  self.create_response(request, {'error': 'attempt not logged'}, HttpUnauthorized)

            dsa_book = get_book(request.POST['book'])
            ubook = get_user_book(kusername, dsa_book)

            with transaction.commit_on_success():
                user_data, created = UserData.objects.get_or_create(user=kusername,book=dsa_book)

            module = get_module(request.POST['module_name'])

            if user_exercise and ubook:
                bme = BookModuleExercise.components.filter(book=ubook.book, module=module, exercise=kexercise)[0]
                ex_question = request.POST['sha1']
                if 'non_summative' in request.POST:
                    ex_question = request.POST['non_summative']
                user_exercise,correct = attempt_problem(
                    user_data,
                    user_exercise,
                    request.POST['attempt_number'],
                    request.POST['complete'],
                    request.POST['count_hints'],
                    int(request.POST['time_taken']),
                    request.POST['attempt_content'],
                    request.POST['module_name'],
                    ex_question, 
                    request.META['REMOTE_ADDR'],
                    )

                if correct:
                    print jsonpickle.encode(user_exercise)
                    return  self.create_response(request, jsonpickle.encode(user_exercise) )
                else:
                    return  self.create_response(request, {'error': 'attempt not logged'}, HttpBadRequest)

        return self.create_response(request, {'error': 'unauthorized action'},HttpUnauthorized)

    def obj_create(self, bundle, request=None, **kwargs):
        try:
            bundle = super(CreateUserResource, self).obj_create(bundle, request, **kwargs)
            bundle.obj.set_password(bundle.data.get('password'))
            bundle.obj.save()
        except IntegrityError:
            raise BadRequest('That username already exists')
        return bundle


class ProblemlogResource(ModelResource):
    #instances           = fields.ToManyField('course.api.CourseInstanceResource', 'instances')
    def determine_format(self, request):
        return "application/json"
    class Meta:
        queryset      = UserExerciseLog.objects.all()
        resource_name = 'problemlog'
        excludes      = []

        # TODO: In this version, only GET requests are accepted and no
        # permissions are checked.
        allowed_methods = ['get']
        authentication  = Authentication()
        authorization   = ReadOnlyAuthorization()




class UserDataResource(ModelResource):
    #instances           = fields.ToManyField('course.api.CourseInstanceResource', 'instances')
    def determine_format(self, request):
        return "application/json"
    class Meta:
        queryset      = UserData.objects.all()
        resource_name = 'userdata'
        excludes      = []

        # TODO: In this version, only GET requests are accepted and no
        # permissions are checked.
        allowed_methods = ['get','post']
        authentication  = Authentication()
        authorization   = ReadOnlyAuthorization()
    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/isproficient%s$" %(self._meta.resource_name, trailing_slash()),self.wrap_view('isproficient'), name="api_exeproficient"),
            url(r"^(?P<resource_name>%s)/getgrade%s$" %(self._meta.resource_name, trailing_slash()),self.wrap_view('getgrade'), name="api_getgrade"),
        ]

    def isproficient(self, request, **kwargs):

        if request.POST['key']:
            kusername = get_username(request.POST['key'])
            kexercise = get_exercise(request.POST['exercise'])
            dsa_book = get_book(request.POST['book'])

            user_data = UserData.objects.filter(user=kusername, book=dsa_book)[0]

            if kexercise:
                return self.create_response(request, {'proficient': user_data.is_proficient_at(kexercise)})
        return self.create_response(request, {'proficient': False})


    def getgrade(self, request, **kwargs):
        if request.POST['key']:
            kusername = get_username(request.POST['key'])
            dsa_book = get_book(request.POST['book'])

            if kusername:
                return self.create_response(request, student_grade_all(kusername, dsa_book))
        return self.create_response(request, {'grade': False})




class ModuleResource(ModelResource):

    def determine_format(self, request):
        return "application/json"
    class Meta:
        queryset        = Module.objects.all()
        resource_name   = 'module'
        excludes        = []

        # TODO: In this version, only GET requests are accepted and no
        # permissions are checked.
        allowed_methods = ['get','post']
        authentication  = Authentication()
        authorization   = ReadOnlyAuthorization()
    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/loadmodule%s$" %(self._meta.resource_name, trailing_slash()),self.wrap_view('loadmodule'), name="api_modproficient"),
        ]

    def loadmodule(self, request, **kwargs):
        if request.POST['key']:
            kusername = get_username(request.POST['key'])

            if kusername:
                response = {}
                #get or create Book & link a book to user
                kbook = get_book(request.POST['book'])

                if kbook is None:
                    with transaction.commit_on_success():
                        kbook, added = Books.objects.get_or_create(book_name= request.POST['book'], book_url = request.POST['url'])
                        ubook, created = UserBook.objects.get_or_create(user=kusername, book=kbook)
                else:
                    #link a book to user
                    ubook = get_user_book(kusername, kbook)

                    if ubook is None:
                         with transaction.commit_on_success():
                             ubook, created = UserBook.objects.get_or_create(user=kusername, book=kbook)

                #get or create module
                kmodule = get_module(request.POST['module'])
                
                if kmodule is None:
                    with transaction.commit_on_success():
                        kmodule, added = Module.objects.get_or_create(name=request.POST['module'])
                
                response[kmodule.name] = False

                #get or create exercises
                mod_exes = simplejson.loads(request.POST['exercises'])
                print mod_exes
                exers_ = []
                for mod_exe in mod_exes:
                    if Exercise.objects.filter(name=mod_exe['exercise']).count() == 0:
                        # Add new exercise
                        with transaction.commit_on_success():
                            kexercise, added = Exercise.objects.get_or_create(name=mod_exe['exercise'], covers="dsa", description=mod_exe['name'], ex_type=mod_exe['type'], streak=mod_exe['threshold'])
                    else:
                        # Update existing exercise
                        with transaction.commit_on_success():
                            kexercise = get_exercise(mod_exe['exercise'])
                            kexercise.covers="dsa"
                            kexercise.description=mod_exe['name']
                            kexercise.ex_type=mod_exe['type']
                            kexercise.streak=Decimal(mod_exe['threshold'])
                            kexercise.save()
                    #add exercise in list of module exercises
                    exers_.append(kexercise)
                    if UserData.objects.filter(user=kusername, book=kbook).count() > 0:
                        user_data = UserData.objects.get(user=kusername, book=kbook)
                        u_prof = user_data.is_proficient_at(kexercise)

                    #check student progress -- KA exercises
                    user_exercise = get_user_exercise(user=kusername, exercise=kexercise)

                    if user_exercise is not None:
                        u_prog = user_exercise.progress
                        if user_exercise.is_proficient() and not user_data.is_proficient_at(kexercise):
                            user_data.earned_proficiency(kexercise.id)
                            user_data.save()
                            u_prof = True
                    else:
                        u_prog = 0

                    #Link exercise to module and books only if the exercise is required
                    if BookModuleExercise.components.filter(book=kbook, module=kmodule, exercise=kexercise).count() == 0 and mod_exe['required']:
                        with transaction.commit_on_success():
                            bme = models.BookModuleExercise(book=kbook, module=kmodule, exercise=kexercise, points=mod_exe['points'])
                            bme.save()
                    response[kexercise.name] = {'proficient': u_prof, 'progress': u_prog}

                # Remove exercises that are no longer part of this book / module
                for exer in BookModuleExercise.components.get_mod_exercise_list(kbook,kmodule): #get_exercise_list(kbook):
                  if exer not in exers_:
                    BookModuleExercise.components.filter(book=kbook, module=kmodule, exercise=exer).delete()

                #check module proficiency
                user_module = get_user_module(user=kusername, book=kbook, module=kmodule)

                if user_module is not None:
                    with transaction.commit_on_success():
                        user_data, created = UserData.objects.get_or_create(user=kusername,book = kbook)

                    update_module_proficiency(user_data, request.POST['module'], None)

                    #Module proficiency response
                    response[kmodule.name] = user_module.is_proficient_at()
                return self.create_response(request, response)
        return self.create_response(request, {'error': 'unauthorized action'}, HttpUnauthorized)


class UserModuleResource(ModelResource):

    def determine_format(self, request):
        return "application/json"
    class Meta:
        queryset        = UserData.objects.all()
        resource_name   = 'usermodule'
        excludes        = []

        # TODO: In this version, only GET requests are accepted and no
        # permissions are checked.
        allowed_methods = ['get','post']
        authentication  = Authentication()
        authorization   = ReadOnlyAuthorization()
    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/ismoduleproficient%s$" %(self._meta.resource_name, trailing_slash()),self.wrap_view('ismoduleproficient'), name="api_modproficient"),
        ]

    def ismoduleproficient(self, request, **kwargs):
        if request.POST['key']:
            print request.POST['key']
            kusername = get_username(request.POST['key'])
        if kusername:
            kmodule = get_module(request.POST['module'])
            kbook = get_book(request.POST['book'])
            user_module = get_user_module(kusername, kbook, kmodule)

            if user_module is not None:
                with transaction.commit_on_success():
                    user_data, created = UserData.objects.get_or_create(user=kusername, book=kbook)

                update_module_proficiency(user_data, request.POST['module'], None)
                return self.create_response(request, {'proficient': user_module.is_proficient_at()})

            return self.create_response(request, {'proficient': False})
        return self.create_response(request, {'error': 'unauthorized action'}, HttpUnauthorized)



class UserExerciseSummaryResource(ModelResource):
    #instances           = fields.ToManyField('course.api.CourseInstanceResource', 'instances')
    def determine_format(self, request):
        return "application/json"
    class Meta:
        queryset        = UserExercise.objects.all()
        resource_name   = 'userlog'
        excludes        = []

        # TODO: In this version, only GET requests are accepted and no
        # permissions are checked.
        allowed_methods = ['get']
        authentication  = Authentication()
        authorization   = ReadOnlyAuthorization()
