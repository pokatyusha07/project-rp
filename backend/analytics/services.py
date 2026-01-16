"""
Сервисы для генерации отчетов и аналитики.
"""
from datetime import date
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta

from .models import DailyReport, UserStats
from calls.models import Call, CallAnalysis


class ReportService:
    """
    Сервис для генерации отчетов.
    """
    
    def generate_daily_report(self, report_date=None):
        """
        Генерирует ежедневный отчет по звонкам.
        
        Args:
            report_date: Дата отчета (по умолчанию вчера)
            
        Returns:
            DailyReport: Созданный отчет
        """
        if report_date is None:
            report_date = timezone.now().date() - timedelta(days=1)
        
        # Получаем звонки за указанную дату
        calls = Call.objects.filter(created_at__date=report_date)
        
        # Подсчитываем статистику
        total_calls = calls.count()
        completed_calls = calls.filter(status='completed').count()
        failed_calls = calls.filter(status='failed').count()
        
        total_duration = calls.aggregate(Sum('duration'))['duration__sum'] or 0
        average_duration = calls.aggregate(Avg('duration'))['duration__avg'] or 0
        
        # Статистика по категориям
        categories_stats = dict(
            CallAnalysis.objects.filter(
                call__in=calls
            ).values('category').annotate(
                count=Count('id')
            ).values_list('category', 'count')
        )
        
        # Создаем или обновляем отчет
        report, created = DailyReport.objects.update_or_create(
            date=report_date,
            defaults={
                'total_calls': total_calls,
                'completed_calls': completed_calls,
                'failed_calls': failed_calls,
                'total_duration': total_duration,
                'average_duration': average_duration,
                'categories_stats': categories_stats
            }
        )
        
        return report
    
    def update_user_stats(self, user):
        """
        Обновляет статистику пользователя.
        
        Args:
            user: Объект пользователя
        """
        calls = Call.objects.filter(user=user)
        
        total_calls = calls.count()
        total_duration = calls.aggregate(Sum('duration'))['duration__sum'] or 0
        last_call = calls.order_by('-created_at').first()
        
        UserStats.objects.update_or_create(
            user=user,
            defaults={
                'total_calls': total_calls,
                'total_duration': total_duration,
                'last_call_date': last_call.created_at if last_call else None
            }
        )
