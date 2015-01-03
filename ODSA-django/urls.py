# A+
from views import login,  verify_credentials #home
from oauth_provider.views import protected_resource_example

from opendsa.views import exercise_summary, class_summary, daily_summary, all_statistics, widget_data, home, add_or_edit_assignment, class_students, student_management, rebuild_book_assignments, merged_book, delete_assignment, mobile_devices, prof_statistics, student_work, students_data_home, create_accounts, upload_accounts, glossary_module_data, glossary_module_data_home, get_class_activity, get_all_activity, interactions_data_home, interactions_data, interactionsts_data, interactionsts_data_home
from opendsa.developerview import exercises_stat, exercises_bargraph, exercises_time, student_list, student_exercise, exercise_list, exercise_detail, non_required_exercise_use, total_module_time, slideshow_cheating, work_order, skipping_text, slideshow_stats, time_required, cheating_exercises, work_distribution, student_list_home  
# Django
from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
from django.conf.urls import patterns, include, url

admin.autodiscover()

urlpatterns = patterns('',
    # OAuth plus
    url(r'^oauth/', include('oauth_provider.urls')),
    url(r'^oauth/photo/$', protected_resource_example, name='oauth_example'),

    # A view for returning credentials through OAuth authentication
    url(r'^account/verify_credentials.json$', verify_credentials),

    # OpenDSA
    url(r'^assignments/(?P<course_module_id>[\w]+)/$',add_or_edit_assignment),
    url(r'^assignments/del/(?P<module_id>[\w]+)/$',delete_assignment),
    url(r'^teacher_view/rebuild/(?P<module_id>[\w]+)/$',rebuild_book_assignments),
    url(r'^students/(\d+)$',student_management),
    url(r'^teacher_view/(?P<course_module_id>[\w]+)/$',class_students),
    url(r'^teacher_view/(?P<book>[\w]+)/(?P<course>[\w]+)/$', exercise_summary),
    url(r'^teacher_view/all/(?P<book>[\w]+)/(?P<course>[\w]+)/$', class_summary),
    url(r'^teacher_v/assignments/(?P<module_id>\d+)/$', get_class_activity),
    url(r'^teacher_v/exercises/(?P<module_id>\d+)/$', get_all_activity),
    url(r'^teacher_view/mb/(?P<book>[\w]+)/(?P<book1>[\w]+)/$', merged_book),
    url(r'^students/accounts/(?P<module_id>[\w]+)/$', create_accounts),
    url(r'^students/upload/(?P<module_id>[\w]+)/$', upload_accounts),
#    url(r'^student_view/(?P<student>[\w]+)/(?P<book>[\w]+)/$', module_list),
    url(r'^developer_view/exercises_stat/$', exercises_stat),
    url(r'^developer_view/daily_stat/$', daily_summary),
    url(r'^developer_view/daily_stat/(?P<course_instance>[\w]+)/$', daily_summary),
    url(r'^developer_view/stats/$', all_statistics),
    url(r'^developer_view/prof_data/$', prof_statistics),
    url(r'^developer_view/widget/$', widget_data),
    url(r'^developer_view/mobility/$', mobile_devices),
    url(r'^developer_view/non_required_exercise_use/$', non_required_exercise_use),
    url(r'^developer_view/slideshow_cheating/(?P<student>[\w]+)/$', slideshow_cheating),
    url(r'^developer_view/work_distribution/(?P<book>[\w]+)/(?P<bin_size>[\w]+)$', work_distribution),
    url(r'^developer_view/work_order/(?P<book>[\w]+)/$', work_order),
    url(r'^developer_view/skipping_text/(?P<book>[\w]+)/$', skipping_text),
    url(r'^developer_view/slideshow_stats/(?P<book>[\w]+)/$', slideshow_stats),
    url(r'^developer_view/time_required/(?P<book>[\w]+)/$', time_required),
    url(r'^developer_view/cheating_exercises/(?P<book>[\w]+)/$', cheating_exercises),
    url(r'^developer_view/total_module_time/$', total_module_time),
    url(r'^developer_view/exercises_bargraph/$', exercises_bargraph),
    url(r'^developer_view/exercises_time/$', exercises_time),
    url(r'^developer_view/students/(?P<course_instance>[\w]+)/$', student_list_home),
    url(r'^developer_view/students/$', student_list_home),
    url(r'^developer_view/glossary/(?P<course_instance>[\w]+)/$', glossary_module_data),
    url(r'^developer_view/glossary/$', glossary_module_data),
    url(r'^developer_view/glossary_terms/$', glossary_module_data_home),    
    url(r'^developer_view/interactions/(?P<course_instance>[\w]+)/$', interactions_data),
    url(r'^developer_view/interactions/$', interactions_data),
    url(r'^developer_view/interactions_home/$', interactions_data_home),
    url(r'^developer_view/interactionstime/(?P<course_instance>[\w]+)/$', interactionsts_data),
    url(r'^developer_view/interactionstime/$', interactionsts_data),
    url(r'^developer_view/interactionstime_home/$', interactionsts_data_home),
    url(r'^developer_view/students_stat/(?P<course_instance>[\w]+)/$', student_work),    
    url(r'^developer_view/students_stat/$', student_work),
    url(r'^developer_view/studs_stat/$', students_data_home),
    url(r'^developer_view/students/(?P<course>[\w]+)/student_exercise/(?P<student>[\w]+)/$', student_exercise),
    #url(r'^developer_view/student_exercise/(?P<student>[\w]+)/$', student_exercise),
    url(r'^developer_view/exercise_list/(?P<student>[\w]+)/$', exercise_list),
    url(r'^developer_view/exercise_detail/(?P<student>[\w]+)/(?P<exercise>[\w]+)/$', exercise_detail),
    (r'^activity/', include('actstream.urls')),

    #Haystack
    #(r'^search/', include('haystack.urls')),

    #url(r'^developer_view/timeline_sum/(?P<student>[\w]+)/$', timeline_sum),
    #url(r'^developer_view/timeline_detail/(?P<student>[\w]+)/(?P<module>[\w]+)/(?P<year>[\w]+)/(?P<month>[\w]+)/(?P<day>[\w]+)/$', timeline_detail),

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
