# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message
from startup.models import Startup
from django.contrib.auth.models import User
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.startup_id = self.scope['url_route']['kwargs']['startup_id']
        self.startup = await self.get_startup(self.startup_id)

        # Создаем уникальный канал для этого стартапа
        self.room_group_name = f"startup_{self.startup.id}_chat"

        # Присоединяемся к каналу
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Отсоединяемся от канала
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = self.scope['user']

        # Сохраняем сообщение в базе данных
        message_obj = await database_sync_to_async(self.save_message)(user, message)

        # Отправляем сообщение всем участникам
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': user.username,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        user = event['user']

        # Отправляем сообщение WebSocket клиенту
        await self.send(text_data=json.dumps({
            'message': message,
            'user': user
        }))

    async def get_startup(self, startup_id):
        # Получаем стартап
        return await database_sync_to_async(Startup.objects.get)(id=startup_id)

    def save_message(self, user, message):
        # Сохраняем сообщение
        startup = Startup.objects.get(id=self.startup_id)
        return Message.objects.create(user=user, startup=startup, content=message)
