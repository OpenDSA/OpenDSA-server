from django import forms
from exercise.exercise_models import CourseModule

class CourseModuleForm(forms.ModelForm):
    class Meta:
        model = CourseModule
        exclude = ['course_instance','points_to_pass','opening_time','late_submissions_allowed', 'late_submission_deadline']
