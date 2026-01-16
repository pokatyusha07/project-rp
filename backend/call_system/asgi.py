"""
ASGI конфигурация для поддержки WebSocket соединений.
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'call_system.settings')

django_asgi_app = get_asgi_application()

# Импорт routing и middleware после инициализации Django
from calls import routing as calls_routing
from calls.middleware import JWTAuthMiddlewareStack

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddlewareStack(
            URLRouter(
                calls_routing.websocket_urlpatterns
            )
        )
    ),
})
