from django.db import models
import uuid
from django.utils import timezone
from django.core.exceptions import ValidationError
import json
import requests
import datetime
# Create your models here.

class TwitterAuthToken(models.Model):
    oauth_token = models.CharField(max_length=255)
    oauth_token_secret = models.CharField(max_length=255)

    def __str__(self):
        return self.oauth_token

class Project(models.Model):
    NONE = 'NIL'
    ETHEREUM = 'ETH'
    SOLANA = 'SOL'
    OPTION0 = 0
    OPTION1 = 0.2
    OPTION2 = 0.5
    OPTION3 = 0.7
    OPTION4 = 1.0
    WALLET_TYPE = [(NONE, 'Nil'), (ETHEREUM, 'Ethereum'), (SOLANA, 'Solana')]
    WALLET_BALANCE = [(OPTION0, '0'),(OPTION1, '0.2'), (OPTION2, '0.5'),(OPTION3, '0.7'), (OPTION4, '1.0')]
    project_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project_name = models.CharField(max_length=255)
    no_of_winners = models.PositiveIntegerField(default=1)
    project_date = models.DateTimeField(auto_now_add=True)
    end_hours = models.PositiveIntegerField(default=0)
    project_end_date = models.DateTimeField(default=None, editable=False)
    project_price = models.PositiveIntegerField(default=1)
    project_link = models.URLField(max_length=255)
    project_description = models.TextField()
    project_image = models.ImageField(upload_to='media/uploads/', null=False)
    twitter_follow = models.BooleanField(default=False)
    twitter_follow_username = models.CharField(max_length=255, null=True, blank=True)
    twitter_tweet_link = models.URLField(max_length=255, null=True, blank=True)
    twitter_tweet_id = models.BigIntegerField(editable=False, null=True, blank=True)
    twitter_like = models.BooleanField(default=False)
    twitter_retweet = models.BooleanField(default=False)
    twitter_comment = models.BooleanField(default=False)
    twitter_embed_html = models.TextField(editable=False,null=True, blank=True)
    twitter_account_created = models.BooleanField(default=False)
    twitter_account_months = models.PositiveIntegerField(default=None, null=True, blank=True)
    twitter_followers = models.BooleanField(default=False)
    twitter_least_followers = models.PositiveIntegerField(default=None, null=True, blank=True)
    wallet_type = models.CharField(max_length=3, choices=WALLET_TYPE, default=NONE)
    least_wallet_balance = models.FloatField(choices=WALLET_BALANCE, default=OPTION0)
    email_required = models.BooleanField(default=True)
    status = models.BooleanField(default=True)
    winners = models.ManyToManyField('TwitterUser', editable=False, blank=True, symmetrical=False, related_name='winners')
    
    def clean(self):
        # check if the booleans fields ticked have a corresponding link
        if (self.twitter_follow) != (self.twitter_follow_username is not None):
            raise ValidationError('Twitter follow link is required if twitter follow is checked.')
        count = 0
        
        #Check If at least twitter action match the link
        if (self.twitter_like) == (self.twitter_tweet_link is not None):
            pass
        else: count += 1    
        if (self.twitter_comment) == (self.twitter_tweet_link is not None):
                pass
        else: count += 1
        if (self.twitter_retweet) == (self.twitter_tweet_link is not None):
            pass
        else: count += 1
        print(count)
        if count == 3 :
            raise ValidationError('Twitter link is required if tweets actions is/are checked.')
        if (self.twitter_followers) != (self.twitter_least_followers is not None):
            raise ValidationError('Twitter minimum follower values is required if twitter followers is checked.')
        if (self.twitter_account_created) != (self.twitter_account_months is not None):
            raise ValidationError('Twitter minumum account created years is required if twitter account created is checked.')
        if (self.project_end_date is None):
            self.project_end_date = datetime.datetime.now() + timezone.timedelta(hours=self.end_hours)
    def __str__(self):
        return str(self.project_name)
    
    def save(self, *args, **kwargs):
        
        if  self.twitter_tweet_link and not self.twitter_embed_html:
            self.twitter_embed_html = self.get_tweet_embed_html(self.twitter_tweet_link)
        elif  self.twitter_follow_username and not self.twitter_embed_html:
            self.twitter_embed_html = self.get_tweet_embed_html(self.twitter_follow_username)
        
        if self.twitter_tweet_link:
            self.twitter_tweet_id = self.twitter_tweet_link.split('/')[-1].split('?')[0]
        super(Project, self).save(*args, **kwargs)
    def get_tweet_embed_html(self, tweet_url):
        x = requests.get('https://publish.twitter.com/oembed?url={url}'.format(url=tweet_url))
        json_str = x.text
        json_object = json.loads(json_str)
        return json_object.get('html')
    class Meta:
        ordering = (["-project_date"])
        
class TwitterUser(models.Model):
    twitter_id = models.CharField(max_length=255)
    screen_name = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    profile_image_url = models.CharField(max_length=255, null=True)
    twitter_oauth_token = models.ForeignKey(TwitterAuthToken, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    followers = models.PositiveIntegerField(default=None, null=True, blank=True)
    account_months = models.PositiveIntegerField(default=None, null=True, blank=True)
    projects = models.ManyToManyField(Project, blank=True, symmetrical=False, related_name='registered')
    email = models.CharField(max_length=255, null=True, blank=True)
    eth_wallet_id = models.CharField(max_length=42, null=True, blank=True)
    sol_wallet_id = models.CharField(max_length=44, null=True, blank=True)
    def __str__(self):
        return self.screen_name
class EmailNotification(models.Model):
    subject = models.CharField(max_length=80, default='Congratulations, You have been selected')
    heading = models.CharField(max_length=60, default='Congratulations!!!')
    heading_secondary = models.CharField(max_length=100, default='You have been selected.')
    content = models.TextField(max_length=500, default='You have been picked as the winner of the project you registered for at twitter-minting, you can send us a mail to claim your price.')
    date = models.DateTimeField(auto_now_add=True, editable=False)
    class Meta:
        ordering = (["-date"])
    def __str__(self):
        return self.subject