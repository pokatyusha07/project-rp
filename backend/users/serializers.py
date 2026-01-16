"""
Сериализаторы для работы с пользователями.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User.
    """
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'telegram_id', 'telegram_username', 'phone',
            'notifications_enabled', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя.
    """
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = (
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone'
        )
    
    def validate(self, data):
        """Проверяет совпадение паролей."""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        return data
    
    def create(self, validated_data):
        """Создает нового пользователя с хешированным паролем."""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Сериализатор для входа пользователя.
    """
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """Проверяет учетные данные пользователя."""
        user = authenticate(
            username=data['username'],
            password=data['password']
        )
        
        if not user:
            raise serializers.ValidationError("Неверные учетные данные")
        
        if not user.is_active:
            raise serializers.ValidationError("Аккаунт деактивирован")
        
        data['user'] = user
        return data


class TelegramAuthSerializer(serializers.Serializer):
    """
    Сериализатор для авторизации через Telegram.
    """
    
    telegram_id = serializers.IntegerField()
    telegram_username = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
