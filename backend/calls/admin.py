"""
Админ панель для управления звонками.
"""
from django.contrib import admin
from .models import Call, Transcription, CallAnalysis, CallNote


@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    """Админ панель для модели Call."""
    
    list_display = ('id', 'user', 'status', 'source', 'language', 'duration', 'created_at')
    list_filter = ('status', 'source', 'language', 'created_at')
    search_fields = ('id', 'user__username')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Transcription)
class TranscriptionAdmin(admin.ModelAdmin):
    """Админ панель для модели Transcription."""
    
    list_display = ('id', 'call', 'confidence', 'created_at')
    search_fields = ('call__id', 'text')
    readonly_fields = ('id', 'created_at')


@admin.register(CallAnalysis)
class CallAnalysisAdmin(admin.ModelAdmin):
    """Админ панель для модели CallAnalysis."""
    
    list_display = ('id', 'call', 'category', 'sentiment', 'created_at')
    list_filter = ('category', 'sentiment')
    search_fields = ('call__id', 'summary')
    readonly_fields = ('id', 'created_at')


@admin.register(CallNote)
class CallNoteAdmin(admin.ModelAdmin):
    """Админ панель для модели CallNote."""
    
    list_display = ('id', 'call', 'user', 'created_at')
    search_fields = ('call__id', 'user__username', 'text')
    readonly_fields = ('id', 'created_at')
