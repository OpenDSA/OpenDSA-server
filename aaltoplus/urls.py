# A+
from views import login, home, verify_credentials
from oauth_provider.views import protected_resource_example
from opendsa.views import exercise_summary, module_list, export_csv, progress_summary
from opendsa.developerview import exercises_stat, exercises_bargraph, exercises_time, student_list, student_exercise, exercise_list, exercise_detail, timeline_sum, timeline_detail
# Django
from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    # OAuth plus
    url(r'^oauth/', include('oauth_provider.urls')),
    url(r'^oauth/photo/$', protected_resource_example, name='oauth_example'),
    
    # A view for returning credentials through OAuth authentication
    url(r'^account/verify_credentials.json$', verify_credentials),

    # OpenDSA
    url(r'^teacher_view/$', exercise_summary),
    url(r'^teacher_view/exercise_summary/$', exercise_summary),       
    url(r'^teacher_view/export_csv/$', export_csv),
    url(r'^teacher_view/progress_summary/$', progress_summary),                   
    url(r'^student_view/', module_list),
    url(r'^developer_view/exercises_stat/$', exercises_stat),
    url(r'^developer_view/exercises_bargraph/$', exercises_bargraph),
    url(r'^developer_view/exercises_time/$', exercises_time),
    url(r'^developer_view/$', student_list),  
    url(r'^developer_view/student_exercise/(?P<student>[\w]+)/$', student_exercise),
    url(r'^developer_view/exercise_list/(?P<student>[\w]+)/(?P<module>[\w]+)/$', exercise_list),      
    url(r'^developer_view/exercise_detail/(?P<student>[\w]+)/(?P<exercise>[\w]+)/$', exercise_detail),
    url(r'^developer_view/timeline_sum/(?P<student>[\w]+)/$', timeline_sum),
    url(r'^developer_view/timeline_detail/(?P<student>[\w]+)/(?P<module>[\w]+)/(?P<year>[\w]+)/(?P<month>[\w]+)/(?P<day>[\w]+)/$', timeline_detail),

    # A+
    (r'^$', home),
                       
    (r'^exercise/', include('exercise.urls')),
    (r'^course/', include('course.urls')),
    (r'^api/', include('api_urls')),
    (r'^userprofile/', include('userprofile.urls')),
    (r'^apps/', include('apps.urls')),
    
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    # Shibboleth
    (r'^shibboleth/', include('django_shibboleth.urls')),
    
    #registration
    (r'^accounts/', include('registration.backends.simple.urls')),

    # Django:
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/login/$', login),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'aaltoplus/logout.html'}),
)

urlpatterns += patterns('',
    (r'^comments/', include('django.contrib.comments.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )
