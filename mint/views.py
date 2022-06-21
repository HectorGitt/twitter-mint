
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .decorators import twitter_login_required
from .models import TwitterAuthToken, TwitterUser
from .authorization import create_update_user_from_twitter, check_token_still_valid
from twitter_api.twitter_api import TwitterAPI
from .models import Project
from django.http import HttpResponse


# Create your views here.
def home(request):
    projects_all = Project.objects.all().order_by('-project_date')
    
    return render(request, 'mint/home.html', {'context': projects_all})
def project(request, project_id):
    username = request.user
    project = Project.objects.filter(project_id=project_id).first()
    registered_count = project.registered.all().count()
    if username.is_authenticated:
        try:
            twitter_user = TwitterUser.objects.filter(screen_name=username).first()
            
            registered = twitter_user.projects.all().filter(project_id=project_id).first()
        except:
            return HttpResponse('You are logged in as a Staff and not a twitter user!!!')
        
    else:
        registered = False
    return render(request, 'mint/project.html', {'context': project, 'registered': registered, 'count': registered_count})
def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return render(request, 'mint/login.html')
def twitter_login(request):
    twitter_api = TwitterAPI()
    url, oauth_token, oauth_token_secret = twitter_api.twitter_login()
    if url is None or url == '':
        messages.add_message(request, messages.ERROR, 'Unable to login. Please try again.')
        return render(request, 'authorization/error_page.html')
    else:
        twitter_auth_token = TwitterAuthToken.objects.filter(oauth_token=oauth_token).first()
        if twitter_auth_token is None:
            twitter_auth_token = TwitterAuthToken(oauth_token=oauth_token, oauth_token_secret=oauth_token_secret)
            twitter_auth_token.save()
        else:
            twitter_auth_token.oauth_token_secret = oauth_token_secret
            twitter_auth_token.save()
        return redirect(url) 
def callback(request):
    if 'denied' in request.GET:
        messages.add_message(request, messages.ERROR, 'Unable to login or login canceled. Please try again.')
        return render(request, 'mint/error_page.html')
    twitter_api = TwitterAPI()
    oauth_verifier = request.GET.get('oauth_verifier')
    oauth_token = request.GET.get('oauth_token')
    twitter_auth_token = TwitterAuthToken.objects.filter(oauth_token=oauth_token).first()
    if twitter_auth_token is not None:
        access_token, access_token_secret = twitter_api.twitter_callback(oauth_verifier, oauth_token, twitter_auth_token.oauth_token_secret)
        if access_token is not None and access_token_secret is not None:
            twitter_auth_token.oauth_token = access_token
            twitter_auth_token.oauth_token_secret = access_token_secret
            twitter_auth_token.save()
            # Create user
            info = twitter_api.get_me(access_token, access_token_secret)
            if info is not None:
                twitter_user_new = TwitterUser(twitter_id=info[0]['id'], screen_name=info[0]['username'], name=info[0]['name'], profile_image_url=info[0]['profile_image_url'])
                twitter_user_new.twitter_oauth_token = twitter_auth_token
                user, twitter_user = create_update_user_from_twitter(twitter_user_new)
                if user is not None:
                    login(request, user)
                    return redirect('home')
            else:
                messages.add_message(request, messages.ERROR, 'Unable to get profile details. Please try again.')
                return render(request, 'mint/error_page.html')
        else:
            messages.add_message(request, messages.ERROR, 'Unable to get access token. Please try again.')
            return render(request, 'mint/error_page.html')
    else:
        messages.add_message(request, messages.ERROR, 'Unable to retrieve access token. Please try again.')
        return render(request, 'mint/error_page.html')

@login_required
def twitter_logout(request):
    logout(request)
    return redirect('home')

@login_required
def verify(request, project_id):
    username = request.user
    twitter_user = TwitterUser.objects.filter(screen_name=username).first()
    
    if request.method == 'POST':
        form_email = request.POST.get('email')
        print(twitter_user)
        print(form_email)
        twitter_user.email = str(form_email)
        twitter_user.save()
        return redirect('home')
    else:
        email = twitter_user.email
        if email is None or email == '':
            return render (request, 'mint/verify.html')
        else:
            return redirect('comfirm', project_id)
        
@login_required
def comfirm(request, project_id):
    project = Project.objects.filter(project_id=project_id).first()
    username = request.user
    try:
        twitter_user = TwitterUser.objects.filter(screen_name=username).first()
        oauth_token = str(twitter_user.twitter_oauth_token)
        oauth_token_secret = str(TwitterAuthToken.objects.filter(oauth_token=oauth_token).first().oauth_token_secret)
        twitter_api = TwitterAPI()
        tweet_url = project.twitter_like_link
        profile_url = project.twitter_follow_link
        retweet_url = project.twitter_retweet_link
        
        
        if project.twitter_like:
            tweet_id = tweet_url.split('/')[-1].split('?')[0]
            check_comment = twitter_api.check_comment(oauth_token, oauth_token_secret, tweet_id)
            print(check_comment)
            like_state = twitter_api.check_like(oauth_token, oauth_token_secret, tweet_id)
        else:
            like_state = True
        if project.twitter_retweet:
            retweet_id = retweet_url.split('/')[-1].split('?')[0]
            retweet_state = twitter_api.check_retweet(oauth_token, oauth_token_secret, retweet_id)
        else:
            retweet_state = True
        if project.twitter_follow:
            screen_name = profile_url.split('/')[-1].split('?')[0]
            follow_state = twitter_api.check_follow(oauth_token, oauth_token_secret, screen_name)
        else:
            follow_state = True

        if like_state and retweet_state and follow_state:
            project = Project.objects.filter(project_id=project_id).first()
            twitter_user.projects.add(project)
            return render(request, 'mint/comfirm.html', {'context': project})
        else:
            context = {'context': project, 'like_state': like_state, 'retweet_state': retweet_state, 'follow_state': follow_state}
            return render(request, 'mint/error_page.html', context)
        
    except AttributeError: 
        return HttpResponse('You are logged in as a Staff and not a twitter user!!!')