# Python
from icalendar import Calendar, Event

# A+
from userprofile.models import UserProfile

# OpenDSA
from opendsa.models import Exercise, UserExercise

# Django
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseForbidden
from course.context import CourseContext


def exercise_summary(request):
    """ 
    Displays a summary of student's exercises.
    """

    exercises = Exercise.objects.all()
    user_exercises = UserExercise.objects.order_by('user', 'exercise').all()

    return render_to_response("teacher_view/exercise_summary.html",
                              {'user_exercises' : user_exercises,
                               'exercises' : exercises})       

    
