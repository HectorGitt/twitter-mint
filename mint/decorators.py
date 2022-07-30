from functools import wraps
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from mint.authorization import check_token_still_valid
from mint.models import TwitterUser

'''Twitter Oauth Login wrapper'''

#twiter login required decorator
def twitter_login_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        #check if request has a valid user with valid token
        twitter_user = TwitterUser.objects.filter(user=request.user).first()
        info = check_token_still_valid(twitter_user)
        #redirect to login if access token not valid
        if info is None:
            logout(request)
            return HttpResponseRedirect(reverse('twitter_login'))
        else:
            return function(request, *args, **kwargs)
    return wrap