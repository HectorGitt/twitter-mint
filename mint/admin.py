from django.contrib import admin
from .models import Project, TwitterUser, EmailNotification
from .methods import methods, send_html_mail
import random
from django.contrib import messages
from django.utils.translation import ngettext
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core import mail
from django.db.models.signals import m2m_changed
from django.core.exceptions import ValidationError



# Register your models here.
admin.site.register(EmailNotification)
class TwitterUserInline(admin.TabularInline):
    model = Project.winners.through
    extra = 1
    verbose_name = "Winner"
    verbose_name_plural = "Winners"
    can_delete = True



class AccountMonthBornListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = ('account month')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'months'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('1', ('more than 1 month')),
            ('3', ('more than 3 months')),
            ('6', ('more than 6 months')),
            ('12', ('more than 12 months')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == '1':
            return queryset.filter(
                account_months__gte =1)
        if self.value() == '3':
            return queryset.filter(
                account_months__gte=3)
        if self.value() == '6':
            return queryset.filter(
                account_months__gte=6)
        if self.value() == '12':
            return queryset.filter(
                account_months__gte=12)
            


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
    list_filter = ( AccountMonthBornListFilter,)
    

    def register_winner(self,request, project, pks, action):
        email = EmailNotification.objects.all().first()
        if project.status:
            projects = Project.objects.all().order_by('-project_date')[0:2]
            users_list = ''
            for i in pks:
                winner = TwitterUser.objects.filter(twitter_id=i).first()
                project.winners.add(winner)
                subject = email.subject
                html_message = render_to_string('mail_template.html', {'project': project, 'projects': projects, 'email':email})
                plain_message = 'strip_tags(html_message)'
                from_email = 'adeniyi.olaitanhector@yahoo.com'
                to = winner.email
                send_html_mail(subject,from_email,plain_message, [to], html_message=html_message, fail_silently=True, reply_to=from_email)
                users_list += winner.screen_name + ','
            project.status = False
            project.save()
            self.message_user(request, ngettext(
                '%d %s user was successfully picked as a winner for the project.',
                '%d %s users were successfully picked as winners for the project..',
                len(pks) ,
            ) % (len(pks), action) , messages.SUCCESS)
            self.message_user(request, users_list, messages.SUCCESS)
        else:
            self.message_user(request, 'This project has already ended', messages.ERROR)    
    @admin.action(description='Generate Random Winner(s)')
    def generate_winner(self, request, queryset):
        try:
            pks = queryset.values_list('twitter_id', flat=True)
            project_id = (request.GET.get('projects__project_id', ''))
            project = Project.objects.filter(project_id=project_id).first()
            self.register_winner(request, project, pks, 'Random')
        except ValidationError:
            self.message_user(request, 'No project was selected', messages.ERROR)
                
            
            
    @admin.action(description='Pick Winner(s)')
    def pick_winner(self, request, queryset):
        try:
            pks = queryset.values_list('twitter_id', flat=True)
            project_id = (request.GET.get('projects__project_id', ''))
            project = Project.objects.filter(project_id=project_id).first()
            self.register_winner(request, project, pks, '')
        except ValidationError:
            self.message_user(request, 'No project was selected', messages.ERROR)
        
