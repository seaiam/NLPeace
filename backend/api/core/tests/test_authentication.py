
from django.test import TestCase
from django.urls import reverse
from core.models.models import User , Profile
from django.core.exceptions import ObjectDoesNotExist



class UserLoginTest(TestCase):

    def setUp(self):
        # Create a test user with email as the login identifier
        self.email = 'testuser@email.com'
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)

    def test_correct_login(self):
        # Log in directly
        login_success = self.client.login(username=self.username, password=self.password)
        self.assertTrue(login_success)


    def test_incorrect_login(self):
        # Send a POST request to the login view with invalid credentials
        login_success = self.client.login(username=self.username, password='wronginput')
        self.assertFalse(login_success)


    def test_login_after_registration(self):
        # First, register the user
        registration_data = {
            'username': 'newuser2',
            'email': 'newuser2@email.com',
            'password1': 'newpassword456',
            'password2': 'newpassword456',
        }
        self.client.post(reverse('register_user'), registration_data)

        # Now, attempt to log in with the new user
        login_data = {
            'username': 'newuser2',
            'password': 'newpassword456',
        }
        response = self.client.post(reverse('login'), login_data)

        # Check if the user is authenticated
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        # Check if the response redirects to the desired page after login
        self.assertRedirects(response, '/accounts/profile/')
    
    def test_login_fails_if_user_is_banned(self):
        Profile.objects.create(user=self.user, is_banned=True)
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword123'})
        self.assertRedirects(response, reverse('login'))


class ForgetPasswordTest(TestCase):

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
            
            #Try a user email that exists
    def test_forget_password_correct_email(self):
        reset_password_data = {
            'email': 'testuser@email.com',
        }
        response = self.client.post(reverse('forget_password'), reset_password_data,follow=True)

        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, "An email has been sent.")
        #check if a token has been created for the user
        user = User.objects.get(email=self.email)
        profile = Profile.objects.get(user=user)
        self.assertIsNotNone(profile.forget_password_token)
        self.assertRedirects(response, '/accounts/login/')

            #Try a user email that doesn't exist
    def test_forget_password_wrong_email(self):
        reset_password_data = {
            'email': 'testusr@email.com',
        }
        response = self.client.post(reverse('forget_password'), reset_password_data,follow=True)

        self.assertEqual(response.status_code, 200)
        
        #check to see if response shows the desired message
        self.assertContains(response, "No user found with this email.")
        self.assertRedirects(response, '/forget_password/')

       
class ChangePasswordTest(TestCase):

    def setUp(self):
        # Create a test user with email as the login identifier
        self.email = 'testuser2@email.com'
        self.username = 'testuser2'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)
       
        
        try:
            self.profile = self.user.profile  # Try to access the profile
        except ObjectDoesNotExist:
            # Handle the case where the profile does not exist/ create a profile
            self.profile = Profile.objects.create(user=self.user)
            self.profile.forget_password_token='mytoken'
            self.profile.save()
            


    def test_change_password_matching(self):
        reset_password_data = {
           'new_password': 'testpassword1111',
           'confirm_password':'testpassword1111',
        }
        user = User.objects.get(email=self.email)
        profile = Profile.objects.get(user=user)
        # Simulate the POST request to the ChangePassword view with the token
       
        response = self.client.post(reverse('change_password', args=[profile.forget_password_token]), reset_password_data, follow=True)
        # Check the response status code and content
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You have successfully reset your password.")
        self.assertRedirects(response, '/accounts/login/')
        
        


    def test_change_password_nonmatching(self):
        reset_password_data = {
            'new_password': 'testpassword1234',
            'confirm_password':'tpass22',
        }
        user = User.objects.get(email=self.email)
        profile = Profile.objects.get(user=user)
          # Simulate the POST request to the ChangePassword view with the token
        response = self.client.post(reverse('change_password', args=[profile.forget_password_token]), reset_password_data, follow=True)
        # Check the response status code and content
        self.assertEqual(response.status_code, 200)

    
        self.assertContains(response, "The passwords are not matching. Make sure they do.")
        
        
    
   
