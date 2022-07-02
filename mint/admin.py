from django.contrib import admin
from .models import Project, TwitterUser
from .methods import methods
import random
from django.contrib import messages
from django.utils.translation import ngettext
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core import mail



# Register your models here.
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin, methods):
    list_display = ['project_name', 'no_of_winners', 'project_end_date', 'registered_users', 'view_users','end_project']
    search_fields = ("project_name__startswith", )
    list_filter = ('status',)
    
@admin.register(TwitterUser)
class TwitterUserAdmin(admin.ModelAdmin):
    
    list_display = ['screen_name', 'email']
    
    actions = ['generate_winner']


    @admin.action(description='Generate Random Winner(s)')
    def generate_winner(self, request, queryset):
        pks = queryset.values_list('twitter_id', flat=True)
        winners_pks = random.sample(list(pks), k=1)
        for i in winners_pks:
            winner = TwitterUser.objects.filter(twitter_id=i).first()
            project_id = (request.GET.get('projects__project_id', ''))
            project = Project.objects.filter(project_id=project_id).first()
            project.winners.add(winner)
            project.status = False
            #project.save()
            subject = 'Subject'
            html_message = render_to_string('mail_template.html', {'context': 'values'})
            plain_message = strip_tags(html_message)
            from_email = 'From <adeniyi.olaitanhector@yahoo.com>'
            to = 'adeniyi.olaitanhector@outlook.com'
            mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message, fail_silently=False)


            
        self.message_user(request, ngettext(
            '%d Random user was successfully picked as a winner for the project.',
            '%d Random users were successfully picked as winners for the project..',
            len(winners_pks),
        ) % len(winners_pks), messages.SUCCESS)
        


