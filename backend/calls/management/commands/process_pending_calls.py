"""
Команда для обработки зависших звонков.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from calls.models import Call
from calls.tasks import process_call_task


class Command(BaseCommand):
    """
    Обрабатывает звонки, которые зависли в статусе processing.
    """
    
    help = 'Обрабатывает зависшие звонки'
    
    def add_arguments(self, parser):
        """Добавляет аргументы команды."""
        parser.add_argument(
            '--timeout',
            type=int,
            default=30,
            help='Таймаут в минутах для определения зависшего звонка'
        )
    
    def handle(self, *args, **options):
        """Выполняет команду."""
        timeout = options['timeout']
        threshold = timezone.now() - timedelta(minutes=timeout)
        
        # Находим зависшие звонки
        stuck_calls = Call.objects.filter(
            status='processing',
            updated_at__lt=threshold
        )
        
        count = stuck_calls.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('Зависших звонков не найдено')
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f'Найдено {count} зависших звонков')
        )
        
        # Перезапускаем обработку
        for call in stuck_calls:
            self.stdout.write(f'Перезапуск обработки звонка {call.id}')
            call.status = 'pending'
            call.save()
            
            # Запускаем задачу
            process_call_task.delay(str(call.id))
        
        self.stdout.write(
            self.style.SUCCESS(f'Успешно перезапущено {count} звонков')
        )
