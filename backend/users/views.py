"""
Views для работы с пользователями и аутентификацией.
"""
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.contrib.auth import get_user_model

from .models import User
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    TelegramAuthSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления пользователями.
    Поддерживает CRUD операции и дополнительные действия.
    """
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Ограничивает queryset в зависимости от роли пользователя."""
        user = self.request.user
        if user.is_admin():
            return User.objects.all()
        return User.objects.filter(id=user.id)
    
    @extend_schema(
        summary="Получить профиль текущего пользователя",
        responses={200: UserSerializer}
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Возвращает профиль текущего пользователя."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Обновить профиль текущего пользователя",
        request=UserSerializer,
        responses={200: UserSerializer}
    )
    @action(detail=False, methods=['patch'])
    def update_profile(self, request):
        """Обновляет профиль текущего пользователя."""
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class RegisterView(generics.CreateAPIView):
    """
    Регистрация нового пользователя.
    """
    
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
    @extend_schema(
        summary="Регистрация нового пользователя",
        request=UserRegistrationSerializer,
        responses={201: UserSerializer}
    )
    def post(self, request, *args, **kwargs):
        """Создает нового пользователя и возвращает JWT токены."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Генерируем JWT токены
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    """
    Вход пользователя в систему.
    """
    
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer
    
    @extend_schema(
        summary="Вход пользователя",
        request=UserLoginSerializer,
        responses={200: dict}
    )
    def post(self, request, *args, **kwargs):
        """Аутентифицирует пользователя и возвращает JWT токены."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


class TelegramAuthView(generics.GenericAPIView):
    """
    Авторизация через Telegram.
    """
    
    permission_classes = [AllowAny]
    serializer_class = TelegramAuthSerializer
    
    @extend_schema(
        summary="Авторизация через Telegram",
        request=TelegramAuthSerializer,
        responses={200: dict}
    )
    def post(self, request, *args, **kwargs):
        """
        Авторизует пользователя через Telegram ID.
        Создает нового пользователя, если он не существует.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        telegram_id = serializer.validated_data['telegram_id']
        
        # Ищем пользователя по Telegram ID
        user, created = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                'username': f'tg_{telegram_id}',
                'telegram_username': serializer.validated_data.get('telegram_username'),
                'first_name': serializer.validated_data.get('first_name', ''),
                'last_name': serializer.validated_data.get('last_name', ''),
            }
        )
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'created': created
        })
