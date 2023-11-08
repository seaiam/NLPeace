from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from core.models.models import *
from django.core.exceptions import ObjectDoesNotExist

class FollowUserTest(TestCase):
    def setUp(self):
        # Create a test user with email as the login identifier
        self.email = 'testuser@email.com'
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)
        self.email2 = 'testuser2@email.com'
        self.username2 = 'testuser2'
        self.password2 = 'testpassword123'
        self.user2 = User.objects.create_user(username=self.username2, email=self.email2, password=self.password2)
        self.notifications = Notifications.objects.create(notifications="notify",user=self.user2,sent_by=self.user,type="request")

        try:
            self.user=User.objects.get(username=self.username)
            self.user2 = User.objects.get(username=self.username2)
        except User.DoesNotExist:
            self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)
            self.user2 = User.objects.create_user(username=self.username2, email=self.email2, password=self.password2)
            self.user.save()
            self.user2.save()

        try:
            self.profile = self.user.profile  # Try to access the profile
            self.user2_profile=self.user2.profile
        except ObjectDoesNotExist:
            # Handle the case where the profile does not exist/ create a profile
            self.profile = Profile.objects.create(user=self.user)
            self.user2_profile=Profile.objects.create(user=self.user2)
            self.profile.save()
            self.user2_profile.save()
          

    def test_follow_private_user_request(self):
        
        data = {
            'followed_user': self.user2.id,
            'following_user': self.user.id,
            'search': 'testuser2',
        }
        self.client.login(username='testuser', password='testpassword123')
        self.client.login(username='testuser2', password='testpassword123')
       
        response = self.client.post(reverse('follow_user'), data,follow=True)

       
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A follow request has been sent.')

       
    def test_accept_private_user_request(self):
        self.client.login(username='testuser', password='testpassword123')
        self.client.login(username='testuser2', password='testpassword123')
       
        data = {
            
       'followed_user' : self.user2.id,
       'following_user' : self.user.id,
       'action' : "accept",
        }
       
       
        response = self.client.post(reverse('accept_decline_invite'), data,follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser started following you.')


    def test_follow_public_user(self):
        self.client.login(username='testuser', password='testpassword123')
        self.client.login(username='testuser2', password='testpassword123')
        user2_profile = self.user2.profile
        user_profile = self.user.profile
        user2_profile.is_private = False
        user2_profile.followers.clear()
        user_profile.following.clear()
        user2_profile.save()
        data = {
            'followed_user': self.user2.id,
            'following_user': self.user.id,
            'search': 'testuser2',
        }
       
        response = self.client.post(reverse('follow_user'), data,follow=True)

       
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You have started following testuser2.')
   