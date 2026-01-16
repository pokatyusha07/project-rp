"""
URL маршруты для аналитики.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AnalyticsViewSet, DailyReportViewSet, UserStatsViewSet

router = DefaultRouter()
router.register('stats', AnalyticsViewSet, basename='analytics')
router.register('reports', DailyReportViewSet, basename='report')
router.register('user-stats', UserStatsViewSet, basename='user-stats')

urlpatterns = [
    path('', include(router.urls)),
]
