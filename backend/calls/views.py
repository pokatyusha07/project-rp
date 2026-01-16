"""
Views для работы со звонками.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db.models import Q

from .models import Call, Transcription, CallAnalysis, CallNote
from .serializers import (
    CallSerializer,
    CallListSerializer,
    CallUploadSerializer,
    TranscriptionSerializer,
    CallAnalysisSerializer,
    CallNoteSerializer
)
from .tasks import process_call_task


class CallViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления звонками.
    Поддерживает загрузку, просмотр и поиск звонков.
    """
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'source', 'language']
    search_fields = ['transcription__text']
    ordering_fields = ['created_at', 'duration']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Возвращает звонки пользователя или все для админа."""
        user = self.request.user
        if user.is_admin():
            return Call.objects.all().select_related(
                'user', 'transcription', 'analysis'
            ).prefetch_related('notes')
        return Call.objects.filter(user=user).select_related(
            'user', 'transcription', 'analysis'
        ).prefetch_related('notes')
    
    def get_serializer_class(self):
        """Возвращает соответствующий сериализатор."""
        if self.action == 'list':
            return CallListSerializer
        elif self.action == 'upload':
            return CallUploadSerializer
        return CallSerializer
    
    @extend_schema(
        summary="Загрузить аудио файл",
        request=CallUploadSerializer,
        responses={201: CallSerializer}
    )
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """
        Загружает аудио файл и запускает процесс транскрипции.
        """
        serializer = CallUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Создаем запись звонка
        call = serializer.save(user=request.user, status='pending')
        
        # Запускаем асинхронную обработку
        process_call_task.delay(str(call.id))
        
        return Response(
            CallSerializer(call).data,
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        summary="Получить транскрипцию звонка",
        responses={200: TranscriptionSerializer}
    )
    @action(detail=True, methods=['get'])
    def transcription(self, request, pk=None):
        """Возвращает транскрипцию звонка."""
        call = self.get_object()
        
        if not hasattr(call, 'transcription'):
            return Response(
                {'detail': 'Транскрипция еще не готова'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = TranscriptionSerializer(call.transcription)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Получить анализ звонка",
        responses={200: CallAnalysisSerializer}
    )
    @action(detail=True, methods=['get'])
    def analysis(self, request, pk=None):
        """Возвращает анализ звонка."""
        call = self.get_object()
        
        if not hasattr(call, 'analysis'):
            return Response(
                {'detail': 'Анализ еще не готов'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = CallAnalysisSerializer(call.analysis)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Добавить заметку к звонку",
        request=CallNoteSerializer,
        responses={201: CallNoteSerializer}
    )
    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        """Добавляет заметку к звонку."""
        call = self.get_object()
        
        serializer = CallNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, call=call)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="Поиск по звонкам",
        parameters=[
            OpenApiParameter('q', str, description='Поисковый запрос'),
            OpenApiParameter('category', str, description='Категория'),
        ],
        responses={200: CallListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Поиск по транскрипциям звонков.
        """
        query = request.query_params.get('q', '')
        category = request.query_params.get('category', '')
        
        queryset = self.get_queryset()
        
        if query:
            queryset = queryset.filter(
                Q(transcription__text__icontains=query) |
                Q(analysis__keywords__icontains=query)
            )
        
        if category:
            queryset = queryset.filter(analysis__category=category)
        
        serializer = CallListSerializer(queryset, many=True)
        return Response(serializer.data)


class CallNoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления заметками к звонкам.
    """
    
    serializer_class = CallNoteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Возвращает заметки пользователя."""
        return CallNote.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Автоматически устанавливает пользователя."""
        serializer.save(user=self.request.user)
