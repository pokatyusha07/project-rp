"""
Django signals для отправки WebSocket уведомлений при изменении данных.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

from .models import Call, Transcription, CallAnalysis

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Call)
def call_saved(sender, instance, created, **kwargs):
    """
    Отправляет WebSocket уведомление при создании или обновлении звонка.
    """
    channel_layer = get_channel_layer()
    
    try:
        # Уведомление для группы пользователя
        async_to_sync(channel_layer.group_send)(
            f'user_calls_{instance.user.id}',
            {
                'type': 'call_created' if created else 'call_updated',
                'call_id': str(instance.id),
                'call': {
                    'id': str(instance.id),
                    'status': instance.status,
                    'duration': instance.duration,
                    'language': instance.language,
                    'created_at': instance.created_at.isoformat()
                } if created else None,
                'status': instance.status if not created else None
            }
        )
        
        # Уведомление об изменении статуса для конкретного звонка
        if not created:
            async_to_sync(channel_layer.group_send)(
                f'transcription_{instance.id}',
                {
                    'type': 'status_update',
                    'call_id': str(instance.id),
                    'status': instance.status,
                    'message': f'Статус обновлен на: {instance.get_status_display()}'
                }
            )
        
    except Exception as e:
        logger.error(f"Ошибка отправки WebSocket уведомления: {e}")


@receiver(post_delete, sender=Call)
def call_deleted(sender, instance, **kwargs):
    """
    Отправляет WebSocket уведомление при удалении звонка.
    """
    channel_layer = get_channel_layer()
    
    try:
        async_to_sync(channel_layer.group_send)(
            f'user_calls_{instance.user.id}',
            {
                'type': 'call_deleted',
                'call_id': str(instance.id)
            }
        )
    except Exception as e:
        logger.error(f"Ошибка отправки WebSocket уведомления об удалении: {e}")


@receiver(post_save, sender=Transcription)
def transcription_saved(sender, instance, created, **kwargs):
    """
    Отправляет WebSocket уведомление при создании транскрипции.
    """
    if not created:
        return
    
    channel_layer = get_channel_layer()
    
    try:
        async_to_sync(channel_layer.group_send)(
            f'transcription_{instance.call.id}',
            {
                'type': 'transcription_completed',
                'call_id': str(instance.call.id),
                'transcription': {
                    'id': str(instance.id),
                    'text': instance.text,
                    'confidence': instance.confidence,
                    'segments': instance.segments
                }
            }
        )
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления о транскрипции: {e}")


@receiver(post_save, sender=CallAnalysis)
def analysis_saved(sender, instance, created, **kwargs):
    """
    Отправляет WebSocket уведомление при создании анализа.
    """
    if not created:
        return
    
    channel_layer = get_channel_layer()
    
    try:
        async_to_sync(channel_layer.group_send)(
            f'transcription_{instance.call.id}',
            {
                'type': 'status_update',
                'call_id': str(instance.call.id),
                'status': 'analysis_completed',
                'message': 'Анализ звонка завершен'
            }
        )
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления об анализе: {e}")
