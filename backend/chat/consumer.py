import json
from .models import Conversation
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Conversation, Message

class Chatting(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        conversation = Conversation.objects.filter(name=self.room_name).first()

        if not conversation:
            self.close()
            return

        if not conversation.members.filter(id=self.scope["user"].id).exists():
            self.close()
            return

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_name, self.channel_name
        )
        
    def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "").strip()
        user = self.scope["user"]

        if not message:
            return
        
        conversation = Conversation.objects.filter(name=self.room_name).first()
        if not conversation:
            return

        Message.objects.create(
            conversation=conversation,
            sender=user,
            content=message
        )

        async_to_sync(self.channel_layer.group_send)(
            self.room_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": user.email,
            }
        )

    def chat_message(self, event):
        self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
        }))