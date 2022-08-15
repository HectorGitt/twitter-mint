import tweepy
from decouple import config
import datetime
import re

'''Twitter Oauth login handler'''

class TwitterAPI:
    def __init__(self):
        # Twitter API config variables
        self.api_key = config('TWITTER_API_KEY')
        self.api_secret = config('TWITTER_API_SECRET')
        self.client_id = config('TWITTER_CLIENT_ID')
        self.client_secret = config('TWITTER_CLIENT_SECRET')
        self.oauth_callback_url = config('TWITTER_OAUTH_CALLBACK_URL')

        
    def twitter_login(self):        
        """_summary_:
            Get authurization url for twitter login

        Returns:
            _str_: _redirect_url_
            _str_: _api_request_token_
            _str_: _api_request_token_secret_     
        """
        oauth1_user_handler = tweepy.OAuthHandler(self.api_key, self.api_secret, callback=self.oauth_callback_url)
        url = oauth1_user_handler.get_authorization_url(signin_with_twitter=True)
        request_token = oauth1_user_handler.request_token["oauth_token"]
        request_secret = oauth1_user_handler.request_token["oauth_token_secret"]
        return url, request_token, request_secret

    def twitter_callback(self,oauth_verifier, oauth_token, oauth_token_secret):
        """_summary_:
        Get access tokens from twitter api

        Args:
            oauth_verifier (_str_): _Returned from twitter api for access_
            oauth_token (_str_): _Returned from twitter api for access_
            oauth_token_secret (_str_): _Returned from twitter api for access_

        Returns:
            _str_: _access_token_
            _str_: _access_token_secret_
        """
        oauth1_user_handler = tweepy.OAuthHandler(self.api_key, self.api_secret, callback=self.oauth_callback_url)
        oauth1_user_handler.request_token = {
            'oauth_token': oauth_token,
            'oauth_token_secret': oauth_token_secret
        }
        access_token, access_token_secret = oauth1_user_handler.get_access_token(oauth_verifier)
        return access_token, access_token_secret

    def get_me(self, access_token, access_token_secret):
        """_summary_:
        Get user info from twitter api

        Args:
            access_token (_type_): _users_token_
            access_token_secret (_type_): _users_token_secret_

        Returns:
            _object_: _objects container user information_
        """
        try:
            client = tweepy.Client(consumer_key=self.api_key, consumer_secret=self.api_secret, access_token=access_token, access_token_secret=access_token_secret)
            info = client.get_me(user_auth=True, expansions='pinned_tweet_id')
            return info
        except Exception as e:
            print(e)
            return None
        
    def check_like(self, access_token, access_token_secret, tweet_id):
        """_summary_:
        Check if tweet is liked by user

        Args:
            access_token (_type_): _users_token_
            access_token_secret (_type_): _users_token_secret_
            tweet_id (_str_): _tweet_id_

        Returns:
            _Boolean_: _If tweet is liked_
        Errors:
            _Exception_: _If error_
            _Boolean_: _False_
        """
        try:
            auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth, wait_on_rate_limit=True)
            tweet = api.get_status(tweet_id)
            return tweet.favorited
        except Exception as e:
            print(e)
            return False
        
    def check_follow(self, access_token, access_token_secret, screen_name):
        """_summary_
        Check if user is following another twitter user

        Args:
            access_token (_str_): _users_token_
            access_token_secret (_str_): _users_token_secret_
            screen_name (_str_): _twitter_account_screen_name_to_check_if_user has followed_

        Returns:
            _Boolean_: _If_user_is_following_passed_user_
            
        Exception:
            _Boolean_: _return False_
        """
        try:
            auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth, wait_on_rate_limit=True)
            user = api.get_user(screen_name=screen_name)
            return user.following
        except Exception as e:
            print(e)
            return False
    def check_retweet(self, access_token, access_token_secret, retweet_id):
        """_summary_
        Check if tweet is retweeted by user

        Args:
            access_token (_str_): _users_token_
            access_token_secret (_str_): _users_token_secret_
            retweet_id (_int_): _tweet id of the tweet to be checked_

        Returns:
            _Boolean_: _If has retweeted the tweet_
            
        Exception:
            _Boolean_: _return False_
        """
        try:
            auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth, wait_on_rate_limit=True)
            tweet = api.get_status(retweet_id)
            return tweet.retweeted
        except Exception as e:
            print(e)
            return False
    def check_comment(self, access_token, access_token_secret, tweet_id, mention_count):
        """_summary_:
        Check if tweet is commented by user and also if user mentions require number of account

        Args:
            access_token (_str_): _users_token_
            access_token_secret (_str_): _users_token_secret_
            tweet_id (_int_): _tweet id of the tweet to be checked_
            mention_count(_int_): _number of required mentions_

        Returns:
             _Boolean_: _If user has commented on the tweet_
             _Boolean_: _If user has mentioned required number of account_
            
        Exception:
            _Boolean_: _return False_
        """
        try:
            auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth, wait_on_rate_limit=True)
            user = api.verify_credentials().screen_name
            tweet = api.get_status(tweet_id)
            comment = False
            mention_state = False
            #get 9 most recent status from users timeline
            timeline = api.user_timeline(since_id=tweet_id, count=9)
            for status in timeline:
                #check if status is a reply to project tweet   
                if status.in_reply_to_status_id == tweet_id and status.user.screen_name == user:
                    comment = True
                    #get all mentions in the tweet
                    mentions = set(re.findall('[@]\w+', status.text))
                    valid_mentions = 0
                    if mention_count > 0:
                        if len(mentions) > 0:
                            for mention in mentions:
                                screen_name = mention[1:]
                                if status.in_reply_to_screen_name != screen_name and screen_name != user:
                                    mentioned = api.get_user(screen_name=screen_name)
                                    if mentioned.screen_name == screen_name:
                                        valid_mentions += 1
                        if valid_mentions >= mention_count:
                            mention_state = True
                    else: mention_state = None
                    return comment,mention_state
            return comment,mention_state
        except Exception as e:
            print(e)
            return False,False
    def check_followers(self, access_token, access_token_secret, min_follow):
        """_summary_:
        Check if user meets minimum followers requirement

        Args:
            access_token (_str_): _users_token_
            access_token_secret (_str_): _users_token_secret_
            min_follow (_int_): _minimum followers requirement for project_

        Returns:
             _Boolean_: _If user met minimum follower requirement_
             _int_: _number of followers_
            
        Exception:
            _Boolean_: _return False_
            _None_: _return None
        """
        try:
            auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth, wait_on_rate_limit=True)
            me = api.verify_credentials()
            followers = me.followers_count
            if followers >= min_follow:
                return True, followers
            else: return False, followers
        except Exception as e:
            print(e)
            return False, None
    def check_created_at(self, access_token, access_token_secret, min_month):
        """_summary_:
        Check if user meets minimum creation period requirement

        Args:
            access_token (_str_): _users_token_
            access_token_secret (_str_): _users_token_secret_
            min_month (_int_): _minimum creation year/month requirement for project_

        Returns:
             _Boolean_: _If user met minimum creation period requirement_
             _int_: _account age in months_
            
        Exception:
            _Boolean_: _return False_
            _None_: _return None
        """
        try:
            auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth, wait_on_rate_limit=True)
            me = api.verify_credentials()
            date = me.created_at
            account_month = (datetime.date.today().year - date.date().year) * 12 + (datetime.date.today().month - date.date().month)
            if account_month >= min_month:
                return True, account_month
            else: return False, account_month
            
        except Exception as e:
            print(e)
            return False, None
    def process(self,oauth_token,oauth_token_secret,project):
        tweet_url = project.twitter_tweet_link
        if tweet_url:
            tweet_id = int(tweet_url.split('/')[-1].split('?')[0])
        else: tweet_id = None
        if project.twitter_like:
            like_state = self.check_like(oauth_token, oauth_token_secret, tweet_id)
        else: like_state = None
        if project.twitter_comment:
            mention_count = project.twitter_mention_count
            comment_state, mention_state = self.check_comment(oauth_token, oauth_token_secret, tweet_id, mention_count)
        else: 
            comment_state = None
            mention_state = None
        if project.twitter_retweet:
            retweet_state = self.check_retweet(oauth_token, oauth_token_secret, tweet_id)
        else: retweet_state = None
        if project.twitter_follow:
            screen_names = project.twitter_follow_username.split(',')
            follow_states = {}
            follow_state = True
            for screen_name in screen_names:
                state = self.check_follow(oauth_token, oauth_token_secret, screen_name)
                follow_states[screen_name] = state
                if state == False:
                    follow_state = False
        else: follow_state = None
        if project.twitter_account_created:
            month_state, month_value = self.check_created_at(oauth_token, oauth_token_secret, project.twitter_account_months)
        else:
            month_state = None
            month_value = None
        if project.twitter_followers:
            followers_state, followers_value = self.check_followers(oauth_token, oauth_token_secret, project.twitter_least_followers)
        else: 
            followers_state = None
            followers_value = None
        context = {'like_state': like_state, 'retweet_state': retweet_state, 'follow_state': follow_state, 'month_state': month_state, 'comment_state': comment_state, 'followers_state': followers_state, 'mention_state': mention_state,'followers_value': followers_value,'month_value': month_value}
        return context