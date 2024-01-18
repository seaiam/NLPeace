from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from io import BytesIO
from PIL import Image
from chat.models import ChatRoom, Message, ReportMessage
from core.models.models import User
from core.models.models import *

class ChatTest(TestCase):
    
    def setUp(self):
        # Create a test user with email as the login identifier
        email1 = 'testuser2@email.com'
        self.username1 = 'testuser1'
        email2 = 'testuser2@email.com'
        self.username2 = 'testuser2'
        self.password = 'testpassword123'
        self.message = 'testmessage'
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
        expected = f"/accounts/login/?next=/chat/{self.user2.id}"
        self.assertRedirects(response, expected)

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



    def test_search_existing_user(self):

        self.client.login(username=self.username1, password=self.password)

        # search for user2
        response = self.client.get(reverse('messages') + "?search=" + self.username2)

        self.assertContains(response, self.username2)
        self.assertNotContains(response, "No user found with the username: " + self.username2) 
        

    def test_search_nonexistent_user(self):
        try:  
            self.user1_profile=self.user1.profile
        except ObjectDoesNotExist:
            # Handle the case where the profile does not exist/ create a profile
            self.user1_profile=Profile.objects.create(user=self.user1)    
            self.user1_profile.save()

        self.client.login(username=self.username1, password=self.password)
        search_term="jenny"
        
        response = self.client.get(reverse('messages') + f"?search={search_term}",follow=True)
        self.assertContains(response, "No user found with the username: jenny") 

    def test_chat_file_upload(self):
        self.client.login(username=self.username1, password=self.password)
        self.client.get(reverse('room', args=[self.user2.id]))
        data = {'file': SimpleUploadedFile("assets/test.txt", b"file_content")}
        count = Message.objects.count()
        response = self.client.post(reverse('upload_file', args=[self.user2.id]), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Message.objects.count(), count + 1)
    
    def test_chat_image_upload(self):
        self.client.login(username=self.username1, password=self.password)
        self.client.get(reverse('room', args=[self.user2.id]))
        with Image.open('assets/test.jpg') as image:
            f = BytesIO()
            image.save(f, 'jpeg')
            f.seek(0)
            data = {'image': SimpleUploadedFile('test.jpg', f.read())}
            count = Message.objects.count()
            response = self.client.post(reverse('upload_image', args=[self.user2.id]), data)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(Message.objects.count(), count + 1)

    def test_report_message(self):
        self.client.login(username=self.username1, password=self.password)
        testroom = ChatRoom.objects.create(user1=self.user1, user2=self.user2)
        reports = ReportMessage.objects.all()
        count = reports.count()
        testmessage = Message.objects.create(author=self.user2, content=self.message, room_id=testroom)
        response = self.client.post(reverse('report_message', args=[testmessage.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(count+1, reports.count())


    def test_existing_chatroom(self):
        self.client.login(username='testuser1', password='testpassword123')
        chatroom = ChatRoom.objects.create(user1=self.user1, user2=self.user2)
        response = self.client.get(reverse('messages'))
        self.assertContains(response, 'Chats')
        self.client.logout()

    
    def test_no_chatroom(self):
        self.client.login(username='testuser1', password='testpassword123')
        response = self.client.get(reverse('messages'))
        self.assertContains(response, 'Please choose a chat')
        self.client.logout()