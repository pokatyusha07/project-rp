"""
Мониторинг и метрики системы.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from calls.models import Call
from users.models import User


class SystemMonitor:
    """
    Класс для мониторинга состояния системы.
    """
    
    @staticmethod
    def get_system_health():
        """
        Возвращает статус здоровья системы.
        
        Returns:
            dict: Статус компонентов системы
        """
        health = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'components': {}
        }
        
        # Проверка базы данных
        try:
            User.objects.count()
            health['components']['database'] = 'healthy'
        except Exception as e:
            health['components']['database'] = f'unhealthy: {str(e)}'
            health['status'] = 'degraded'
        
        # Проверка Redis (через Celery)
        try:
            from call_system.celery import app
            app.control.inspect().active()
            health['components']['redis'] = 'healthy'
        except Exception as e:
            health['components']['redis'] = f'unhealthy: {str(e)}'
            health['status'] = 'degraded'
        
        # Проверка очереди задач
        try:
            pending_calls = Call.objects.filter(status='pending').count()
            processing_calls = Call.objects.filter(status='processing').count()
            
            health['components']['queue'] = {
                'status': 'healthy',
                'pending': pending_calls,
                'processing': processing_calls
            }
            
            if pending_calls > 50:
                health['status'] = 'degraded'
                health['components']['queue']['status'] = 'overloaded'
        except Exception as e:
            health['components']['queue'] = f'unhealthy: {str(e)}'
            health['status'] = 'degraded'
        
        return health
    
    @staticmethod
    def get_performance_metrics():
        """
        Возвращает метрики производительности.
        
        Returns:
            dict: Метрики производительности
        """
        now = timezone.now()
        last_hour = now - timedelta(hours=1)
        last_day = now - timedelta(days=1)
        
        metrics = {
            'calls': {
                'last_hour': Call.objects.filter(created_at__gte=last_hour).count(),
                'last_day': Call.objects.filter(created_at__gte=last_day).count(),
                'processing': Call.objects.filter(status='processing').count(),
                'failed': Call.objects.filter(status='failed', created_at__gte=last_day).count(),
            },
            'users': {
                'total': User.objects.count(),
                'active_today': User.objects.filter(
                    calls__created_at__gte=last_day
                ).distinct().count()
            }
        }
        
        return metrics
