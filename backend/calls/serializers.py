"""
Сериализаторы для работы со звонками.
"""
from rest_framework import serializers
from .models import Call, Transcription, CallAnalysis, CallNote


class TranscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для транскрипции звонка.
    """
    
    class Meta:
        model = Transcription
        fields = (
            'id', 'call', 'text', 'confidence',
            'segments', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class CallAnalysisSerializer(serializers.ModelSerializer):
    """
    Сериализатор для анализа звонка.
    """
    
    category_display = serializers.CharField(
        source='get_category_display',
        read_only=True
    )
    
    class Meta:
        model = CallAnalysis
        fields = (
            'id', 'call', 'category', 'category_display',
            'keywords', 'sentiment', 'word_frequency',
            'speaker_stats', 'summary', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class CallNoteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для заметок к звонку.
    """
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = CallNote
        fields = ('id', 'call', 'user', 'user_name', 'text', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')


class CallSerializer(serializers.ModelSerializer):
    """
    Сериализатор для звонка.
    """
    
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    source_display = serializers.CharField(
        source='get_source_display',
        read_only=True
    )
    user_name = serializers.CharField(source='user.username', read_only=True)
    transcription = TranscriptionSerializer(read_only=True)
    analysis = CallAnalysisSerializer(read_only=True)
    notes = CallNoteSerializer(many=True, read_only=True)
    
    class Meta:
        model = Call
        fields = (
            'id', 'user', 'user_name', 'audio_file', 'duration',
            'status', 'status_display', 'source', 'source_display',
            'language', 'transcription', 'analysis', 'notes',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'duration', 'status', 'created_at', 'updated_at')


class CallUploadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для загрузки звонка.
    """
    
    class Meta:
        model = Call
        fields = ('audio_file', 'language', 'source')
    
    def validate_audio_file(self, value):
        """Проверяет размер и формат аудио файла."""
        # Проверка размера файла
        if value.size > 100 * 1024 * 1024:  # 100MB
            raise serializers.ValidationError(
                "Размер файла не должен превышать 100MB"
            )
        
        # Проверка расширения файла
        allowed_extensions = ['.mp3', '.wav', '.ogg', '.m4a', '.flac']
        ext = value.name.lower().split('.')[-1]
        if f'.{ext}' not in allowed_extensions:
            raise serializers.ValidationError(
                f"Поддерживаемые форматы: {', '.join(allowed_extensions)}"
            )
        
        return value


class CallListSerializer(serializers.ModelSerializer):
    """
    Упрощенный сериализатор для списка звонков.
    """
    
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    user_name = serializers.CharField(source='user.username', read_only=True)
    has_transcription = serializers.SerializerMethodField()
    has_analysis = serializers.SerializerMethodField()
    
    class Meta:
        model = Call
        fields = (
            'id', 'user_name', 'duration', 'status', 'status_display',
            'language', 'source', 'has_transcription', 'has_analysis',
            'created_at'
        )
    
    def get_has_transcription(self, obj):
        """Проверяет наличие транскрипции."""
        return hasattr(obj, 'transcription')
    
    def get_has_analysis(self, obj):
        """Проверяет наличие анализа."""
        return hasattr(obj, 'analysis')
