from django.contrib import admin
from .models import Project, TwitterUser, EmailNotification, Referral
from .methods import methods, send_html_mail
from django.contrib import messages
from django.utils.translation import ngettext
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core import mail
from django.db.models.signals import m2m_changed
from django.core.exceptions import ValidationError
import random



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

#register twitter user model in admin dashboard
@admin.register(TwitterUser)
class TwitterUserAdmin(admin.ModelAdmin):
    """
    Controls model fields to be displayed in the admin dashboard
    """
    def __init__(self, model, admin_site): 
        self.request = None
        super().__init__(model, admin_site)

    def get_queryset(self, request):
        self.request = request      
        return super().get_queryset(request)
    list_display = ['screen_name', 'email', 'account_months', 'followers','referrals']
    actions = ['generate_winner', 'pick_winner']
    list_filter = ( AccountMonthBornListFilter,)
    
    @admin.display(description='referrals')
    def referrals(self,twitter_user):
        id = self.request.GET.get('projects__project_id')
        project = Project.objects.filter(project_id=id).first()
        if project is not None:
            count = Referral.objects.filter(project=project,user=twitter_user.user).count()
        else:
            count = Referral.objects.filter(user=twitter_user.user).count()
        return count

    def register_winner(self,request, project, pks, action):
        """_It _

        Args:
            request (_request_object_): _description_
            project (_query_set_): _The active project that was selected_
            pks (_list_): _Contains user ids of winners to be processed_
            action (_string_): _Indicate if user is random or picked for display message_
        """
        #Gets email notification template from email notification model
        email = EmailNotification.objects.all().first()
        #checks if the project is active
        if project.status:
            projects = Project.objects.all().order_by('-project_date')[0:2]
            #initiate a list to store the winners name
            users_list = ''
            #loop through the winners id and get user object
            for i in pks:
                winner = TwitterUser.objects.filter(twitter_id=i).first()
                #add winner to user relationship model
                project.winners.add(winner)
                #check if email exists
                if email is not None:
                    #replace the placeholders in the email template with the winner name and project name
                    subject = str(email.subject).replace('{{name}}', winner.name)
                    subject = subject.replace('{{project_name}}', project.project_name)
                    #html_message = render_to_string('mail_template.html', {'project': project, 'projects': projects,'name': winner.name, 'email':email})
                    html_message = 'Congratulations ' + winner.name +' you have been selected for the Project ' + str(project.project_name)
                    plain_message = 'strip_tags(html_message)'
                    from_email = 'adeniyi.olaitanhector@yahoo.com'
                    to = winner.email
                    #check if winner has an email address
                    if to is None:
                        self.message_user(request, f'user {winner.screen_name} has no email specified', messages.ERROR)
                    else:
                        send_html_mail(subject,from_email,plain_message, [to], html_message=html_message, fail_silently=True, reply_to=from_email)
                    users_list += winner.screen_name + ','
                    
                else:
                    #if email message is not found, add user to email list
                    users_list += winner.screen_name + ','
            if email is None:
                #if email template is not found, send an error message
                self.message_user(request, f'No email message created, Reselect winners {users_list} to deliver email', messages.ERROR)  
            else:
                #if email template is found, send a success message, display the winners and end the project
                project.status = False
                project.save()
                self.message_user(request, ngettext(
                '%d %s user was successfully picked as a winner for the project.',
                '%d %s users were successfully picked as winners for the project..',
                len(pks) ,) % (len(pks), action) , messages.SUCCESS)
                self.message_user(request, users_list, messages.SUCCESS)
            
        else:
            #if project is not active, send an error message
            self.message_user(request, 'This project has already ended', messages.ERROR)    
    #register random winner method
    @admin.action(description='Generate Random Winner(s)')
    def generate_winner(self, request, queryset):
        """_Get the query set of all selected registered users for a selected project and randomly generate a
            winner queryset which is passed to the register_winner method_

        Args:
            request (_request_object_): _description_
            queryset (_query_set_): _query set of user that registered for a project_
        """
        try:
            #get the twitter_id of user registered for the project
            pks = queryset.values_list('twitter_id', flat=True)
            #get project id from request object
            project_id = (request.GET.get('projects__project_id', ''))
            project = Project.objects.filter(project_id=project_id).first()
            #randomly select winner from the queryset based on project number of winners
            winner_pks = random.sample(sorted(pks), k=project.no_of_winners)
            self.register_winner(request, project, winner_pks, 'Random')
        except ValidationError:
            #if project is not selected, send an error message
            self.message_user(request, 'No project was selected', messages.ERROR)
                
            
            
    @admin.action(description='Pick Winner(s)')
    def pick_winner(self, request, queryset):
        """_Get the query set(winners) of all selected users for a selected project and process the winners
            from the passed queryset which is passed to the register_winner method_

        Args:
            request (_request_object_): _description_
            queryset (_query_set_): _description_
        """
        try:
            #get the twitter_id of user registered for the project
            pks = queryset.values_list('twitter_id', flat=True)
            #get project id from request object
            project_id = (request.GET.get('projects__project_id', ''))
            project = Project.objects.filter(project_id=project_id).first()
            if len(queryset) == project.no_of_winners:
                #if number of winners is equal to the number of winners in the project, process the winners
                self.register_winner(request, project, pks, '')
            elif len(queryset) < project.no_of_winners:
                #if number of winners selected is less than the number of project winners, send an error message
                self.message_user(request, 'No of picked winners less than no of desired winners', messages.ERROR)
            else:
                #if number of winners selected is more than the number of project winners, send an error message
                self.message_user(request, 'No of picked winners more than no of desired winners', messages.ERROR)
        except ValidationError:
            #if project is not selected, send an error message
            self.message_user(request, 'No project was selected', messages.ERROR)
        