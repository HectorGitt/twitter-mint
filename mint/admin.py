from django.contrib import admin
from .models import Project, TwitterUser
from .methods import methods
import random
from django.contrib import messages
from django.utils.translation import ngettext


# Register your models here.
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin, methods):
    list_display = ['project_name', 'no_of_winners', 'project_end_date', 'registered_users', 'view_users','end_project']
    search_fields = ("project_name__startswith", )
    list_filter = ('project_status',)
    
@admin.register(TwitterUser)
class TwitterUserAdmin(admin.ModelAdmin):
    
    list_display = ['screen_name', 'email']
    
    actions = ['generate_winner']


    @admin.action(description='Generate Random Winner(s)')
    def generate_winner(self, request, queryset):
        pks = queryset.values_list('twitter_id', flat=True)
        winners_pks = random.sample(list(pks), k=1)
        print(winners_pks)
        for i in winners_pks:
            winner = queryset.filter(twitter_id=i)
            print(winner)
            project_id = (request.GET.get('projects__project_id', ''))
        self.message_user(request, ngettext(
            '%d Random user was successfully picked as a winner for the project.',
            '%d Random users were successfully picked as winners for the project..',
            len(winners_pks),
        ) % len(winners_pks), messages.SUCCESS)
        

