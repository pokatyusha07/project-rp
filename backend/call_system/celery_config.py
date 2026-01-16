"""
Конфигурация периодических задач Celery Beat.
"""
from celery.schedules import crontab

# Периодические задачи
beat_schedule = {
    # Генерация ежедневного отчета каждый день в 00:30
    'generate-daily-report': {
        'task': 'calls.tasks.generate_daily_report_task',
        'schedule': crontab(hour=0, minute=30),
    },
}
