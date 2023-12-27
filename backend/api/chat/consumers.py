import json
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Message

User=get_user_model()

class ChatConsumer(WebsocketConsumer):
    
    def fetch_messages(self,data):
        messages=Message.last_10_messages()
        content={
            'command': 'messages',
            'messages':self.messages_to_json(messages)
        }
        print(content)
        self.send_message(content)
    
    def messages_to_json(self,messages):
        result=[]
        for message in messages:
            result.append(self.message_to_json(message))
        return result
    
    def message_to_json(self,message):
        return {
            'author':message.author.username,
            'content':message.content,
            'gif_url': message.gif_url,  
            'timestamp':str(message.timestamp),
        }
    
    def new_message(self,data):
        author=data['from']
        # author_user= User.objects.filter(username=author)[0]
        author_user = User.objects.filter(username=author).first()
        if author_user is None:
            return

        #message=Message.objects.create(author=author_user,content=data['message'])
        message = Message.objects.create(
            author=author_user,
            content=data.get('message', ''),
             gif_url=data.get('gif_url', None)
        )
        content={
            'command':'new_message',
            'message':self.message_to_json(message)
        }
        return self.send_chat_message(content)
    
    commands={
        'fetch_messages':fetch_messages,
        'new_message':new_message,
        
    }

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    # def receive(self, text_data):
    #     data = json.loads(text_data)
    #     self.commands[data['command']](self,data)

    def receive(self, text_data=None, bytes_data=None):
        if text_data:
            try:
                data = json.loads(text_data)
                self.commands[data['command']](self, data)
            except json.JSONDecodeError as e:
                self.send(text_data=json.dumps({'error': 'Invalid JSON'}))
        elif bytes_data:
            pass

        
    def send_chat_message(self,message):
        # message = data["message"]

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat.message", "message": message}
        )
    def send_message(self,message):
        self.send(text_data=json.dumps(message))
        
    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
       
        self.send(text_data=json.dumps(message))