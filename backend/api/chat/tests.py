import pytest

from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.urls import path

from .consumers import NotificationConsumer
from .models import ChatRoom, Message, User
from core.models.post_models import Post

# We use a 'purely functional' style for asyn tests as suggested here: https://stackoverflow.com/a/61600142.
@pytest.mark.asyncio
async def test_notification_on_chat_message(self):
    username1 = 'test1'
    password1 = 'test1'
    username2 = 'test2'
    password2 = 'test2'
    user1 = await User.objects.acreate(username=username1, password=password1)
    user2 = await User.objects.acreate(username=username2, password=password2)
    room = await ChatRoom.objects.acreate(user1=user1, user2=user2)
    application = URLRouter([path('testws/<id>', NotificationConsumer.as_asgi())])
    communicator = WebsocketCommunicator(application, f'testws/{user2.id}')
    communicator.scope['user'] = user2
    try:
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        message = await Message.objects.acreate(author=user1, room_id=room, content='test')
        response = await communicator.receive_json_from()
        self.assertEqual('message', response['message']['type'])
        self.assertEqual(message.author.get_username(), response['message']['author'])
    finally:
        await communicator.disconnect()

@pytest.mark.asyncio
async def test_notification_on_post_comment(self):
    username1 = 'test1'
    password1 = 'test1'
    username2 = 'test2'
    password2 = 'test2'
    user1 = await User.objects.acreate(username=username1, password=password1)
    user2 = await User.objects.acreate(username=username2, password=password2)
    parent = await Post.objects.acreate(user=user2, content='test')
    application = URLRouter([path('testws/<id>', NotificationConsumer.as_asgi())])
    communicator = WebsocketCommunicator(application, f'testws/{user2.id}')
    communicator.scope['user'] = user2
    try:
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        comment = await Post.objects.create(user=user1, content='test', parent_post=parent)
        response = await communicator.receive_json_from()
        self.assertEqual('comment', response['message']['type'])
        self.assertEqual(comment.user.get_username(), response['message']['author'])
    finally:
        await communicator.disconnect()
