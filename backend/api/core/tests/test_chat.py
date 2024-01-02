from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from chat.models import ChatRoom, Message
from core.models.models import *

class ChatTest(TestCase):
    
    def setUp(self):
        # Create a test user with email as the login identifier
        email1 = 'testuser2@email.com'
        self.username1 = 'testuser1'
        email2 = 'testuser2@email.com'
        self.username2 = 'testuser2'
        self.password = 'testpassword123'
        self.user1 = User.objects.create_user(username=self.username1, email=email1, password=self.password)
        self.user2 = User.objects.create_user(username=self.username2, email=email2, password=self.password)
    
    def test_creation_chatRoom_authenticated(self):
        self.client.login(username=self.username1, password=self.password)
        count = ChatRoom.objects.count()
        self.assertEqual(count, 0)
        self.client.get(reverse('room', args=[self.user2.id]))
        count = ChatRoom.objects.count()
        self.assertEqual(count, 1)

    def test_chat_unauthenticated(self):
        response = self.client.get(reverse('room', args=[self.user2.id]))
        expected = f"/accounts/login/?next=/accounts/profile/messages/{self.user2.id}"
        self.assertRedirects(response, expected) 

    def test_chat_file_upload(self):
        self.client.login(username=self.username1, password=self.password)
        self.client.get(reverse('room', args=[self.user2.id]))
        data = {'file': SimpleUploadedFile("../static/testProfilePic.jpg", b"file_content")}
        count = Message.objects.count()
        response = self.client.post(reverse('upload', args=[self.user2.id]), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Message.objects.count(), count + 1)

    def test_chat_private_accounts(self):
       
        try:  
            self.user2_profile=self.user2.profile
        except ObjectDoesNotExist:
            # Handle the case where the profile does not exist/ create a profile
            self.user2_profile=Profile.objects.create(user=self.user2)    
            self.user2_profile.save()

        # Authenticate user1
        self.client.login(username=self.username1, password=self.password)

        # Attempt to access the chat room of user2
        response = self.client.get(reverse('room', args=[self.user2.id]))

        self.assertContains(response, "This user only allows messages from their followers")


    def test_chat_public_account(self):
       
        try:  
            self.user2_profile=self.user2.profile
        except ObjectDoesNotExist:
            # Handle the case where the profile does not exist/ create a profile
            self.user2_profile=Profile.objects.create(user=self.user2)    
            self.user2_profile.save()
            self.user2_profile.messaging_is_private=False
            self.user2_profile.save()

        # Authenticate user1
        self.client.login(username=self.username1, password=self.password)

        # Attempt to access the chat room of user2
        response = self.client.get(reverse('room', args=[self.user2.id]))

        self.assertNotContains(response, "This user only allows messages from their followers") 
        self.assertContains(response, "Start a Post...") 
 

    def test_chat_own_account(self):
       
        try:  
            self.user2_profile=self.user2.profile
        except ObjectDoesNotExist:
            # Handle the case where the profile does not exist/ create a profile
            self.user2_profile=Profile.objects.create(user=self.user2)    
            self.user2_profile.save()
           
        # Authenticate user1
        self.client.login(username=self.username2, password=self.password)

        # Attempt to access the chat room of user2
        response = self.client.get(reverse('room', args=[self.user2.id]))

        self.assertNotContains(response, "This user only allows messages from their followers") 
        self.assertContains(response, "Start a Post...") 



