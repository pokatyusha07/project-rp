"""
Главный пакет Django приложения для системы обработки звонков.
"""
from .celery import app as celery_app

__all__ = ('celery_app',)
