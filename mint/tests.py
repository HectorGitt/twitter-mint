from django.test import TestCase
from .models import Project
from django.db import IntegrityError
import tempfile
from twitter_api.twitter_api import TwitterAPI

# Create your tests here.

class ProjectTestCase(TestCase):
    image = tempfile.NamedTemporaryFile(suffix=".jpg").name
    def setUp(self):
        Project.objects.create(project_name='BlackBoard',project_link='hello', project_description='sss',project_image=self.image ) 
    def test_error(self):
        new = Project.objects.get(project_name='BlackBoard')
        self.assertEqual(new.project_name, 'BlackBoard')
        new.no_of_winners = -1
        self.assertEqual(new.no_of_winners, -1)
        
class TwitterApiTestCase(self):
    twitter_api = TwitterAPI()
    
    #def check_comment_test(self):
        
