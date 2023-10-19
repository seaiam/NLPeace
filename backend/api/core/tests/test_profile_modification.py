from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from core.forms import EditBioForm, EditProfileBannerForm, EditProfilePicForm
from core.models import User, Profile

class EditProfilePicFormTest(TestCase):
    def setUp(self):
        # Create a test user with email as the login identifier
        self.email = 'testuser@email.com'
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)

    def test_update_profile_pic_view_authenticated(self):
        self.client.login(username='testuser', password='testpassword123')
        
        response = self.client.get(reverse('edit_pic'))
        self.assertEqual(response.status_code, 200)
        
                
        files={
            "banner": SimpleUploadedFile("../static/testProfilePic.jpg", b"file_content"
            )}
        response = self.client.post(reverse('edit_pic'), files)
        self.assertRedirects(response, reverse('profile')) 

    def test_update_profile_pic_view_unauthenticated(self):
        response = self.client.get(reverse('edit_pic'))
        self.assertRedirects(response, '/accounts/login/?next=/accounts/profile/updatePic/') 

class EditProfileBannerFormTest(TestCase):

    def setUp(self):
        # Create a test user with email as the login identifier
        self.email = 'testuser@email.com'
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)

    def test_update_profile_banner_authenticated(self):
        self.client.login(username='testuser', password='testpassword123')
        
        response = self.client.get(reverse('edit_banner'))
        self.assertEqual(response.status_code, 200)
        
        files={
            "banner": SimpleUploadedFile("../static/testBannerPic.jpg", b"file_content"
            )}
        response = self.client.post(reverse('edit_banner'), files)
        self.assertRedirects(response, reverse('profile'))  

    def test_update_profile_banner_unauthenticated(self):
        response = self.client.get(reverse('edit_banner'))
        self.assertRedirects(response, '/accounts/login/?next=/accounts/profile/updateBanner/') 


class EditBioFormTest(TestCase):
    def setUp(self):
        # Create a test user with email as the login identifier
        self.email = 'testuser@email.com'
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)
        self.profile = Profile.objects.create(user=self.user, bio="Old Bio")

    def test_update_bio_authenticated(self):
        self.client.login(username='testuser', password='testpassword123')
        bio_data = {
            'bio': 'NewBio',
        }
        response = self.client.post(reverse('edit_bio'), bio_data)
        self.assertRedirects(response, reverse('profile'))  
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.bio,"NewBio")

    def test_update_profile_banner_unauthenticated(self):
        response = self.client.get(reverse('edit_bio'))
        self.assertRedirects(response, '/accounts/login/?next=/accounts/profile/updateBio/')

class DefaultProfilePicTest(TestCase):
    def setUp(self):
        # Create a test user with email as the login identifier
        self.email = 'testuser@email.com'
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)
        self.profile = Profile.objects.create(user=self.user)
    
    def test_profile_without_profile_picutre_has_default(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('profile'))
        self.assertContains(response, 'default.jpg')