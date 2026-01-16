"""
Celery задачи для обработки звонков.
"""
from celery import shared_task
from django.core.files import File
import logging
import asyncio

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_call_task(self, call_id):
    """
    Асинхронная обработка звонка: транскрипция и анализ.
    
    Args:
        call_id: ID звонка для обработки
    """
    from .models import Call
    from .services import TranscriptionService, AnalysisService
    
    try:
        # Получаем звонок
        call = Call.objects.get(id=call_id)
        call.status = 'processing'
        call.save()
        
        logger.info(f"Начало обработки звонка {call_id}")
        
        # Транскрибируем аудио
        transcription_service = TranscriptionService()
        transcription_data = transcription_service.transcribe(call)
        
        logger.info(f"Транскрипция звонка {call_id} завершена")
        
        # Анализируем текст
        analysis_service = AnalysisService()
        analysis_service.analyze(call)
        
        logger.info(f"Анализ звонка {call_id} завершен")
        
        # Обновляем статус
        call.status = 'completed'
        call.save()
        
        # Отправляем уведомление пользователю
        send_notification_task.delay(call.user.id, call_id)
        
        return {
            'status': 'success',
            'call_id': call_id,
            'transcription_length': len(transcription_data.get('text', ''))
        }
        
    except Call.DoesNotExist:
        logger.error(f"Звонок {call_id} не найден")
        return {'status': 'error', 'message': 'Call not found'}
        
    except Exception as exc:
        logger.error(f"Ошибка при обработке звонка {call_id}: {str(exc)}")
        
        # Обновляем статус на ошибку
        try:
            call = Call.objects.get(id=call_id)
            call.status = 'failed'
            call.save()
        except:
            pass
        
        # Повторяем задачу
        raise self.retry(exc=exc, countdown=60)


@shared_task
def send_notification_task(user_id, call_id):
    """
    Отправляет уведомление пользователю о готовности транскрипции.
    
    Args:
        user_id: ID пользователя
        call_id: ID звонка
    """
    from users.models import User
    from .notifications import TelegramNotifier
    
    try:
        user = User.objects.get(id=user_id)
        
        if user.notifications_enabled and user.telegram_id:
            notifier = TelegramNotifier()
            async_to_sync(notifier.send_transcription_ready)(user, call_id)
            
            logger.info(f"Уведомление отправлено пользователю {user_id}")
        
    except User.DoesNotExist:
        logger.error(f"Пользователь {user_id} не найден")
    except Exception as exc:
        logger.error(f"Ошибка при отправке уведомления: {str(exc)}")


@shared_task
def generate_daily_report_task():
    """
    Генерирует ежедневный отчет по звонкам.
    Запускается автоматически по расписанию.
    """
    from analytics.services import ReportService
    
    try:
        report_service = ReportService()
        report = report_service.generate_daily_report()
        
        logger.info(f"Ежедневный отчет создан: {report.date}")
        
        # Отправляем отчет админам
        from users.models import User
        admins = User.objects.filter(role='admin', notifications_enabled=True)
        
        for admin in admins:
            if admin.telegram_id:
                from .notifications import TelegramNotifier
                notifier = TelegramNotifier()
                notifier.send_daily_report(admin, report)
        
        return {'status': 'success', 'report_date': str(report.date)}
        
    except Exception as exc:
        logger.error(f"Ошибка при создании отчета: {str(exc)}")
        return {'status': 'error', 'message': str(exc)}
