"""
Модели для хранения аналитических данных.
"""
from django.db import models
from django.conf import settings


class DailyReport(models.Model):
    """
    Ежедневный отчет по звонкам.
    """
    
    date = models.DateField(
        unique=True,
        verbose_name='Дата'
    )
    
    total_calls = models.IntegerField(
        default=0,
        verbose_name='Всего звонков'
    )
    
    completed_calls = models.IntegerField(
        default=0,
        verbose_name='Завершенных звонков'
    )
    
    failed_calls = models.IntegerField(
        default=0,
        verbose_name='Ошибок обработки'
    )
    
    total_duration = models.FloatField(
        default=0,
        verbose_name='Общая длительность (сек)'
    )
    
    average_duration = models.FloatField(
        default=0,
        verbose_name='Средняя длительность (сек)'
    )
    
    categories_stats = models.JSONField(
        default=dict,
        verbose_name='Статистика по категориям'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    class Meta:
        verbose_name = 'Ежедневный отчет'
        verbose_name_plural = 'Ежедневные отчеты'
        ordering = ['-date']
    
    def __str__(self):
        return f"Отчет за {self.date}"


class UserStats(models.Model):
    """
    Статистика пользователя.
    """
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stats',
        verbose_name='Пользователь'
    )
    
    total_calls = models.IntegerField(
        default=0,
        verbose_name='Всего звонков'
    )
    
    total_duration = models.FloatField(
        default=0,
        verbose_name='Общая длительность (сек)'
    )
    
    last_call_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Последний звонок'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'Статистика пользователя'
        verbose_name_plural = 'Статистика пользователей'
    
    def __str__(self):
        return f"Статистика {self.user.username}"
