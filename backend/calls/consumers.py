"""
WebSocket consumers для real-time обновлений.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
import logging

logger = logging.getLogger(__name__)


class TranscriptionConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer для отслеживания прогресса транскрипции конкретного звонка.
    Отправляет промежуточные результаты транскрипции в реальном времени.
    """
    
    async def connect(self):
        """
        Обрабатывает подключение клиента к WebSocket.
        Проверяет авторизацию и добавляет в группу звонка.
        """
        self.call_id = self.scope['url_route']['kwargs']['call_id']
        self.room_group_name = f'transcription_{self.call_id}'
        
        # Проверяем авторизацию
        user = self.scope.get('user')
        if not user or isinstance(user, AnonymousUser):
            await self.close(code=4001)
            return
        
        # Проверяем доступ к звонку
        has_access = await self.check_call_access(user, self.call_id)
        if not has_access:
            await self.close(code=4003)
            return
        
        # Добавляем в группу канала
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        logger.info(f"WebSocket подключен: user={user.username}, call_id={self.call_id}")
        
        # Отправляем текущий статус звонка
        call_status = await self.get_call_status(self.call_id)
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'call_id': self.call_id,
            'status': call_status
        }))
    
    async def disconnect(self, close_code):
        """
        Обрабатывает отключение клиента от WebSocket.
        """
        # Удаляем из группы канала
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        logger.info(f"WebSocket отключен: call_id={self.call_id}, code={close_code}")
    
    async def receive(self, text_data):
        """
        Обрабатывает входящие сообщения от клиента.
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                # Ответ на ping для поддержания соединения
                await self.send(text_data=json.dumps({
                    'type': 'pong'
                }))
            
        except json.JSONDecodeError:
            logger.error(f"Ошибка парсинга JSON: {text_data}")
    
    async def transcription_progress(self, event):
        """
        Отправляет прогресс транскрипции клиенту.
        Вызывается через channel_layer.group_send().
        """
        await self.send(text_data=json.dumps({
            'type': 'transcription_progress',
            'call_id': event['call_id'],
            'progress': event['progress'],
            'text': event.get('text', ''),
            'segment': event.get('segment'),
            'timestamp': event.get('timestamp')
        }))
    
    async def transcription_completed(self, event):
        """
        Отправляет уведомление о завершении транскрипции.
        """
        await self.send(text_data=json.dumps({
            'type': 'transcription_completed',
            'call_id': event['call_id'],
            'transcription': event['transcription'],
            'analysis': event.get('analysis')
        }))
    
    async def transcription_error(self, event):
        """
        Отправляет уведомление об ошибке транскрипции.
        """
        await self.send(text_data=json.dumps({
            'type': 'transcription_error',
            'call_id': event['call_id'],
            'error': event['error']
        }))
    
    async def status_update(self, event):
        """
        Отправляет обновление статуса звонка.
        """
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'call_id': event['call_id'],
            'status': event['status'],
            'message': event.get('message')
        }))
    
    @database_sync_to_async
    def check_call_access(self, user, call_id):
        """
        Проверяет, имеет ли пользователь доступ к звонку.
        """
        from .models import Call
        try:
            call = Call.objects.get(id=call_id)
            return call.user == user or user.is_admin()
        except Call.DoesNotExist:
            return False
    
    @database_sync_to_async
    def get_call_status(self, call_id):
        """
        Получает текущий статус звонка.
        """
        from .models import Call
        try:
            call = Call.objects.get(id=call_id)
            return {
                'status': call.status,
                'has_transcription': hasattr(call, 'transcription'),
                'has_analysis': hasattr(call, 'analysis')
            }
        except Call.DoesNotExist:
            return {'status': 'not_found'}


class CallsConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer для отслеживания всех звонков пользователя.
    Отправляет уведомления о новых звонках и изменении статусов.
    """
    
    async def connect(self):
        """
        Обрабатывает подключение клиента.
        """
        user = self.scope.get('user')
        if not user or isinstance(user, AnonymousUser):
            await self.close(code=4001)
            return
        
        self.user_id = user.id
        self.room_group_name = f'user_calls_{self.user_id}'
        
        # Добавляем в группу пользователя
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        logger.info(f"WebSocket подключен к списку звонков: user={user.username}")
    
    async def disconnect(self, close_code):
        """
        Обрабатывает отключение клиента.
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        logger.info(f"WebSocket отключен от списка звонков: user_id={self.user_id}")
    
    async def receive(self, text_data):
        """
        Обрабатывает входящие сообщения.
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
            
        except json.JSONDecodeError:
            logger.error(f"Ошибка парсинга JSON: {text_data}")
    
    async def call_created(self, event):
        """
        Отправляет уведомление о создании нового звонка.
        """
        await self.send(text_data=json.dumps({
            'type': 'call_created',
            'call': event['call']
        }))
    
    async def call_updated(self, event):
        """
        Отправляет уведомление об обновлении звонка.
        """
        await self.send(text_data=json.dumps({
            'type': 'call_updated',
            'call_id': event['call_id'],
            'status': event.get('status'),
            'updates': event.get('updates')
        }))
    
    async def call_deleted(self, event):
        """
        Отправляет уведомление об удалении звонка.
        """
        await self.send(text_data=json.dumps({
            'type': 'call_deleted',
            'call_id': event['call_id']
        }))
