from django.contrib import admin
from .models import Level, Subject

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'order')
    list_editable = ('order',)
    list_filter = ('category',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_academic')