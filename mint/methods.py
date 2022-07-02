from .models import Project
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
class methods():
    def __init__(self):
        pass
    def registered_users(self, obj):
        project = Project.objects.filter(project_id=obj.project_id).first()
        count = project.registered.all().count()
        return count
    def view_users(self, obj):
        url = (
            reverse("admin:mint_twitteruser_changelist")
            + "?"
            + urlencode({"projects__project_id": f"{obj.project_id}"})
        )
        return format_html('<a class="btn btn-success" href="{}">Check Registered Users</a>', url)
        
    def end_project(self, obj):
        project = Project.objects.filter(project_id=obj.project_id).first()
        registered = project.registered.all()
        url = (
            reverse("admin:mint_twitteruser_changelist")
            + "?"
            + urlencode({"projects__project_id": f"{obj.project_id}"})
        )
        ''' url2 = (
            reverse("admin:mint_project_changelist")
            + "?"
            + urlencode({"twitteruser__project_id": f"{obj.project_id}"})
        ) '''
        if obj.status:
            return format_html('<a class="btn btn-success" href="{}">End</a>', url)
        else:
            return format_html('<a class=" disabled btn btn-success" href="{}">Ended</a>', url)
        
