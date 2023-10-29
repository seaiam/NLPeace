from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models.models import *
from django.contrib.messages import get_messages


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


class ProfilePrivacyTest(TestCase):

    def setUp(self):
        # Create a test user with email as the login identifier
        self.email = 'testuser@email.com'
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)
        self.profile = Profile.objects.create(user=self.user, is_private=True)

    def test_privacy_settings_authenticated(self):
        self.client.login(username='testuser', password='testpassword123')
        
        privacy_data = {
            'is_private': False,  # Setting it to public
        }
        response = self.client.post(reverse('privacy_settings', args=[self.user.id]), privacy_data) 
        
        # Check that a success message is shown
        storage = get_messages(response.wsgi_request)
        self.assertIn("Privacy settings updated!", [message.message for message in storage])

        self.assertRedirects(response, reverse('privacy_settings', args=[self.user.id]))
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.is_private, False)

    def test_privacy_settings_unauthenticated(self):
        response = self.client.get(reverse('privacy_settings', args=[self.user.id]))  
        self.assertRedirects(response, '/accounts/login/?next=' + reverse('privacy_settings', args=[self.user.id])) 

    def test_privacy_settings_different_user(self):
        # Create another user with a private profile
        other_user = User.objects.create_user(username='otheruser', email='otheruser@email.com', password='otherpassword123')
        other_profile = Profile.objects.create(user=other_user, is_private=True)

        # Log in as the primary test user
        self.client.login(username='testuser', password='testpassword123')
        
        privacy_data = {   
            'is_private': False,
        }
        
        # Attempt to modify the privacy settings of the other user
        response = self.client.post(reverse('privacy_settings', args=[other_user.id]), privacy_data) 
        
        
        self.assertIn("You don't have permission to edit this user's settings.", response.content.decode())
        self.assertNotIn("Edit Profile", response.content.decode())
        self.assertNotIn("Update Bio", response.content.decode())
        self.assertNotIn("Edit Privacy Settings", response.content.decode())
        self.assertNotIn("Posts", response.content.decode())
        self.assertNotIn("Replies", response.content.decode())
        self.assertNotIn("Media", response.content.decode())
        self.assertNotIn("Likes", response.content.decode())


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