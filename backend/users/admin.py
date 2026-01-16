"""
Админ панель для управления пользователями.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админ панель для модели User."""
    
    list_display = ('username', 'email', 'role', 'telegram_id', 'notifications_enabled', 'created_at')
    list_filter = ('role', 'notifications_enabled', 'is_active')
    search_fields = ('username', 'email', 'telegram_username')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'telegram_id', 'telegram_username', 'phone', 'notifications_enabled')
        }),
    )
