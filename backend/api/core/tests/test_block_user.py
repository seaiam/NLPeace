from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from core.models.models import *


class TestBlockUser(TestCase):
    def setUp(self):
        # Create a test user with email as the login identifier
        self.email = 'testuser@email.com'
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)
        self.profile = Profile.objects.create(user=self.user)
        
        # create second user
        id=0
        email = 'testuser@test.com'
        username = 'test'
        password = 'testpassword123'
        user = User.objects.create_user(username=username, email=email, password=password,id=id)
        user.profile = Profile.objects.create(user=user)
        
        self.user1=user

    def test_blocking_user(self):
        
        
        self.client.login(username='testuser', password='testpassword123')
  
        response = self.client.get(reverse('add_block',args=[self.user1.id]))
        self.assertRedirects(response, reverse('profile'))  
        self.user.refresh_from_db()
