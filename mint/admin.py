from django.contrib import admin
from .models import Project, TwitterUser
from .methods import methods, send_html_mail
import random
from django.contrib import messages
from django.utils.translation import ngettext
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core import mail
from django.db.models.signals import m2m_changed



# Register your models here.
class TwitterUserInline(admin.TabularInline):
    model = Project.winners.through
    extra = 1
    verbose_name = "Winner"
    verbose_name_plural = "Winners"
    can_delete = True


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin, methods):
    list_display = ['project_name', 'no_of_winners', 'project_end_date', 'registered_users', 'view_users','end_project']
    search_fields = ("project_name__startswith", )
    list_filter = ('status',)
    inlines = [TwitterUserInline]
    
def winners_changed(sender,**kwargs):
    print('added winner')
m2m_changed.connect(winners_changed, sender=Project.winners,dispatch_uid='uuid.uuid4')
   
@admin.register(TwitterUser)
class TwitterUserAdmin(admin.ModelAdmin):
    
    list_display = ['screen_name', 'email', 'account_months', 'followers']
    actions = ['generate_winner', 'pick_winner']
    list_filter = ('account_months',)
    


    @admin.action(description='Generate Random Winner(s)')
    def generate_winner(self, request, queryset):
        pks = queryset.values_list('twitter_id', flat=True)
        project_id = (request.GET.get('projects__project_id', ''))
        project = Project.objects.filter(project_id=project_id).first()
        projects = Project.objects.all().order_by('-project_date')[0:2]
        if project.status:
            users_list = ''
            winners_pks = random.sample(list(pks), k=1)
            for i in winners_pks:
                winner = TwitterUser.objects.filter(twitter_id=i).first()
                project.winners.add(winner)
                subject = 'Congratulations, You have been selected'
                html_message = render_to_string('mail_template.html', {'project': project, 'projects': projects})
                plain_message = 'strip_tags(html_message)'
                from_email = 'adeniyi.olaitanhector@yahoo.com'
                to = winner.email
                send_html_mail(subject,from_email,plain_message, [to], html_message=html_message, fail_silently=True, reply_to=from_email)
                users_list += winner.screen_name + ','
            project.status = False
            project.save()
            self.message_user(request, ngettext(
            '%d Random user was successfully picked as a winner for the project.',
            '%d Random users were successfully picked as winners for the project..',
            len(winners_pks), ) % len(winners_pks), messages.SUCCESS)
            self.message_user(request, users_list, messages.SUCCESS)
        else:
            self.message_user(request, 'This project has already ended', messages.ERROR)

            
        
        
    @admin.action(description='Pick Winner(s)')
    def pick_winner(self, request, queryset):
        pks = queryset.values_list('twitter_id', flat=True)
        project_id = (request.GET.get('projects__project_id', ''))
        project = Project.objects.filter(project_id=project_id).first()
        projects = Project.objects.all().order_by('-project_date')[0:2]
        if project.status:
            users_list = ''
            for i in pks:
                winner = TwitterUser.objects.filter(twitter_id=i).first()
                project.winners.add(winner)
                subject = 'Congratulations, You have been selected'
                html_message = render_to_string('mail_template.html', {'project': project, 'projects': projects})
                plain_message = 'strip_tags(html_message)'
                from_email = 'adeniyi.olaitanhector@yahoo.com'
                to = winner.email
                send_html_mail(subject,from_email,plain_message, [to], html_message=html_message, fail_silently=True, reply_to=from_email)
                users_list += winner.screen_name + ','
            project.status = False
            project.save()
            self.message_user(request, ngettext(
                '%d user was successfully picked as a winner for the project.',
                '%d users were successfully picked as winners for the project..',
                len(pks) ,
            ) % (len(pks)) , messages.SUCCESS)
            self.message_user(request, users_list, messages.SUCCESS)
        else:
            self.message_user(request, 'This project has already ended', messages.ERROR)

