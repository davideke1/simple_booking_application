# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Booking, ChatMessage, CustomUser

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.booking_id = self.scope['url_route']['kwargs']['booking_id']
        self.booking_group_name = f'chat_{self.booking_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.booking_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.booking_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']

        # Get user instance
        user = self.scope['user']
        if user.is_anonymous:
            return

        # Get booking instance
        booking = await sync_to_async(Booking.objects.get)(id=self.booking_id)

        # Save message to database
        chat_message = ChatMessage(
            booking=booking,
            sender=user,
            message=message
        )
        await sync_to_async(chat_message.save)()

        # Send message to room group
        await self.channel_layer.group_send(
            self.booking_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))