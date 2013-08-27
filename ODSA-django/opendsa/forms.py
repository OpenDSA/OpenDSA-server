from django import forms
from django.forms import MultipleChoiceField
from django.forms.widgets import Select, CheckboxSelectMultiple
from opendsa.models import Assignments, Books, Exercise, BookModuleExercise
from django.contrib import admin
from django.utils.safestring import mark_safe

from exercise.exercise_models import  CourseModule
import settings

# Widget
class CSICheckboxSelectMultiple(CheckboxSelectMultiple):
    def value_from_datadict(self, data, files, name):
        # Return a string of comma separated integers since the database, and
        # field expect a string (not a list).
        print data 
        return ','.join(data.getlist(name)).encode('ascii','ignore')

    def render(self, name, value, attrs=None, choices=()):
        # Convert comma separated integer string to a list, since the checkbox
        # rendering code expects a list (not a string)
        if value:
            value.encode('ascii','ignore')
            value = value.split(',')
        js = """
             <script type="text/javascript">
             function fillChapters(course,book){
               $.getJSON('%(path)s' + course + '.json', function(data) {
                 $('#id_assignment_chapter').empty();
                 $.each(data, function(key0, val0) {
                     $.each(val0, function(key1, val1) {
                       $.each(val1, function(key2, val2) {
                         chap = key2.split("-")[0];
                         chap_id = key2.split("-")[1];
                             $('#id_assignment_chapter').append('<option selected="selected" value="'+chap_id+'">'+chap+'</option>');
                       });
                     });
                 });                          
               });
             }
             var selected = [];
             function fillExercises(course,book,chapter){
               $.getJSON('%(path)s' + course + '.json', function(data) {
                     $('#exercises-checkbox').empty();
                     $.each(data, function(key0, val0) {
                       $.each(val0, function(key1, val1) {
                         $.each(val1, function(key2, val2) {
                           var j = 0;
                           if(key2.split("-")[1]==chapter){   
                             $.each(val2, function(key, val) {
                               var checked ="";
                               if(jQuery.inArray(key,selected) != -1){
                                 //checkbox checked
                                 checked ="checked";
                               };
                               $('#exercises-checkbox').append('<li><label for="id_assignment_exercises_'+j+'"><input id="id_assignment_exercises_'+j+'" type="checkbox" value="'+key+'" name="assignment_exercises"'+checked+'>'+val+'</label></li>');
                               j++;
                             });
                           }
                       });
                     });
                 });
               });
             }   
             (function($) {
                $(document).ready(function(){
                   //get selected exercises (if any)
                   $(':checkbox:checked').each(function(i){
                     selected[i] = $(this).val();
                   });
                   var course = $("h1").text().split(" ")[1];
                   //add chapter select box
                   $('#id_assignment_book').after('<p><label for="id_assignment_chapter">Assignment chapter:</label><select id="id_assignment_chapter" name="assignment_chapter"></select></p>');
                   //we only display book associated with the course
                   $.getJSON('%(path)s' + course + '.json', function(data) {
                     $('#id_assignment_book').empty();
                     $.each(data, function(key0, val0) {
                       $.each(val0, function(key, val) {
                         text = key.split("-")[0];
                         value = key.split("-")[1];
                         $('#id_assignment_book').append('<option selected="selected" value="'+value+'">'+text+'</option>');
                           $.each(val, function(key1, val1) {
                             chap = key1.split("-")[0];
                             chap_id = key1.split("-")[1];
                             $('#id_assignment_chapter').append('<option selected="selected" value="'+chap_id+'">'+chap+'</option>'); 
                           });
                       });
                     });
                   });
                   fillExercises( course, $('#id_assignment_book').val(), $('#id_assignment_chapter').val());
                   $('#id_assignment_book').change(function(){
                     fillChapters( course, $('#id_assignment_book').val());
                   });
                   $('#id_assignment_chapter').change(function(){
                     fillExercises( course, $('#id_assignment_book').val(), $('#id_assignment_chapter').val());
                   });

                })
             })(jQuery);
             </script>
             """
        js = js % {"path": settings.MEDIA_URL }
        output = super(CSICheckboxSelectMultiple, self).render(
            name, value, attrs=attrs, choices=choices
        )
        output = output.replace('<ul>','<ul id= "exercises-checkbox">')
        output += js
        return mark_safe(output)

# Form field
class CSIMultipleChoiceField(MultipleChoiceField):
    widget = CSICheckboxSelectMultiple

    # Value is stored and retrieved as a string of comma separated
    # integers. We don't want to do processing to convert the value to
    # a list like the normal MultipleChoiceField does.
    def to_python(self, value):
        return value

    def validate(self, value):
        # If we have a value, then we know it is a string of comma separated
        # integers. To use the MultipleChoiceField validator, we first have
        # to convert the value to a list.
        if value:
            value.encode('ascii','ignore')
            value = value.split(',')
        super(CSIMultipleChoiceField, self).validate(value)


def exercises_in_book(book=None):
    a_exe = Exercise.objects.all()
    result = ()
    for exe in a_exe:
       if not exe.name.isspace():
          result += ((exe.id,exe.name),)
    return result


class AssignmentForm(forms.ModelForm):
    assignment_exercises = CSIMultipleChoiceField( choices =exercises_in_book(), # settings.exercises_in_book, #all_exercises(),
        required=False,
    )

    class Meta:
        model = Assignments 

class AssignmentAdmin(admin.ModelAdmin):
    form = AssignmentForm


admin.site.register(Assignments, AssignmentAdmin)
