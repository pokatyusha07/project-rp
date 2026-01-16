"""
WSGI конфигурация для стандартных HTTP запросов.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'call_system.settings')

application = get_wsgi_application()
