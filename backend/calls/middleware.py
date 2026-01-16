"""
Middleware для WebSocket аутентификации.
"""
from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token_string):
    """
    Получает пользователя из JWT токена.
    """
    try:
        token = AccessToken(token_string)
        user_id = token.payload.get('user_id')
        user = User.objects.get(id=user_id)
        return user
    except Exception as e:
        logger.error(f"Ошибка аутентификации токена: {e}")
        return AnonymousUser()


class JWTAuthMiddleware:
    """
    Middleware для аутентификации WebSocket соединений через JWT токен.
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        # Получаем токен из query string
        query_string = scope.get('query_string', b'').decode()
        params = dict(x.split('=') for x in query_string.split('&') if '=' in x)
        token = params.get('token')
        
        if token:
            scope['user'] = await get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()
        
        return await self.app(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    """
    Создает middleware stack с JWT аутентификацией.
    """
    return JWTAuthMiddleware(AuthMiddlewareStack(inner))
