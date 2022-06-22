from django.contrib import admin
from .models import Project, TwitterUser
from .methods import methods


# Register your models here.
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin, methods):
    list_display = ['project_name', 'no_of_winners', 'project_end_date', 'registered_users', 'view_registered_users','generate_winner']
    
admin.site.register(TwitterUser)

