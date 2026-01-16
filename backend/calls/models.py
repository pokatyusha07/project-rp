"""
Модели для хранения звонков, транскрипций и анализа.
"""
from django.db import models
from django.conf import settings
import uuid


class Call(models.Model):
    """
    Модель звонка с аудио файлом.
    """
    
    STATUS_CHOICES = (
        ('pending', 'Ожидает обработки'),
        ('processing', 'Обрабатывается'),
        ('completed', 'Завершено'),
        ('failed', 'Ошибка'),
    )
    
    SOURCE_CHOICES = (
        ('web', 'Веб интерфейс'),
        ('telegram', 'Telegram'),
        ('api', 'API'),
    )
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='calls',
        verbose_name='Пользователь'
    )
    
    audio_file = models.FileField(
        upload_to='calls/%Y/%m/%d/',
        verbose_name='Аудио файл'
    )
    
    duration = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Длительность (сек)'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default='web',
        verbose_name='Источник'
    )
    
    language = models.CharField(
        max_length=5,
        default='ru',
        verbose_name='Язык'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'Звонок'
        verbose_name_plural = 'Звонки'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Звонок {self.id} от {self.user.username}"


class Transcription(models.Model):
    """
    Модель транскрипции звонка.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    call = models.OneToOneField(
        Call,
        on_delete=models.CASCADE,
        related_name='transcription',
        verbose_name='Звонок'
    )
    
    text = models.TextField(
        verbose_name='Текст транскрипции'
    )
    
    confidence = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Уверенность (%)'
    )
    
    segments = models.JSONField(
        default=list,
        verbose_name='Сегменты'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    class Meta:
        verbose_name = 'Транскрипция'
        verbose_name_plural = 'Транскрипции'
    
    def __str__(self):
        return f"Транскрипция {self.call.id}"


class CallAnalysis(models.Model):
    """
    Модель анализа звонка с NLP обработкой.
    """
    
    CATEGORY_CHOICES = (
        ('complaint', 'Жалоба'),
        ('order', 'Заказ'),
        ('support', 'Поддержка'),
        ('inquiry', 'Запрос'),
        ('other', 'Другое'),
    )
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    call = models.OneToOneField(
        Call,
        on_delete=models.CASCADE,
        related_name='analysis',
        verbose_name='Звонок'
    )
    
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        null=True,
        blank=True,
        verbose_name='Категория'
    )
    
    keywords = models.JSONField(
        default=list,
        verbose_name='Ключевые слова'
    )
    
    sentiment = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='Тональность'
    )
    
    word_frequency = models.JSONField(
        default=dict,
        verbose_name='Частота слов'
    )
    
    speaker_stats = models.JSONField(
        default=dict,
        verbose_name='Статистика говорящих'
    )
    
    summary = models.TextField(
        null=True,
        blank=True,
        verbose_name='Краткое содержание'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    class Meta:
        verbose_name = 'Анализ звонка'
        verbose_name_plural = 'Анализы звонков'
    
    def __str__(self):
        return f"Анализ {self.call.id}"


class CallNote(models.Model):
    """
    Заметки к звонку от пользователя.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    call = models.ForeignKey(
        Call,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name='Звонок'
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    
    text = models.TextField(
        verbose_name='Текст заметки'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    class Meta:
        verbose_name = 'Заметка'
        verbose_name_plural = 'Заметки'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заметка к {self.call.id}"
