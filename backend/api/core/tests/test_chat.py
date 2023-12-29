from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from chat.models import ChatRoom, Message
from core.models.models import User

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

    def test_chat_fileupload(self):
        self.client.login(username=self.username1, password=self.password)
        self.client.get(reverse('room', args=[self.user2.id]))
        data = {'file': SimpleUploadedFile("../static/testProfilePic.jpg", b"file_content")}
        count = Message.objects.count()
        response = self.client.post(reverse('upload', args=[self.user2.id]), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Message.objects.count(), count + 1)
