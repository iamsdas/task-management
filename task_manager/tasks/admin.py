from django.contrib import admin

# Register your models here.

from .models import Task

admin.sites.site.register(Task)
