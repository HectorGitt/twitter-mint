import tweepy
from decouple import config
from dateutil.relativedelta import relativedelta
import datetime

class TwitterAPI:
    def __init__(self):
        self.api_key = config('TWITTER_API_KEY')
        self.api_secret = config('TWITTER_API_SECRET')
        self.client_id = config('TWITTER_CLIENT_ID')
        self.client_secret = config('TWITTER_CLIENT_SECRET')
        self.oauth_callback_url = config('TWITTER_OAUTH_CALLBACK_URL')

    def twitter_login(self):
        oauth1_user_handler = tweepy.OAuthHandler(self.api_key, self.api_secret, callback=self.oauth_callback_url)
        url = oauth1_user_handler.get_authorization_url(signin_with_twitter=True)
        request_token = oauth1_user_handler.request_token["oauth_token"]
        request_secret = oauth1_user_handler.request_token["oauth_token_secret"]
        return url, request_token, request_secret

    def twitter_callback(self,oauth_verifier, oauth_token, oauth_token_secret):
        oauth1_user_handler = tweepy.OAuthHandler(self.api_key, self.api_secret, callback=self.oauth_callback_url)
        oauth1_user_handler.request_token = {
            'oauth_token': oauth_token,
            'oauth_token_secret': oauth_token_secret
        }
        access_token, access_token_secret = oauth1_user_handler.get_access_token(oauth_verifier)
        return access_token, access_token_secret

    def get_me(self, access_token, access_token_secret):
        try:
            client = tweepy.Client(consumer_key=self.api_key, consumer_secret=self.api_secret, access_token=access_token,
                                   access_token_secret=access_token_secret)
            info = client.get_me(user_auth=True, expansions='pinned_tweet_id')
            return info
        except Exception as e:
            print(e)
            return None
    def check_like(self, access_token, access_token_secret, tweet_id):
        try:
            auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth, wait_on_rate_limit=True)
            tweet = api.get_status(tweet_id)
            return tweet.favorited
        except Exception as e:
            print(e)
            return None
        
        
        
    def check_follow(self, access_token, access_token_secret, screen_name):
        try:
            auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth, wait_on_rate_limit=True)
            user = api.get_user(screen_name=screen_name)
            return user.following
        except Exception as e:
            print(e)
            return None
    def check_retweet(self, access_token, access_token_secret, retweet_id):
        try:
            auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth, wait_on_rate_limit=True)
            tweet = api.get_status(retweet_id)
            return tweet.retweeted
        except Exception as e:
            print(e)
            return None
    def check_comment(self, access_token, access_token_secret, tweet_id):
        try:
            auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth, wait_on_rate_limit=True)
            tweet = api.get_status(tweet_id)
            me = api.verify_credentials()
            status = me.status
            print(type(status.in_reply_to_status_id), type(tweet_id))
            if status.in_reply_to_status_id == tweet_id:
                return True
            else: return False
        except Exception as e:
            print(e)
            return None
    def check_followers(self, access_token, access_token_secret, min_follow):
        try:
            auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth, wait_on_rate_limit=True)
            me = api.verify_credentials()
            followers = me.followers_count
            if followers >= min_follow:
                return True
            else: return False
        except Exception as e:
            print(e)
            return None
    def check_created_at(self, access_token, access_token_secret, min_years):
        try:
            auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth, wait_on_rate_limit=True)
            me = api.verify_credentials()
            date = me.created_at
            account_years = relativedelta(date.date(), datetime.date.today()).years
            if account_years >= min_years:
                return True
            else: return False
            
        except Exception as e:
            print(e)
            return None