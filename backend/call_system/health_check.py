"""
Health check endpoint для мониторинга.
"""
from django.http import JsonResponse
from django.views import View
from .monitoring import SystemMonitor


class HealthCheckView(View):
    """
    Endpoint для проверки здоровья системы.
    """
    
    def get(self, request):
        """Возвращает статус здоровья системы."""
        health = SystemMonitor.get_system_health()
        
        status_code = 200 if health['status'] == 'healthy' else 503
        
        return JsonResponse(health, status=status_code)


class MetricsView(View):
    """
    Endpoint для метрик производительности.
    """
    
    def get(self, request):
        """Возвращает метрики производительности."""
        metrics = SystemMonitor.get_performance_metrics()
        return JsonResponse(metrics)
