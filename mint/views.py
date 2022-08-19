from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseForbidden
from django.core.exceptions import ValidationError
from django.views.generic.list import ListView
from twitter_api.twitter_api import TwitterAPI
from web3api.web3api import Web3api
from web3.exceptions import InvalidAddress
from solana.rpc.api import Client
from solana.publickey import PublicKey
from decouple import config
from .models import Project
from .models import TwitterAuthToken, TwitterUser
from .authorization import create_update_user_from_twitter
from django.utils import timezone
from django.views.decorators.cache import never_cache


# Create your views here.
def home(request):
    """_Loads the first set of most recent product and render it on home template_

    Args:
        request (_request_): _description_

    Returns:
        _http_response_: _description_
    """
    project_per_page = 6
    projects_all = Project.objects.all().order_by('-project_date')[0:project_per_page]
    return render(request, 'mint/home.html', {'context': projects_all})
class ProjectListView(ListView):
    """_paginate a list of model data into pages and render in template_

    Args:
        ListView (_object_): _django list view class_

    Returns:
        _type_: _description_
    """
    model = Project
    paginate_by = 3
    template_name = 'projects.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
@never_cache  
def project(request, project_id):
    """_Processes the project contect data and render dynnamic data based on
        project details_

    Args:
        request (_type_): _description_
        project_id (_type_): _product id of selected project_

    Returns:
        _http_response_: _description_
    """
    #get user from request object
    username = request.user
    project = get_object_or_404(Project, project_id=project_id)
    registered_count = project.registered.all().count()
    #check if user is authenticated
    if username.is_authenticated:
        try:
            #get user object and check if user is registered
            twitter_user = TwitterUser.objects.filter(screen_name=username).first()
            registered = twitter_user.projects.all().filter(project_id=project_id).first()
        except:
            return HttpResponse('You are logged in as a Staff and not a twitter user!!!')
        
    else:
        #instantiate object with empty attributes if user not authenticated and set registration to false
        class twitter_user():
            email = ''
            eth_wallet_id = ''
            sol_wallet_id = ''
        twitter_user = twitter_user()
        registered = False
    if project.twitter_tweet_link:
        #get tweet id from project
        tweet_id = project.twitter_tweet_id
    else: tweet_id = None
    #estimated time of action completion
    estimated = 0
    if project.twitter_follow:
        follow_list = project.twitter_follow_username.split()
        estimated += (2*len(follow_list))
    else: follow_list = []
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
    #check if project end date is not reached
    if project.project_end_date > timezone.now():
        status = True
    else:
        status = False
    return render(request, 'mint/project.html', {'context': project, 'registered': registered, 'count': registered_count, 'tweet_id': tweet_id, 'twitter_user': twitter_user, 'estimated': estimated, 'status': status, 'screen_names': follow_list})
def login_user(request):
    """_handle login request_

    Args:
        request (_request_object_): _description_

    Returns:
        _http_response_: _renders page with next variable for redirect_
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    else:
        request.session['next'] = request.GET.get('next', '/')
        return render(request, 'mint/login.html', {'next': next})
    
@never_cache
def twitter_login(request):
    """_Handles twitter oauth login_

    Args:
        request (_request_object_): _description_

    Returns:
        _http_redirect_: _redirect to twitter authorization url_
    """
    twitter_api = TwitterAPI()
    #get tokens and authorization url
    url, oauth_token, oauth_token_secret = twitter_api.twitter_login()
    if url is None or url == '':
        messages.add_message(request, messages.ERROR, 'Unable to login. Please try again.')
        return render(request, 'authorization/error_page.html')
    else:
        twitter_auth_token = TwitterAuthToken.objects.filter(oauth_token=oauth_token).first()
        #if user not found with the auth tokens
        if twitter_auth_token is None:
            twitter_auth_token = TwitterAuthToken(oauth_token=oauth_token, oauth_token_secret=oauth_token_secret)
            twitter_auth_token.save()
        else:
            #if found, change the auth token secret to updated secret key
            twitter_auth_token.oauth_token_secret = oauth_token_secret
            twitter_auth_token.save()
        return redirect(url) 
def callback(request):
    """_handle twitter api oauth login callback and display appropriate errors _

    Args:
        request (_request_object_): _description_

    Returns:
        _http_response_: _description_
    """
    #if twitter oauth login was denied
    if 'denied' in request.GET:
        messages.add_message(request, messages.ERROR, 'Unable to login or login canceled. Please try again.')
        return render(request, 'mint/error_page.html')
    twitter_api = TwitterAPI()
    #get tokens from callback request object
    oauth_verifier = request.GET.get('oauth_verifier')
    oauth_token = request.GET.get('oauth_token')
    twitter_auth_token = TwitterAuthToken.objects.filter(oauth_token=oauth_token).first()
    #if auth token is found for twitter user
    if twitter_auth_token is not None:
        access_token, access_token_secret = twitter_api.twitter_callback(oauth_verifier, oauth_token, twitter_auth_token.oauth_token_secret)
        #if access
        if access_token is not None and access_token_secret is not None:
            #get twitter user object that match last auth token
            user = TwitterAuthToken.objects.filter(oauth_token=access_token).last()
            #save tokens if user is not found or if user token is needs to be updated
            if user is None or user.oauth_token_secret != access_token_secret : 
                twitter_auth_token.oauth_token = access_token
                twitter_auth_token.oauth_token_secret = access_token_secret
                twitter_auth_token.save()
            else:
                twitter_auth_token.delete()
            # get user info from twitter api
            info = twitter_api.get_me(access_token, access_token_secret)
            if info is not None:
                twitter_user_new = TwitterUser(twitter_id=info[0]['id'], screen_name=info[0]['username'], name=info[0]['name'], profile_image_url=info[0]['profile_image_url'])
                #check if user token not none
                if user is not None:
                    twitter_user_new.twitter_oauth_token = user
                else:
                    twitter_user_new.twitter_oauth_token = twitter_auth_token
                #create new user in database
                user, twitter_user = create_update_user_from_twitter(twitter_user_new)
                #if user successfully created
                if user is not None:
                    #login
                    login(request, user)
                    #try to return to initial page from next url
                    try:
                        return redirect(request.session['next'])
                    except:
                        return redirect('home')
                    
            else:
                #if get me twitter api returns none
                messages.add_message(request, messages.ERROR, 'Unable to get profile details. Please try again.')
                return render(request, 'mint/error_page.html')
        else:
            #if access token not returned from twitter api
            messages.add_message(request, messages.ERROR, 'Unable to get access token. Please try again.')
            return render(request, 'mint/error_page.html')
    else:
        #if access token is not found in the database
        messages.add_message(request, messages.ERROR, 'Unable to retrieve access token. Please try again.')
        return render(request, 'mint/error_page.html')

@login_required
def twitter_logout(request):
    """_handles twitter oauth logout_

    Args:
        request (_request_object_): _description_

    Returns:
        _http_response_: _redirect to homepage_
    """
    logout(request)
    return redirect('home')

def connect_twitter(request):
    """_Redirects to twitter oauth login view_

    Args:
        request (_request_object_): _description_

    Returns:
        _http_response_: _redirect to twitter oauth login view_
    """
    #get next url from request and save to session(later used by twitter_login view)
    request.session['next'] = request.GET.get('next', '/')
    return redirect('twitter_login')
    

@login_required
def verify(request, project_id):
    """_Verify forms and walle_

    Args:
        request (_request_object_): _description_
        project_id (_int_): _description_

    Raises:
        Http404: _description_
        
    Exception:
        Attribute Error: _Raises when logged in user is not a twitter user_

    Returns:
        _type_: _description_
    """
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        username = request.user
        try:
            twitter_user = TwitterUser.objects.filter(screen_name=username).first()
            project = Project.objects.filter(project_id=project_id).first()
            if request.method == 'POST':
                form_email = request.POST.get('email')
                eth = request.POST.get('eth')
                sol = request.POST.get('sol')
                if project.email_required and form_email != twitter_user.email:
                    twitter_user.email = str(form_email)
                if project.least_wallet_balance != 0 and project.wallet_type == 'ETH':
                    web3 = Web3api()
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
                    ui_balance = round((balance * (10**-9) ), 9)
                    if ui_balance < project.least_wallet_balance:
                       return HttpResponse(400)
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
        registered = twitter_user.projects.all().filter(project_id=project_id).first()
        if registered is not None:
            data = 300
            return HttpResponse(data)
        elif not project.status:
            return HttpResponse('Nice try..... Project Ended!!!')
        else:
            data = twitter_api.process(oauth_token, oauth_token_secret,project)
            if project.twitter_account_created:
                twitter_user.account_months = data['month_value']
            if project.twitter_followers:
                twitter_user.followers = data['followers_value']
            twitter_user.save()
            def check_none_true(value):
                if value is None or value:
                    return True
                else: return False
            if check_none_true(data['like_state']) and check_none_true(data['retweet_state']) and check_none_true(data['follow_state']) and check_none_true(data['month_state']) and check_none_true(data['followers_state']) and check_none_true(data['comment_state']) and check_none_true(data['mention_state']):
                project = Project.objects.filter(project_id=project_id).first()
                twitter_user.projects.add(project)
                dataVal = 200
                return HttpResponse(dataVal)
            else:
                return JsonResponse(data)
            
    except AttributeError as e:
        print(e)
        return HttpResponse('You are logged in as a Staff and not a twitter user!!!')
    except ValidationError:
        raise Http404('Project does not exist')
def checkactions(request, project_id):
    auth_user = request.user
    if request.method == "GET" and auth_user.is_authenticated :
        project = Project.objects.filter(project_id=project_id).first()
        twitter_user = TwitterUser.objects.filter(screen_name=auth_user).first()
        oauth_token = str(twitter_user.twitter_oauth_token)
        oauth_token_secret = str(TwitterAuthToken.objects.filter(oauth_token=oauth_token).first().oauth_token_secret)
        twitter_api = TwitterAPI()
        data = twitter_api.process(oauth_token, oauth_token_secret, project)
        return JsonResponse(data)
def success(request):
    projects_all = Project.objects.all().order_by('-project_date').first()
    
    return render(request, 'mint/home2.html', {'context': projects_all})
def checkwalletbalance(request,project_id):
    auth_user = request.user
    project = Project.objects.filter(project_id=project_id).first()
    twitter_user = TwitterUser.objects.filter(screen_name=auth_user).first()
    if request.method == "POST" and auth_user.is_authenticated :
        eth = request.POST.get('eth')
        sol = request.POST.get('sol')
        if eth is not None and twitter_user.eth_wallet_id != eth:
            twitter_user.eth_wallet_id = str(eth)
        if project.least_wallet_balance != 0 and project.wallet_type == 'ETH':
            web3 = Web3api()
            try:
                ui_balance = web3.web3eth_balance(str(eth))
            except InvalidAddress:
                return HttpResponse(501)
        if sol is not None and twitter_user.sol_wallet_id != sol:
            twitter_user.sol_wallet_id = str(sol)
        if project.least_wallet_balance != 0 and project.wallet_type == 'SOL':
            solana_client = Client(config('SOLANA_PROVIDER'))
            obj = solana_client.get_balance(PublicKey(str(sol)))
            balance = obj['result']['value']
            ui_balance = round((balance * (10**-9) ), 9)
        twitter_user.save()
        obj = {'response': 200, 'value': ui_balance}
        return JsonResponse(obj)
    else:
        return HttpResponse('Denied')
        
        