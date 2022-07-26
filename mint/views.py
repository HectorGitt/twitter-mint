from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseForbidden
from django.core.exceptions import ValidationError
from django.views.generic.list import ListView
from twitter_api.twitter_api import TwitterAPI
from web3api.web3api import Web3
from .models import Project
from .models import TwitterAuthToken, TwitterUser
from .authorization import create_update_user_from_twitter
from web3.exceptions import InvalidAddress
from solana.rpc.api import Client
from solana.publickey import PublicKey
from decouple import config

# Create your views here.
def home(request):
    projects_all = Project.objects.all().order_by('-project_date')[0:6]
    return render(request, 'mint/home.html', {'context': projects_all})
class ProjectListView(ListView):
    model = Project
    paginate_by = 3
    template_name = 'projects.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
def project(request, project_id):
    username = request.user
    project = get_object_or_404(Project, project_id=project_id)
    registered_count = project.registered.all().count()
    if username.is_authenticated:
        try:
            twitter_user = TwitterUser.objects.filter(screen_name=username).first()
            registered = twitter_user.projects.all().filter(project_id=project_id).first()
        except:
            return HttpResponse('You are logged in as a Staff and not a twitter user!!!')
        
    else:
        class twitter_user():
            email = ''
            eth_wallet_id = ''
            sol_wallet_id = ''
        twitter_user = twitter_user()
        registered = False
    if project.twitter_tweet_link:
        tweet_id = project.twitter_tweet_id
    else: tweet_id = None
    estimated = 0
    if project.twitter_follow:
        estimated += 2
    if project.twitter_like:
        estimated += 2
    if project.twitter_retweet:
        estimated += 2
    if project.twitter_comment:
        estimated += 4
    if project.email_required:
        estimated += 4
    if project.wallet_type == 'SOL' or project.wallet_type == 'ETH':
        estimated += 4
    return render(request, 'mint/project.html', {'context': project, 'registered': registered, 'count': registered_count, 'tweet_id': tweet_id, 'twitter_user': twitter_user, 'estimated': estimated})
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
            user = TwitterAuthToken.objects.filter(oauth_token=access_token).last()
            if user is None or user.oauth_token_secret != access_token_secret : 
                twitter_auth_token.oauth_token = access_token
                twitter_auth_token.oauth_token_secret = access_token_secret
                twitter_auth_token.save()
            else:
                twitter_auth_token.delete()
            # Create user
            info = twitter_api.get_me(access_token, access_token_secret)
            if info is not None:
                twitter_user_new = TwitterUser(twitter_id=info[0]['id'], screen_name=info[0]['username'], name=info[0]['name'], profile_image_url=info[0]['profile_image_url'])
                if user is not None:
                    twitter_user_new.twitter_oauth_token = user
                else:
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
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        username = request.user
        try:
            twitter_user = TwitterUser.objects.filter(screen_name=username).first()
            project = Project.objects.filter(project_id=project_id).first()
            if request.method == 'POST':
                form_email = request.POST.get('email')
                eth = request.POST.get('eth')
                sol = request.POST.get('sol')
                if form_email != twitter_user.email:
                    twitter_user.email = str(form_email)
                if project.least_wallet_balance != 0 and project.wallet_type == 'ETH':
                    web3 = Web3()
                    try:
                        balance = web3.web3eth_balance(str(eth))
                    except InvalidAddress:
                        return HttpResponse(501)
                    if balance < project.least_wallet_balance:
                        return HttpResponse('Denied access')
                if eth is not None and twitter_user.eth_wallet_id != eth:
                    twitter_user.eth_wallet_id = str(eth)
                if project.least_wallet_balance != 0 and project.wallet_type == 'SOL':
                    solana_client = Client(config('SOLANA_PROVIDER'))
                    obj = solana_client.get_balance(PublicKey(str(sol)))
                    balance = obj['result']['value']
                    if balance < project.least_wallet_balance:
                       return HttpResponseForbidden('Forbidden')
                if sol is not None and twitter_user.sol_wallet_id != sol:
                    twitter_user.sol_wallet_id = str(sol)
                twitter_user.save()
                return redirect('comfirm', project_id)
            else:
                return redirect('comfirm', project_id)    
        except AttributeError as e:
            print(e)
            return HttpResponse('You are logged in as a Staff and not a twitter user!!!')
    else:
        raise Http404()     
@login_required
def comfirm(request, project_id):
    try:
        project = Project.objects.filter(project_id=project_id).first()
        username = request.user
        twitter_user = TwitterUser.objects.filter(screen_name=username).first()
        oauth_token = str(twitter_user.twitter_oauth_token)
        oauth_token_secret = str(TwitterAuthToken.objects.filter(oauth_token=oauth_token).first().oauth_token_secret)
        twitter_api = TwitterAPI()
        tweet_url = project.twitter_tweet_link
        if tweet_url:
            tweet_id = int(tweet_url.split('/')[-1].split('?')[0])
        else: tweet_id = None
        registered = twitter_user.projects.all().filter(project_id=project_id).first()
        if registered is not None:
            data = 300
            return HttpResponse(data)
        elif not project.status:
            return HttpResponse('Nice try..... Project Ended!!!')
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
                followers_state, followers_value = twitter_api.check_followers(oauth_token, oauth_token_secret, project.twitter_least_followers)
                twitter_user.followers = followers_value
            else: followers_state = None
            twitter_user.save()
            def check_none_true(value):
                if value is None or value:
                    return True
                else: return False
            #print(check_none_true(like_state) , check_none_true(retweet_state) , check_none_true(follow_state) , check_none_true(month_state) , check_none_true(followers_state) , check_none_true(comment_state))
            if check_none_true(like_state) and check_none_true(retweet_state) and check_none_true(follow_state) and check_none_true(month_state) and check_none_true(followers_state) and check_none_true(comment_state) :
                project = Project.objects.filter(project_id=project_id).first()
                twitter_user.projects.add(project)
                data = 200
                return HttpResponse(data)
            else:
                context = {'like_state': like_state, 'retweet_state': retweet_state, 'follow_state': follow_state, 'month_state': month_state, 'comment_state': comment_state, 'followers_state': followers_state}
                return JsonResponse(context)
            
    except AttributeError as e:
        print(e)
        return HttpResponse('You are logged in as a Staff and not a twitter user!!!')
    except ValidationError:
        raise Http404('Project does not exist')
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
def checkcomment(request, project_id):
    auth_user = request.user
    if request.method == "GET" and auth_user.is_authenticated :
        
        tweet_id = Project.objects.filter(project_id=project_id).first().twitter_tweet_id
        twitter_api = TwitterAPI()
        twitter_user = TwitterUser.objects.filter(screen_name=auth_user).first()
        oauth_token = str(twitter_user.twitter_oauth_token)
        oauth_token_secret = str(TwitterAuthToken.objects.filter(oauth_token=oauth_token).first().oauth_token_secret)
        comment_state = twitter_api.check_comment(oauth_token, oauth_token_secret, tweet_id)
        return HttpResponse(comment_state)
    else: 
        return HttpResponse('')
    
def checkfollowers(request, project_id):
    auth_user = request.user
    if request.method == "GET" and auth_user.is_authenticated :
        min_followers = Project.objects.filter(project_id=project_id).first().twitter_least_followers
        twitter_api = TwitterAPI()
        twitter_user = TwitterUser.objects.filter(screen_name=auth_user).first()
        oauth_token = str(twitter_user.twitter_oauth_token)
        oauth_token_secret = str(TwitterAuthToken.objects.filter(oauth_token=oauth_token).first().oauth_token_secret)
        followers_state, followers_value = twitter_api.check_followers(oauth_token, oauth_token_secret, min_followers )
        twitter_user.followers = followers_value
        return HttpResponse(followers_state)
    else: 
        return HttpResponse('')
def checkmonths(request, project_id):
    auth_user = request.user
    if request.method == "GET" and auth_user.is_authenticated :
        min_months = Project.objects.filter(project_id=project_id).first().twitter_account_months
        twitter_api = TwitterAPI()
        twitter_user = TwitterUser.objects.filter(screen_name=auth_user).first()
        oauth_token = str(twitter_user.twitter_oauth_token)
        oauth_token_secret = str(TwitterAuthToken.objects.filter(oauth_token=oauth_token).first().oauth_token_secret)
        months_state, months_value = twitter_api.check_created_at(oauth_token, oauth_token_secret, min_months)
        twitter_user.account_months = months_value
        return HttpResponse(months_state)
    else: 
        return HttpResponse('')
def success(request):
    projects_all = Project.objects.all().order_by('-project_date').first()
    
    return render(request, 'mint/home2.html', {'context': projects_all})
def checkwalletbalance(request,project_id):
    auth_user = request.user
    if request.method == "GET" and auth_user.is_authenticated :
        twitter_api = TwitterAPI()
        twitter_user = TwitterUser.objects.filter(screen_name=auth_user).first()
        oauth_token = str(twitter_user.twitter_oauth_token)
        oauth_token_secret = str(TwitterAuthToken.objects.filter(oauth_token=oauth_token).first().oauth_token_secret)
        #wallet_id = twitter_user.
        return HttpResponse(months_state)