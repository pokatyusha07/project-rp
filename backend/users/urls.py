"""
URL маршруты для пользователей.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UserViewSet,
    RegisterView,
    LoginView,
    TelegramAuthView
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')

urlpatterns = [
    # Аутентификация
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('telegram-auth/', TelegramAuthView.as_view(), name='telegram-auth'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # User endpoints
    path('', include(router.urls)),
]
