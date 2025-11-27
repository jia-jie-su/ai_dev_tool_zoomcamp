from django.contrib import admin
from .models import Todo

# Register your models here.

@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ['title', 'due_date', 'resolved', 'created_at']
    list_filter = ['resolved', 'created_at', 'due_date']
    search_fields = ['title', 'description']
    list_editable = ['resolved']
