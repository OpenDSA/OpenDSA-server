from django.contrib import admin
from opendsa.models import Exercise, UserExercise, UserExerciseLog, UserData, Module, UserModule, \
                              BookModuleExercise, Books, UserBook 
from django.db.models import Q


class BooksAdmin(admin.ModelAdmin):
    pass

admin.site.register(Books, BooksAdmin)

