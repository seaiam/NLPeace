
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from core.forms import EditProfileForm
from django.core.files.uploadedfile import SimpleUploadedFile

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


class EditProfileFormTest(TestCase):

    def test_valid_form(self):
        form_data = {
            'uuid': 'test_uuid',
            'bio': 'test bio.',
        }

        banner_file = SimpleUploadedFile("testBannerPic.jpg", b"file_content")
        pic_file = SimpleUploadedFile("testProfilePic.png", b"file_content")

        form = EditProfileForm(data=form_data, files={'banner': banner_file, 'pic': pic_file})

        if not form.is_valid():
            print(form.errors)

        self.assertTrue(form.is_valid())
    
    def test_invalid_form(self):
        form_data = {
            'uuid': 'test_uuid',  
            'bio': 'test bio.',
        }
        #no banner or profile picture files
        form = EditProfileForm(data=form_data)

        self.assertFalse(form.is_valid())
