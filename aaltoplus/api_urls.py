from django.conf.urls.defaults import *
from tastypie.api import Api
from course.api import CourseResource, CourseInstanceResource
from userprofile.api import UserProfileResource
from exercise.api import ExerciseResource, CourseModuleResource, SubmissionResource, \
    LearningObjectResource
from opendsa.api import ExerciseResource, UserexerciseResource, ProblemlogResource, UserResource  


api = Api(api_name='v1')
api.register(CourseResource())
api.register(CourseInstanceResource())
api.register(UserProfileResource())
api.register(ExerciseResource())
api.register(CourseModuleResource())
api.register(SubmissionResource())
api.register(LearningObjectResource())
api.register(ExerciseResource())
api.register(UserexerciseResource())
api.register(ProblemlogResource())
api.register(UserResource())

urlpatterns = patterns('',
    (r'^', include(api.urls)),
)
