"""
Команда для очистки старых звонков.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from calls.models import Call
import os


class Command(BaseCommand):
    """
    Удаляет старые звонки и их файлы.
    """
    
    help = 'Удаляет звонки старше указанного количества дней'
    
    def add_arguments(self, parser):
        """Добавляет аргументы команды."""
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Количество дней для хранения звонков (по умолчанию 90)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Только показать, что будет удалено'
        )
    
    def handle(self, *args, **options):
        """Выполняет команду."""
        days = options['days']
        dry_run = options['dry_run']
        
        threshold = timezone.now() - timedelta(days=days)
        
        # Находим старые звонки
        old_calls = Call.objects.filter(created_at__lt=threshold)
        count = old_calls.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('Старых звонков не найдено')
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f'Найдено {count} звонков старше {days} дней')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.NOTICE('Режим dry-run: звонки не будут удалены')
            )
            for call in old_calls[:10]:
                self.stdout.write(f'  - {call.id} ({call.created_at})')
            return
        
        # Удаляем файлы и записи
        deleted_files = 0
        for call in old_calls:
            if call.audio_file:
                try:
                    if os.path.exists(call.audio_file.path):
                        os.remove(call.audio_file.path)
                        deleted_files += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Ошибка удаления файла {call.id}: {e}')
                    )
        
        old_calls.delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Успешно удалено {count} звонков и {deleted_files} файлов'
            )
        )
