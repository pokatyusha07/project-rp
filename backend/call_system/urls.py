"""
URL конфигурация для системы обработки звонков.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .health_check import HealthCheckView, MetricsView

urlpatterns = [
    # Админ панель Django
    path('admin/', admin.site.urls),
    
    # Health check и метрики
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('metrics/', MetricsView.as_view(), name='metrics'),
    
    # API эндпоинты
    path('api/users/', include('users.urls')),
    path('api/calls/', include('calls.urls')),
    path('api/analytics/', include('analytics.urls')),
    
    # Swagger документация
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Добавляем медиа файлы в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
