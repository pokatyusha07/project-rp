"""
Конфигурация Celery для асинхронной обработки задач.
"""
import os
from celery import Celery

# Устанавливаем модуль настроек Django по умолчанию
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'call_system.settings')

app = Celery('call_system')

# Загружаем конфигурацию из настроек Django с префиксом CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим задачи во всех приложениях Django
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """Тестовая задача для отладки."""
    print(f'Request: {self.request!r}')
