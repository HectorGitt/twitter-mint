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

#url patterns
urlpatterns = [
    path('', views.home, name='home'),
    path('projects/<slug:page>', ProjectListView.as_view(), name='projects'),
    path('project/<slug:slug>', views.project, name='project'),
    path('login/', views.login_user, name='login'),
    path('twitter_login', views.twitter_login, name='twitter_login'),
    path('connect_twitter', views.connect_twitter, name='connect_twitter'),
    path('twitter_logout', views.twitter_logout, name='logout'),
    path('callback', views.callback, name='callback'),
    path('project/<slug:slug>/verify',views.verify, name='verify'),
    path('project/<slug:slug>/comfirm', views.comfirm, name='comfirm'),
    path('project/<slug:slug>/check', views.checkactions, name='checkactions'),
    path('checkwalletbalance/<slug:slug>', views.checkwalletbalance, name='checkwalletbalance'),
    path('success', views.success, name='success'),
    path('project/<slug:slug>/referral', views.request_referral_code, name='referral'),
    path('referral', views.verify_referral, name='verify_referral'),
]

#added media upload root directory to url paths
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

#added static files root directory to url paths
urlpatterns += staticfiles_urlpatterns()
