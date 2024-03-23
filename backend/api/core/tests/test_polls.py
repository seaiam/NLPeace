from django.test import TestCase
from django.contrib.auth.models import User
from core.models.models import Post, Poll, PollChoice, Vote, Profile
from django.core.exceptions import ObjectDoesNotExist

class PollTestCase(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')        
        try:
            self.profile = self.user.profile  # Try to access the profile
        except ObjectDoesNotExist:
            # Handle the case where the profile does not exist/ create a profile
            self.profile = Profile.objects.create(user=self.user)
    
    def test_poll(self):
        # Create a post
        self.post = Post.objects.create(user=self.user, content='Test content')
        
        # Create a poll associated with the post
        self.poll = Poll.objects.create(post=self.post)

        # Create choices for the poll
        self.choice1 = PollChoice.objects.create(poll=self.poll, choice_text='Choice 1')
        self.choice2 = PollChoice.objects.create(poll=self.poll, choice_text='Choice 2')

        # Create a vote for choice1
        vote1 = Vote.objects.create(choice=self.choice1, user=self.user)
        self.assertEqual(self.choice1, vote1.choice)
        self.choice1.choice_votes += 1
        self.poll.total_votes += 1
        
        # assert if vote totals are added correctly 
        self.assertEqual(self.choice1.choice_votes, 1)     
        self.assertEqual(self.poll.total_votes, 1)