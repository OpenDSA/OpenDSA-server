# Tastypie
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authentication import Authentication, OAuthAuthentication
from tastypie.authorization import DjangoAuthorization, ReadOnlyAuthorization
from tastypie import fields
from tastypie.utils import trailing_slash
from tastypie.serializers import Serializer
from tastypie.http import HttpUnauthorized, HttpForbidden  

# ODSA 
from opendsa.models import Exercise, UserExercise, ProblemLog 
from django.conf.urls.defaults import patterns, url
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout 
from django.contrib.auth.models import User
from django.utils import simplejson 
from django.contrib.sessions.models import Session

from exercises import attempt_problem, make_wrong_attempt



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
        
        # TODO: In this version, only GET requests are accepted and no 
        # permissions are checked.
        allowed_methods = ['get','post']
        authentication  = Authentication()
        authorization   = ReadOnlyAuthorization()
    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/attempt%s$" %(self._meta.resource_name, trailing_slash()),self.wrap_view('logexercise'), name="api_logexe"),
        ]
    def logexercise(self, request, **kwargs):

        if request.POST['user']:    #request.user:
            kexercise = Exercise.objects.get(name= request.POST['sha1'])  
            kusername = User.objects.get(username=request.POST['user']) 
            print '---'
            print request
            print kusername.id   
            print '---'
            user_exercise = UserExercise.objects.get_or_create(user=kusername, exercise=kexercise)  
            if user_exercise:
                 review_mode = request.POST['review_mode'] 
                 problem_number = 1  
                 user_exercise = attempt_problem(
                    kusername,
                    user_exercise,
                    problem_number,
                    request.POST['attempt_number'],
                    request.POST['attempt_content'],
                    request.POST['sha1'],
                    request.POST['seed'],
                    request.POST['complete'],
                    request.POST['count_hints'],
                    int(request.POST['time_taken']),
                    review_mode,
                    0, #request.POST['non_summative'],
                    request.POST['problem_type'],
                    request.META['REMOTE_ADDR'],
                    )
                 return user_exercise
        return 'unauthorize response' 
 
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
        queryset        = ProblemLog.objects.all()
        resource_name   = 'problemlog'
        excludes        = []

        # TODO: In this version, only GET requests are accepted and no
        # permissions are checked.
        allowed_methods = ['get']
        authentication  = Authentication()
        authorization   = ReadOnlyAuthorization()
