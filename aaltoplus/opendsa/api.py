# Tastypie
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authentication import Authentication, OAuthAuthentication
from tastypie.authorization import DjangoAuthorization, ReadOnlyAuthorization, Authorization 
from tastypie import fields
from tastypie.utils import trailing_slash
from tastypie.serializers import Serializer
from tastypie.http import HttpUnauthorized, HttpForbidden  

# ODSA 
from opendsa.models import Exercise, UserExercise, UserExerciseLog, UserData, Module, Feedback    
from django.conf.urls.defaults import patterns, url
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout 
from django.contrib.auth.models import User
from django.utils import simplejson 
from django.contrib.sessions.models import Session
from django.http import HttpResponse
import jsonpickle  

from exercises import attempt_problem, make_wrong_attempt, get_pe_name_from_referer, log_button_action, attempt_problem_pe 



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
        if 'sessionid' in request.COOKIES:
            s = Session.objects.get(pk=request.COOKIES['sessionid'])
            if '_auth_user_id' in s.get_decoded():
                u = User.objects.get(id=s.get_decoded()['_auth_user_id'])
                request.user = u
                return self.create_response(request, {'success': 'is_authenticated!'}) 
 
        #if request.user.is_authenticated():
        #    return self.create_response(request, {'success': 'is_authenticated!'}) 
        self.method_check(request, allowed=['post'])
        username = request.POST['username']                   
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return self.create_response(request, {'success': True})
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
        authentication  = Authentication()
        authorization   = ReadOnlyAuthorization()
        filtering = {
            'name': ('exact',), 
        }
 
class FeedbackResource(ModelResource): 
      
    def determine_format(self, request):
        return "application/json"

    class Meta:
        queryset        = Feedback.objects.all()
        resource_name   = 'feedback'
        excludes        = []

        allowed_methods = ['get','post']
        authentication  = Authentication()
        authorization   = Authorization()   #ReadOnlyAuthorization()  

    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/feedback%s$" %(self._meta.resource_name, trailing_slash()),self.wrap_view('logfeedback'), name="api_logfb"),
    ]
#    def logfeedback(self, request, **kwargs):
#            print 'toto'    #request.META['REMOTE_ADDR']   
#            feedback, created = Feedback.objects.create(name=kusername)
#                    request.META['REMOTE_ADDR'],
#                 if correct:
#                    return  self.create_response(request, user_exercise)
#                 else:
#                    return  self.create_response(request, {'error': 'attempt not logged'})
#        return self.create_response(request, {'error': 'unauthorized action'})




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
        ]

    def listlogs():
        return UserExercise.objects.all() 

    def logavbutton(self, request, **kwargs):
        if request.POST['username']:   
            action =   request.POST['actions']
            actions = simplejson.loads(action)
            pe_name = get_pe_name_from_referer(request.META['HTTP_REFERER'])
            number_logs = 0
            for act in actions:
               #kexercise = Exercise.objects.get(name = act['av'])  
               #if kexercise:
               #else:
               if 'score[total]' in request.POST:
                  streak = request.POST['score[total]'] 
               else:
                  streak = 0 

               if  len(Exercise.objects.filter(name= act['av']))==1:
                   kexercise =  Exercise.objects.get(name= act['av'])
                   kexercise.streak= streak
                   kexercise.save()
               else:
                   kexercise = Exercise(name = act['av'], streak=streak)
                   kexercise.save()  #, result = Exercise.objects.get_or_create(name = act['av'], streak=streak) #, author='',ex_type='', streak=1)     
               kusername = User.objects.get(username=request.POST['username'])
               user_data, created = UserData.objects.get_or_create(user=kusername)
               module = Module.objects.get(short_display_name=act['module_name']) #   'Shellsort') 
               if kexercise:
                 user_button,correct = log_button_action(
                    kusername,  #kusername,
                    kexercise,
                    module,
                    act['type'],
                    'description', 
                    act['tstamp'],
                    request.META['REMOTE_ADDR'],
                    )
                 if correct:
                    number_logs += 1 #return  self.create_response(request, user_button)
            
            if number_logs == len(actions):
                return  self.create_response(request,  {'success':True, 'message': 'all button action logged'})
            else:
                    return  self.create_response(request, {'success':False, 'error': 'not all button action logged'})
        return self.create_response(request, {'success':False, 'error': 'unauthorized action'})


    def logpeexercise(self, request, **kwargs):
        print request 
        if request.POST['username']:    
            av = request.POST['av']
            kexercise =  Exercise.objects.get(name= av) 
            if kexercise:
                kexercise.ex_type= request.POST['type'] 
                kexercise.streak= request.POST['score[total]']
                kexercise.covers="dsa"
                kexercise.save()                 
            else: 
                kexercise, inserted = Exercise.objects.get_or_create(name= av,covers="dsa",description="",ex_type= request.POST['type'],streak= request.POST['score[total]']) #streak = max number of correct steps
   
            kusername = User.objects.get(username=request.POST['username'])
            if kusername and kexercise:
                user_exercise, exe_created = UserExercise.objects.get_or_create(user=kusername, exercise=kexercise, streak=0) 
            user_data, created = UserData.objects.get_or_create(user=kusername)
            if user_exercise:
                    user_exercise,correct = attempt_problem_pe(
                       user_data,  
                       user_exercise,
                       request.POST['attempt'],
                       1, #request.POST['complete'],
                       int(request.POST['total_time']),
                       request.POST['score[fix]'],
                       int(request.POST['score[undo]']),
                       int(request.POST['score[correct]']),
                       int(request.POST['score[student]']),
                       int(request.POST['score[total]']),
                       request.META['REMOTE_ADDR'],
                       )
                    return  self.create_response(request, {'success': True, 'proficient': correct})   
            else:
                       return  self.create_response(request, {'error': 'attempt not logged'})
        return self.create_response(request, {'error': 'unauthorized action'})



 
    def logexercise(self, request, **kwargs):
        if request.POST['user']:    #request.user:
            kexercise = Exercise.objects.get(name= request.POST['sha1'])  
            kusername = User.objects.get(username=request.POST['user']) 
            user_exercise, exe_created = UserExercise.objects.get_or_create(user=kusername, exercise=kexercise) 
            user_data, created = UserData.objects.get_or_create(user=kusername) 
            if user_exercise:
                 user_exercise,correct = attempt_problem(
                    user_data,  #kusername,
                    user_exercise,
                    request.POST['attempt_number'],
                    request.POST['complete'],
                    request.POST['count_hints'],
                    int(request.POST['time_taken']),
                    request.META['REMOTE_ADDR'],
                    )
                 if correct:
                    print jsonpickle.encode(user_exercise)
                    return  self.create_response(request, jsonpickle.encode(user_exercise) )           #    user_exercise) 
                 else:
                    return  self.create_response(request, {'error': 'attempt not logged'})   
        return self.create_response(request, {'error': 'unauthorized action'})
 
    def logexercisehint(self, request, **kwargs):

        if request.POST['user']:    #request.user:
            kexercise = Exercise.objects.get(name= request.POST['sha1'])
            kusername = User.objects.get(username=request.POST['user'])
            user_exercise, exe_created = UserExercise.objects.get_or_create(user=kusername, exercise=kexercise)
            user_data, created = UserData.objects.get_or_create(user=kusername)
            if user_exercise:
                 user_exercise,correct = attempt_problem(
                    user_data,  #kusername,
                    user_exercise,
                    request.POST['attempt_number'],
                    request.POST['complete'],
                    request.POST['count_hints'],
                    int(request.POST['time_taken']),
                    request.META['REMOTE_ADDR'],
                    )
                 if correct:
                    return  self.create_response(request, user_exercise)
                 else:
                    return  self.create_response(request, {'error': 'attempt not logged'})
        return self.create_response(request, {'error': 'unauthorized action'})


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
        ]
     
    def isproficient(self, request, **kwargs):

        if request.POST['username']:    #request.user:
            kexercise = Exercise.objects.get(name= request.POST['exercise'])
            kusername = User.objects.get(username=request.POST['username'])
            user_data = UserData.objects.get(user=kusername)
            if kexercise:
                return self.create_response(request, {'proficient': user_data.is_proficient_at(kexercise)}) 
            self.create_response(request, {'proficient': 'false'}) 
        return self.create_response(request, {'proficient': 'false'})










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
