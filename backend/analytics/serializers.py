"""
Сериализаторы для аналитики.
"""
from rest_framework import serializers
from .models import DailyReport, UserStats


class DailyReportSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ежедневного отчета.
    """
    
    class Meta:
        model = DailyReport
        fields = (
            'date', 'total_calls', 'completed_calls', 'failed_calls',
            'total_duration', 'average_duration', 'categories_stats',
            'created_at'
        )


class UserStatsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для статистики пользователя.
    """
    
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserStats
        fields = (
            'user', 'username', 'total_calls', 'total_duration',
            'last_call_date', 'updated_at'
        )
