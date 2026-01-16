"""
URL маршруты для звонков.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CallViewSet, CallNoteViewSet

router = DefaultRouter()
router.register('calls', CallViewSet, basename='call')
router.register('notes', CallNoteViewSet, basename='note')

urlpatterns = [
    path('', include(router.urls)),
]
