"""twittermint URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

from .views import ProjectListView


urlpatterns = [
    path('', views.home, name='home'),
    path('projects/<int:page>/', ProjectListView.as_view(), name='projects'),
    path('project/<uuid:project_id>/', views.project, name='project'),
    path('login/', views.login_user, name='login'),
    path('twitter_login', views.twitter_login, name='twitter_login'),
    path('connect_twitter', views.connect_twitter, name='connect_twitter'),
    path('twitter_logout', views.twitter_logout, name='logout'),
    path('callback', views.callback, name='callback'),
    path('project/<uuid:project_id>/verify',views.verify, name='verify'),
    path('project/<uuid:project_id>/comfirm', views.comfirm, name='comfirm'),
    path('checkfollow/<uuid:project_id>', views.checkfollow, name='checkfollow'),
    path('checklike/<uuid:project_id>', views.checklike, name='checklike'),
    path('checkretweet/<uuid:project_id>', views.checkretweet, name='checkretweet'),
    path('checkcomment/<uuid:project_id>', views.checkcomment, name='checkcomment'),
    path('checkfollowers/<uuid:project_id>', views.checkfollowers, name='checkfollowers'),
    path('checkmonths/<uuid:project_id>', views.checkmonths, name='checkmonths'),
    path('success', views.success, name='success'),
]
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
