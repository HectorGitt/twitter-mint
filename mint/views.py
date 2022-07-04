
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
import json



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
    if project.twitter_tweet_link:
        tweet_id = project.twitter_tweet_id
    else: tweet_id = None
    return render(request, 'mint/project.html', {'context': project, 'registered': registered, 'count': registered_count, 'tweet_id': tweet_id})

def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    else:
        request.session['next'] = request.GET.get('next', '/')
        return render(request, 'mint/login.html', {'next': next})
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
                    try:
                        return redirect(request.session['next'])
                    except:
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

def connect_twitter(request):
    request.session['next'] = request.GET.get('next', '/')
    return redirect('twitter_login')
    

@login_required
def verify(request, project_id):
    username = request.user
    twitter_user = TwitterUser.objects.filter(screen_name=username).first()
    
    if request.method == 'POST':
        form_email = request.POST.get('email')
        wallet_id = request.POST.get('wallet_id')
        twitter_user.email = str(form_email)
        twitter_user.wallet_id = str(wallet_id)
        twitter_user.save()
        return redirect('comfirm', project_id)
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
        tweet_url = project.twitter_tweet_link
        tweet_id = int(tweet_url.split('/')[-1].split('?')[0])
        
        registered = twitter_user.projects.all().filter(project_id=project_id).first()
        if registered is not None:
            return HttpResponse('You registered already!!!')
        else:
            if project.twitter_like:
                like_state = twitter_api.check_like(oauth_token, oauth_token_secret, tweet_id)
            else: like_state = None
            if project.twitter_comment:
                comment_state = twitter_api.check_comment(oauth_token, oauth_token_secret, tweet_id)
            else: comment_state = None
            if project.twitter_retweet:
                retweet_state = twitter_api.check_retweet(oauth_token, oauth_token_secret, tweet_id)
            else: retweet_state = None
            if project.twitter_follow:
                screen_name = project.twitter_follow_username
                follow_state = twitter_api.check_follow(oauth_token, oauth_token_secret, screen_name)
                
            else: follow_state = None
            if project.twitter_account_created:
                month_state, month_value = twitter_api.check_created_at(oauth_token, oauth_token_secret, project.twitter_account_months)
                twitter_user.account_months = month_value
            else: month_state = None
            if project.twitter_followers:
                followers_state, followers_value = twitter_api.check_created_at(oauth_token, oauth_token_secret, project.twitter_least_followers)
                twitter_user.followers = followers_value
            else: followers_state = None
            def check_none_true(value):
                if value is None or value:
                    return True
                else: return False
            #print(check_none_true(like_state) , check_none_true(retweet_state) , check_none_true(follow_state) , check_none_true(month_state) , check_none_true(followers_state) , check_none_true(comment_state))
            twitter_user.save()
            if check_none_true(like_state) and check_none_true(retweet_state) and check_none_true(follow_state) and check_none_true(month_state) and check_none_true(followers_state) and check_none_true(comment_state) :
                project = Project.objects.filter(project_id=project_id).first()
                twitter_user.projects.add(project)
                return render(request, 'mint/comfirm.html', {'context': project})
            else:
                context = {'context': project, 'like_state': like_state, 'retweet_state': retweet_state, 'follow_state': follow_state, 'month_state': month_state, 'comment_state': comment_state, 'followers_state': followers_state}
                return render(request, 'mint/error_page.html', context)
            
    except AttributeError as e: 
        print(e)
        return HttpResponse('You are logged in as a Staff and not a twitter user!!!')
def checkfollow(request, project_id):
    auth_user = request.user
    if request.method == "GET" and auth_user.is_authenticated :
        username = Project.objects.filter(project_id=project_id).first().twitter_follow_username
        twitter_api = TwitterAPI()
        twitter_user = TwitterUser.objects.filter(screen_name=auth_user).first()
        oauth_token = str(twitter_user.twitter_oauth_token)
        oauth_token_secret = str(TwitterAuthToken.objects.filter(oauth_token=oauth_token).first().oauth_token_secret)
        follow_state = twitter_api.check_follow(oauth_token, oauth_token_secret, username)
        return HttpResponse(follow_state)
    else: 
        return HttpResponse('')
def checklike(request, project_id):
    auth_user = request.user
    if request.method == "GET" and auth_user.is_authenticated :
        
        tweet_url = Project.objects.filter(project_id=project_id).first().twitter_tweet_link
        tweet_id = tweet_url.split('/')[-1].split('?')[0]
        twitter_api = TwitterAPI()
        twitter_user = TwitterUser.objects.filter(screen_name=auth_user).first()
        oauth_token = str(twitter_user.twitter_oauth_token)
        oauth_token_secret = str(TwitterAuthToken.objects.filter(oauth_token=oauth_token).first().oauth_token_secret)
        like_state = twitter_api.check_like(oauth_token, oauth_token_secret, tweet_id)
        return HttpResponse(like_state)
    else: 
        return HttpResponse('')
     
def checkretweet(request, project_id):
    auth_user = request.user
    if request.method == "GET" and auth_user.is_authenticated :
        
        tweet_id = Project.objects.filter(project_id=project_id).first().twitter_tweet_id
        twitter_api = TwitterAPI()
        twitter_user = TwitterUser.objects.filter(screen_name=auth_user).first()
        oauth_token = str(twitter_user.twitter_oauth_token)
        oauth_token_secret = str(TwitterAuthToken.objects.filter(oauth_token=oauth_token).first().oauth_token_secret)
        retweet_state = twitter_api.check_retweet(oauth_token, oauth_token_secret, tweet_id)
        return HttpResponse(retweet_state)
        
    else: 
        return HttpResponse('')
def checkcomment(request):
    auth_user = request.user
    if request.method == "GET" and auth_user.is_authenticated :
        
        tweet_id = Project.objects.filter(project_id=project_id).first().twitter_tweet_id
        twitter_api = TwitterAPI()
        oauth_token = str(twitter_user.twitter_oauth_token)
        oauth_token_secret = str(TwitterAuthToken.objects.filter(oauth_token=oauth_token).first().oauth_token_secret)
        comment_state = twitter_api.check_comment(oauth_token, oauth_token_secret, tweet_id)
        return HttpResponse(comment_state)
    else: 
        return HttpResponse('')
    
def success(request):
    projects_all = Project.objects.all().order_by('-project_date').first()
    
    return render(request, 'mint/home2.html', {'context': projects_all})