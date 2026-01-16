"""
Views для аналитики и статистики.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta

from .models import DailyReport, UserStats
from .serializers import DailyReportSerializer, UserStatsSerializer
from calls.models import Call, CallAnalysis


class AnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet для получения аналитических данных.
    """
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Общая статистика",
        responses={200: dict}
    )
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """
        Возвращает общую статистику по звонкам.
        """
        user = request.user
        
        # Определяем queryset в зависимости от роли
        if user.is_admin():
            calls = Call.objects.all()
        else:
            calls = Call.objects.filter(user=user)
        
        # Статистика за последние 30 дней
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_calls = calls.filter(created_at__gte=thirty_days_ago)
        
        stats = {
            'total_calls': calls.count(),
            'completed_calls': calls.filter(status='completed').count(),
            'pending_calls': calls.filter(status='pending').count(),
            'failed_calls': calls.filter(status='failed').count(),
            'recent_calls': recent_calls.count(),
            'total_duration': calls.aggregate(Sum('duration'))['duration__sum'] or 0,
            'average_duration': calls.aggregate(Avg('duration'))['duration__avg'] or 0,
        }
        
        return Response(stats)
    
    @extend_schema(
        summary="Статистика по категориям",
        responses={200: dict}
    )
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """
        Возвращает статистику по категориям звонков.
        """
        user = request.user
        
        if user.is_admin():
            analyses = CallAnalysis.objects.all()
        else:
            analyses = CallAnalysis.objects.filter(call__user=user)
        
        # Подсчет по категориям
        categories_data = analyses.values('category').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response(categories_data)
    
    @extend_schema(
        summary="Статистика по дням",
        parameters=[
            OpenApiParameter('days', int, description='Количество дней (по умолчанию 30)'),
        ],
        responses={200: list}
    )
    @action(detail=False, methods=['get'])
    def daily_stats(self, request):
        """
        Возвращает статистику по дням за указанный период.
        """
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        user = request.user
        
        if user.is_admin():
            calls = Call.objects.all()
        else:
            calls = Call.objects.filter(user=user)
        
        # Группируем по дням
        daily_data = calls.filter(
            created_at__date__gte=start_date
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            count=Count('id'),
            avg_duration=Avg('duration')
        ).order_by('day')
        
        return Response(daily_data)
    
    @extend_schema(
        summary="Топ ключевых слов",
        parameters=[
            OpenApiParameter('limit', int, description='Количество слов (по умолчанию 20)'),
        ],
        responses={200: list}
    )
    @action(detail=False, methods=['get'])
    def top_keywords(self, request):
        """
        Возвращает топ ключевых слов из анализов.
        """
        limit = int(request.query_params.get('limit', 20))
        user = request.user
        
        if user.is_admin():
            analyses = CallAnalysis.objects.all()
        else:
            analyses = CallAnalysis.objects.filter(call__user=user)
        
        # Собираем все ключевые слова
        all_keywords = {}
        for analysis in analyses:
            for keyword in analysis.keywords:
                all_keywords[keyword] = all_keywords.get(keyword, 0) + 1
        
        # Сортируем и ограничиваем
        sorted_keywords = sorted(
            all_keywords.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return Response([
            {'keyword': k, 'count': v}
            for k, v in sorted_keywords
        ])


class DailyReportViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра ежедневных отчетов (только для админов).
    """
    
    queryset = DailyReport.objects.all()
    serializer_class = DailyReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Ограничивает доступ только для админов."""
        user = self.request.user
        if not user.is_admin():
            return DailyReport.objects.none()
        return DailyReport.objects.all()


class UserStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра статистики пользователей.
    """
    
    queryset = UserStats.objects.all()
    serializer_class = UserStatsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Возвращает статистику пользователя или всех для админа."""
        user = self.request.user
        if user.is_admin():
            return UserStats.objects.all()
        return UserStats.objects.filter(user=user)
