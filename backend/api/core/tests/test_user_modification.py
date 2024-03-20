from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from core.models.profile_models import Profile

class EditBioFormTest(TestCase):
    def setUp(self):
        # Create a test user with email as the login identifier
        self.email = 'testuser@email.com'
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)

        try:
            self.profile = self.user.profile  # Try to access the profile
        except ObjectDoesNotExist:
            # Handle the case where the profile does not exist/ create a profile
            self.profile = Profile.objects.create(user=self.user)   

    def test_change_username_authenticated(self):
        self.client.login(username='testuser', password='testpassword123')
        username_data={
            'username': 'test'
        }
        response = self.client.post(reverse('update_username'), username_data)
        self.assertRedirects(response, reverse('profile'))  
        self.user.refresh_from_db()
        self.assertEqual(self.user.username,"test")
        
    def test_change_username_unauthenticated(self):
        response = self.client.post(reverse('update_username'))
        self.assertRedirects(response, '/accounts/login/?next=%2Faccounts%2Fprofile%2Fsettings%2FupdateUsername')  
        
    def test_change_password_authenticated(self):
        self.client.login(username='testuser', password='testpassword123')
        old_pwd=self.password
        password_data={
            'new_password1': 'newtestpwd123',
            'new_password2': 'newtestpwd123',
            'old_password': 'testpassword123',
        }
        response = self.client.post(reverse('update_password'), password_data)
        self.assertRedirects(response, reverse('profile'))  
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.password,old_pwd)

    def test_change_password_unauthenticated(self):
        response = self.client.post(reverse('update_password'))
        self.assertRedirects(response, '/accounts/login/?next=%2Faccounts%2Fprofile%2Fsettings%2FupdatePassword')