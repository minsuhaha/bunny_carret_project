# chat_app/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatRoom, Message
from datetime import datetime
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):

    # 클라이언트가 WebSocket 연결을 시도할 때 호출되며,
    # 연결을 수락하고 그룹에 사용자를 추가합니다.
    async def connect(self):
        self.room_pk = self.scope['url_route']['kwargs']['room_pk']
        self.room_group_name = f'chat_{self.room_pk}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    # 클라이언트가 WebSocket 연결을 해제할 때 호출되며,
    # 그룹에서 사용자를 제거합니다.
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # 클라이언트로부터 메시지를 받을 때 호출되며,
    # 받은 메시지를 그룹 내의 모든 클라이언트에 전송합니다.
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        chatroom_id = text_data_json['chatroom_id']
        sender_id = self.scope['user'].id # 현재 요청을 보낸 사용자 id
        receiver_id = text_data_json['receiver_id']
        sent_at = datetime.now().isoformat()
        
        # chatroom_id로 ChatRoom 인스턴스를 가져옵니다.
        chatroom = await self.get_chatroom(chatroom_id)
        
        # 메시지 -> 데이터베이스에 저장
        await self.save_message(chatroom, sender_id, receiver_id, message)

        # room group에 메시지 전달
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id,
                'sent_at': sent_at
            }
        )

    # 그룹으로부터 메시지를 받을 때 호출되며,
    # 받은 메시지를 현재 클라이언트에게 전송합니다.	
    async def chat_message(self, event):
        message = event['message']
        sender_id = event['sender_id']
        sent_at = event['sent_at']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id,
            'sent_at': sent_at
        }))

    # 메시지 형식에 맞춰 데이터베이스에 저장합니다
    @database_sync_to_async
    def save_message(self, chatroom_id, sender_id, receiver_id, message):
        Message.objects.create(chatroom=chatroom_id, sender_id=sender_id, receiver_id=receiver_id, content=message)

    # chatroom의 id로 chatroom 인스턴스를 가져옵니다.
    @database_sync_to_async        
    def get_chatroom(self, chatroom_id):
        return ChatRoom.objects.get(id=chatroom_id)