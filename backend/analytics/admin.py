"""
Админ панель для аналитики.
"""
from django.contrib import admin
from .models import DailyReport, UserStats


@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    """Админ панель для модели DailyReport."""
    
    list_display = ('date', 'total_calls', 'completed_calls', 'failed_calls', 'average_duration')
    list_filter = ('date',)
    readonly_fields = ('created_at',)


@admin.register(UserStats)
class UserStatsAdmin(admin.ModelAdmin):
    """Админ панель для модели UserStats."""
    
    list_display = ('user', 'total_calls', 'total_duration', 'last_call_date')
    search_fields = ('user__username',)
    readonly_fields = ('updated_at',)
