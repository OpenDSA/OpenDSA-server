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
try:
    from hashlib import sha1
except ImportError:
    import sha
    sha1 = sha.sha

def create_key(username):
    key = str(username) + str(datetime.datetime.now())
    msg = 'opendsa.cc.vt.edu'
    hash_key = hmac.new(key, msg, sha1)
    return hash_key.digest().encode('hex')

def get_user_by_key(key):
    if  len(ApiKey.objects.filter(key=key))!=1:
        return None
    else:
        return ApiKey.objects.get(key=key).user 

class OpendsaAuthentication(ApiKeyAuthentication):
    def is_authenticated(self, request, **kwargs):
        print '%s' %request 
        try:
            user = User.objects.get(username=request.POST['username']) or  User.objects.get(username=request.GET['username']) 
            key  = request.POST['key'] or  request.GET['key']
            user_key = ApiKey.objects.get(user=user)
            return  user_key.key == key
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
                user_key, created = ApiKey.objects.get_or_create(user=user) 
                user_key.key = hash_key
                user_key.save()
                return self.create_response(request, {'success': True,'key':hash_key })
            else:
                # Return a 'disabled account' error message
                return self.create_response(request, {'success': False, 'reason': 'disabled',}, HttpForbidden)
        else:
            # Return an 'invalid login' error message.
            return self.create_response(request, {'success': False, 'reason': 'incorrect',}, HttpUnauthorized )

    def logout(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        if request.user and request.user.is_authenticated():
            logout(request)
            return self.create_response(request, { 'success': True })
        else:
            return self.create_response(request, { 'success': False }, HttpUnauthorized) 



class ExerciseResource(ModelResource):
    #instances           = fields.ToManyField('course.api.CourseInstanceResource', 'instances')
    def determine_format(self, request): 
        return "application/json"     

    class Meta:
        queryset        = Exercise.objects.all()
        resource_name   = 'exercises'
        excludes        = []
        
        # TODO: In this version, only GET requests are accepted and no 
        # permissions are checked.
        allowed_methods = ['get']
        authentication  = OpendsaAuthentication()   #Authentication()
        authorization   = ReadOnlyAuthorization()
        filtering = {
            'name': ('exact',), 
        }
 

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
            if request.POST['key']=='phantom-key':
                with transaction.commit_on_success():
                    kusername, created = User.objects.get_or_create(username="phantom")
            else:
                kusername = get_user_by_key(request.POST['key'])    #request.user:
            kexercise =  Exercise.objects.get(name= request.POST['exercise']) 
            if  UserExercise.objects.filter(user=kusername, exercise=kexercise).count()==1:
                user_exercise =  UserExercise.objects.get(user=kusername, exercise=kexercise)
            elif UserExercise.objects.filter(user=kusername, exercise=kexercise).count()>1:
                  user_exercise =UserExercise.objects.filter(user=kusername, exercise=kexercise)[0]  
            else:
                user_exercise = None
            if user_exercise is not None:
                return self.create_response(request, {'progress': user_exercise.progress})
            self.create_response(request, {'progress': 0})
        return self.create_response(request, {'progress': 0})


    def logavbutton(self, request, **kwargs):
        print request.POST  
        if request.POST['key']:
            if request.POST['key']=='phantom-key':
                with transaction.commit_on_success():
                    kusername, created = User.objects.get_or_create(username="phantom")   
            else:    
                kusername = get_user_by_key(request.POST['key'])    #request.POST['username']:   
        if kusername:
            action =   request.POST['actions']
            actions = simplejson.loads(action)
            number_logs = 0
            for act in actions:
               if 'score[total]' in request.POST:
                  streak = request.POST['score[total]'] 
               else:
                  streak = 0 

               if  Exercise.objects.filter(name= act['av']).count()==1:
                   kexercise =  Exercise.objects.get(name= act['av'])
               else:
                   with transaction.commit_on_success():
                       kexercise = Exercise(name = act['av'], streak=streak)
                       kexercise.save()       
               with transaction.commit_on_success():
                   kbook = Books.objects.get(book_name= request.POST['book'])
                   user_data, created = UserData.objects.get_or_create(user=kusername,book=kbook)
               module = None 
               if Module.objects.filter(name=act['module']).count()>0: 
                  module = Module.objects.get(name=act['module'])  
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
                    number_logs += 1 #return  self.create_response(request, user_button)
            if number_logs == len(actions):
                return  self.create_response(request,  {'success':True, 'message': 'all button action logged'})
            else:
                    return  self.create_response(request, {'success':False, 'error': 'not all button action logged'}, HttpBadRequest)
        return self.create_response(request, {'success':False, 'error': 'unauthorized action'}, HttpUnauthorized)


    def logpeexercise(self, request, **kwargs):
        print request 
        if request.POST['key']:
            if request.POST['key']=='phantom-key':
                with transaction.commit_on_success():
                    kusername, created = User.objects.get_or_create(username="phantom")
            else:
                kusername = get_user_by_key(request.POST['key'])   
            jsav_exercise = request.POST['exercise']
            if Books.objects.filter(book_name=request.POST['book']).count()==1:
                dsa_book = Books.objects.get(book_name=request.POST['book'])
            else:
                dsa_book = None
            if  Exercise.objects.filter(name= jsav_exercise).count()==1:
                kexercise =  Exercise.objects.get(name= jsav_exercise) 
            else: 
                kexercise = None
            if kusername and kexercise:
                if UserExercise.objects.filter(user=kusername, exercise=kexercise).count()==0:
                    with transaction.commit_on_success():
                        user_exercise, exe_created = UserExercise.objects.get_or_create(user=kusername, exercise=kexercise, streak=0, first_done=date_from_timestamp(int(request.POST['tstamp']))) 
                else:
                    user_exercise = UserExercise.objects.get(user=kusername, exercise=kexercise)
            else:   
                return  self.create_response(request, {'error': 'attempt not logged'}, HttpUnauthorized) 
            if UserBook.objects.filter(user=kusername,book=dsa_book).count()==1:
                ubook = UserBook.objects.get(user=kusername,book=dsa_book)
            else:
                ubook= None
            with transaction.commit_on_success(): 
                user_data, created = UserData.objects.get_or_create(user=kusername,book=dsa_book)
            module = Module.objects.get(name=request.POST['module']) 
            if user_exercise and ubook:
                    bme = BookModuleExercise.objects.filter(book = ubook.book, module = module, exercise=kexercise)[0]
                    user_exercise,correct = attempt_problem_pe(
                       user_data,  
                       user_exercise,
                       request.POST['uiid'],  #attempt_number
                       1, #completed
                       int(request.POST['tstamp']), #submit_time
                       request.POST['total_time'],   #time_taken
                       kexercise.streak, #threshold
                       Decimal(request.POST['score']), #score
                       bme.points,  #request.POST['points'],
                       request.POST['module'], 
                       request.META['REMOTE_ADDR'],
                       )
                    return  self.create_response(request, {'success': True, 'proficient': correct})   
            else:
                    return  self.create_response(request, {'error': 'attempt not logged'}, HttpBadRequest)
        return self.create_response(request, {'error': 'unauthorized action'}, HttpUnauthorized)



 
    def logexercise(self, request, **kwargs):
        #if request.POST['user']:    #request.user:
        if request.POST['key']:
            if request.POST['key']=='phantom-key':
                with transaction.commit_on_success():
                    kusername, created = User.objects.get_or_create(username="phantom")
            else:
                kusername = get_user_by_key(request.POST['key'])
            ka_exercise = request.POST['sha1']
            if Books.objects.filter(book_name=request.POST['book']).count()==1:
                dsa_book = Books.objects.get(book_name=request.POST['book'])
            else:
                dsa_book = None
            if  Exercise.objects.filter(name= ka_exercise).count()==1:
                kexercise =  Exercise.objects.get(name= ka_exercise)
            else:
                kexercise = None
            if kusername and kexercise:
                 if UserExercise.objects.filter(user=kusername, exercise=kexercise).count()==0:
                    user_exercise, exe_created = UserExercise.objects.get_or_create(user=kusername, exercise=kexercise, streak=0)
                 else:
                    user_exercise = UserExercise.objects.get(user=kusername, exercise=kexercise)
            else:
                return  self.create_response(request, {'error': 'attempt not logged'}, HttpUnauthorized)
            if UserBook.objects.filter(user=kusername,book=dsa_book).count()==1:
                ubook = UserBook.objects.get(user=kusername,book=dsa_book)
            else:
                ubook= None
            with transaction.commit_on_success():
                user_data, created = UserData.objects.get_or_create(user=kusername,book=dsa_book)
            module = Module.objects.get(name=request.POST['module_name'])
            if user_exercise and ubook:
                bme = BookModuleExercise.objects.filter(book = ubook.book, module = module, exercise=kexercise)[0]
                user_exercise,correct = attempt_problem(
                   user_data,  #kusername,
                   user_exercise,
                   request.POST['attempt_number'],
                   request.POST['complete'],
                   request.POST['count_hints'],
                   int(request.POST['time_taken']),
                   request.POST['attempt_content'],
                   request.POST['module_name'],
                   bme.points,
                   request.META['REMOTE_ADDR'],
                   )
                if correct:
                   print jsonpickle.encode(user_exercise)
                   return  self.create_response(request, jsonpickle.encode(user_exercise) )           #    user_exercise) 
                else:
                   return  self.create_response(request, {'error': 'attempt not logged'}, HttpBadRequest)   
        return self.create_response(request, {'error': 'unauthorized action'}, HttpUnauthorized)
 
    def logexercisehint(self, request, **kwargs):
        if request.POST['key']:
            if request.POST['key']=='phantom-key':
                with transaction.commit_on_success():
                    kusername, created = User.objects.get_or_create(username="phantom")
            else:
                kusername = get_user_by_key(request.POST['key'])
            ka_exercise = request.POST['sha1']
            if Books.objects.filter(book_name=request.POST['book']).count()==1:
                dsa_book = Books.objects.get(book_name=request.POST['book'])
            else:
                dsa_book = None   
            if  Exercise.objects.filter(name= ka_exercise).count()==1:
                kexercise =  Exercise.objects.get(name= ka_exercise)
            else:
                kexercise = None
            if kusername and kexercise:
                 if UserExercise.objects.filter(user=kusername, exercise=kexercise).count()==0:
                    user_exercise, exe_created = UserExercise.objects.get_or_create(user=kusername, exercise=kexercise, streak=0)
                 else:
                    user_exercise = UserExercise.objects.get(user=kusername, exercise=kexercise)
            else:
                return  self.create_response(request, {'error': 'attempt not logged'}, HttpUnauthorized)
            if UserBook.objects.filter(user=kusername,book=dsa_book).count()==1:
                ubook = UserBook.objects.get(user=kusername,book=dsa_book)
            else:
                ubook= None
            with transaction.commit_on_success():
                user_data, created = UserData.objects.get_or_create(user=kusername,book=dsa_book)
            module = Module.objects.get(name=request.POST['module_name'])
            if user_exercise and ubook:
                bme = BookModuleExercise.objects.filter(book = ubook.book, module = module, exercise=kexercise)[0]

                user_exercise,correct = attempt_problem(
                   user_data,  
                   user_exercise,
                   request.POST['attempt_number'],
                   request.POST['complete'],
                   request.POST['count_hints'],
                   int(request.POST['time_taken']),
                   request.POST['attempt_content'],
                   request.POST['module_name'],
                   bme.points,
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
        queryset        = UserExerciseLog.objects.all()
        resource_name   = 'problemlog'
        excludes        = []

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
        queryset        = UserData.objects.all()
        resource_name   = 'userdata'
        excludes        = []

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
            if request.POST['key']=='phantom-key':
                with transaction.commit_on_success():
                    kusername, created = User.objects.get_or_create(username="phantom")
            else:
                kusername = get_user_by_key(request.POST['key'])      #request.POST['username']:    #request.user:
            #with transaction.commit_on_success():
            jsav_exercise = request.POST['exercise']
            if  Exercise.objects.filter(name= jsav_exercise).count()==1:
                kexercise =  Exercise.objects.get(name= jsav_exercise)
            else:
                kexercise = None
            kbook = Books.objects.get(book_name= request.POST['book']) 
            user_data = UserData.objects.filter(user=kusername,book=kbook)[0]
            if kexercise:
                return self.create_response(request, {'proficient': user_data.is_proficient_at(kexercise)}) 
            self.create_response(request, {'proficient': False}) 
        return self.create_response(request, {'proficient': False})


    def getgrade(self, request, **kwargs):

        if request.POST['key']:    #request.user:
            if request.POST['key']=='phantom-key':
                with transaction.commit_on_success():
                    kusername, created = User.objects.get_or_create(username="phantom")
            else:
                kusername = get_user_by_key(request.POST['key'])
            #kusername = User.objects.get(username=request.POST['username'])
            kbook = Books.objects.get(book_name= request.POST['book'])
            if kusername:
                return self.create_response(request, student_grade_all(kusername, kbook))
            self.create_response(request, {'grade': False})
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

            if request.POST['key']=='phantom-key':
                with transaction.commit_on_success():
                    kusername, created = User.objects.get_or_create(username="phantom")
            else:
                kusername = get_user_by_key(request.POST['key'])
            if kusername:
                response = {}
                #get or create Book & link a book to user  
                if Books.objects.filter(book_name=request.POST['book']).count()==0:  
                    with transaction.commit_on_success():
                        kbook,added = Books.objects.get_or_create(book_name= request.POST['book'], book_url = request.POST['url'])
                        ubook,created = UserBook.objects.get_or_create(user=kusername, book=kbook) 
                else:
                    kbook = Books.objects.get(book_name= request.POST['book'])
                    #link a book to user
                    if UserBook.objects.filter(user=kusername, book=kbook).count()==0:
                         with transaction.commit_on_success():
                             ubook,created = UserBook.objects.get_or_create(user=kusername, book=kbook)    
                #get or create module
                if Module.objects.filter(name=request.POST['module']).count()==0:
                    with transaction.commit_on_success():
                        kmodule,added = Module.objects.get_or_create(name= request.POST['module'])
                else:
                    kmodule = Module.objects.get(name= request.POST['module'])
                response[kmodule.name] = False
                #get or create exercises
                exercises =   request.POST['exercises']
                mod_exes = simplejson.loads(exercises) 
                print mod_exes  
                for mod_exe in mod_exes:  
                    if Exercise.objects.filter(name=mod_exe['exercise']).count()==0:
                        with transaction.commit_on_success():
                            kexercise, added = Exercise.objects.get_or_create(name= mod_exe['exercise'],covers="dsa",description= mod_exe['name'],ex_type= mod_exe['type'],streak= mod_exe['threshold'])     
                        #add exercise to module proficiency model
                        if mod_exe['required'] and (kexercise.id not in kmodule.get_required_exercises()):
                            kmodule.add_required_exercise(kexercise.id) #exercise_list += "%s," %kexercise.id
                            kmodule.save()
                    else:
                        with transaction.commit_on_success():
                            kexercise = Exercise.objects.get(name= mod_exe['exercise'])  
                            kexercise.covers="dsa"
                            kexercise.description= mod_exe['name']
                            kexercise.ex_type= mod_exe['type']
                            kexercise.streak= Decimal(mod_exe['threshold'])
                            kexercise.save()
                    if UserData.objects.filter(user=kusername,book=kbook).count()>0:
                        user_data = UserData.objects.get(user=kusername,book=kbook)
                        u_prof = user_data.is_proficient_at(kexercise)  
                    #check student progress -- KA exercises
                    if  UserExercise.objects.filter(user=kusername, exercise=kexercise).count()==1:
                        user_exercise =  UserExercise.objects.get(user=kusername, exercise=kexercise)
                    elif UserExercise.objects.filter(user=kusername, exercise=kexercise).count()>1:
                        user_exercise =UserExercise.objects.filter(user=kusername, exercise=kexercise)[0]
                    else:
                        user_exercise = None
                    if user_exercise is not None:
                        u_prog = user_exercise.progress
                    else:
                        u_prog = 0

                    #response[kexercise.name] = {'proficient':u_prof,'progress':u_prog}
                    #Link exercise to module and books
                    if BookModuleExercise.objects.filter(book = kbook, module = kmodule,exercise=kexercise).count()==0:
                        with transaction.commit_on_success():
                            bme = models.BookModuleExercise(book = kbook, module = kmodule, exercise = kexercise, points =  mod_exe['points'])
                            bme.save()    

                    #exercise proficiency response
                    if BookModuleExercise.objects.filter(book = kbook, exercise=kexercise).count()==0:
                        u_prof = False
                        u_prog = 0
                    response[kexercise.name] = {'proficient':u_prof,'progress':u_prog}
                #check module proficiency
                if  UserModule.objects.filter(user=kusername,book=kbook, module=kmodule).count()==1:
                    user_module = UserModule.objects.get(user=kusername, book=kbook, module=kmodule)
                elif UserModule.objects.filter(user=kusername, book=kbook, module=kmodule).count()>1:
                    user_module = UserModule.objects.filter(user=kusername, book=kbook, module=kmodule)[0]
                else:
                    user_module = None
                if user_module is not None:
                    with transaction.commit_on_success():
                        user_data, created = UserData.objects.get_or_create(user=kusername,book = kbook)
                    update_module_proficiency(user_data, request.POST['module'], None) 
                    #Module proficiency response
                    if BookModuleExercise.objects.filter(book = kbook, module = kmodule).count()==0:
                        response[kmodule.name] = False
                    else: 
                        response[kmodule.name] = user_module.is_proficient_at()    
                return  self.create_response(request, response)
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
            kusername = get_user_by_key(request.POST['key'])       #request.POST['username']:    #request.user:
        if kusername:
            #with transaction.commit_on_success():
            kmodule = Module.objects.get(name= request.POST['module'])
            kbook = Books.objects.get(book_name= request.POST['book'])
                #kusername = User.objects.get(username=request.POST['username'])
            if  UserModule.objects.filter(user=kusername, book=kbook, module=kmodule).count()==1:  
                user_module = UserModule.objects.get(user=kusername, book=kbook, module=kmodule)
            elif UserModule.objects.filter(user=kusername, book=kbook, module=kmodule).count()>1:
                user_module = UserModule.objects.filter(user=kusername, book=kbook, module=kmodule)[0]
            else:
                user_module = None 
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
