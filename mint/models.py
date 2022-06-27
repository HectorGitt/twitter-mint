from django.db import models
import uuid
import datetime
from django.core.exceptions import ValidationError
import json
import requests
# Create your models here.

class TwitterAuthToken(models.Model):
    oauth_token = models.CharField(max_length=255)
    oauth_token_secret = models.CharField(max_length=255)

    def __str__(self):
        return self.oauth_token



class Project(models.Model):
    project_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project_name = models.CharField(max_length=255)
    no_of_winners = models.PositiveIntegerField(default=1)
    project_date = models.DateTimeField(auto_now_add=True)
    project_end_date = models.DateField(default=(datetime.date.today() + datetime.timedelta(days=3)))
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
    twitter_account_years = models.PositiveIntegerField(default=None, null=True, blank=True)
    twitter_followers = models.BooleanField(default=False)
    twitter_least_followers = models.PositiveIntegerField(default=None, null=True, blank=True)
    project_status = models.BooleanField(default=True, editable = False)
    
    def clean(self):
        # check if the booleans fields ticked have a corresponding link
        if (self.twitter_follow) != (self.twitter_follow_username is not None):
            raise ValidationError('Twitter follow link is required if twitter follow is checked.')
        if (self.twitter_like) != (self.twitter_tweet_link is not None) and (self.twitter_comment) != (self.twitter_tweet_link is not None) and (self.twitter_retweet) != (self.twitter_tweet_link is not None) :
            raise ValidationError('Twitter link is required if tweets actions is/are checked.')
        
        if (self.twitter_followers) != (self.twitter_least_followers is not None):
            raise ValidationError('Twitter minimum follower values is required if twitter followers is checked.')
        if (self.twitter_account_created) != (self.twitter_account_years is not None):
            raise ValidationError('Twitter minumum account created years is required if twitter account created is checked.')
    def __str__(self):
        return self.project_name
    
    def save(self):
        
        if  self.twitter_tweet_link and not self.twitter_embed_html:
            self.twitter_embed_html = self.get_tweet_embed_html(self.twitter_tweet_link)
        elif  self.twitter_follow_username and not self.twitter_embed_html:
            self.twitter_embed_html = self.get_tweet_embed_html(self.twitter_follow_username)
        
        if self.twitter_tweet_link:
            self.twitter_tweet_id = self.twitter_tweet_link.split('/')[-1].split('?')[0]
        super().save()
    def get_tweet_embed_html(self, tweet_url):
        x = requests.get('https://publish.twitter.com/oembed?url={url}'.format(url=tweet_url))
        json_str = x.text
        json_object = json.loads(json_str)
        return json_object['html']
    class Meta:
        ordering = (["-project_date"])
    
class TwitterUser(models.Model):
    twitter_id = models.CharField(max_length=255)
    screen_name = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    profile_image_url = models.CharField(max_length=255, null=True)
    twitter_oauth_token = models.ForeignKey(TwitterAuthToken, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    projects = models.ManyToManyField(Project, blank=True, symmetrical=False, related_name='registered')
    email = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return self.screen_name
class Winner(models.Model):
    
    def __str__(self):
        return 'Display'
    