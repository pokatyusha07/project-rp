"""
Конфигурация приложения calls.
"""
from django.apps import AppConfig


class CallsConfig(AppConfig):
    """Конфигурация для приложения обработки звонков."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calls'
    verbose_name = 'Звонки'
    
    def ready(self):
        """
        Импортирует signals при запуске приложения.
        """
        import calls.signals
