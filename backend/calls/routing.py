"""
WebSocket маршруты для real-time обновлений транскрипции.
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/transcription/(?P<call_id>[0-9a-f-]+)/$', consumers.TranscriptionConsumer.as_asgi()),
    re_path(r'ws/calls/$', consumers.CallsConsumer.as_asgi()),
]
