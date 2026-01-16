"""
Вспомогательные функции для Telegram бота.
"""
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async

User = get_user_model()


@sync_to_async
def get_or_create_user(telegram_id, username, first_name, last_name):
    """
    Получает или создает пользователя по Telegram ID.
    """
    user, created = User.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            'username': username or f'tg_{telegram_id}',
            'telegram_username': username,
            'first_name': first_name,
            'last_name': last_name,
        }
    )
    return user, created


def format_call_info(call):
    """
    Форматирует информацию о звонке для отображения.
    """
    status_emoji = {
        'pending': '⏳',
        'processing': '🔄',
        'completed': '✅',
        'failed': '❌'
    }.get(call.status, '❓')
    
    info_text = f"""
📞 <b>Информация о звонке</b>

🆔 ID: <code>{call.id}</code>
{status_emoji} Статус: {call.get_status_display()}
📅 Дата: {call.created_at.strftime('%d.%m.%Y %H:%M')}
⏱ Длительность: {call.duration or 0:.1f} сек
🌐 Язык: {call.language.upper()}
📱 Источник: {call.get_source_display()}
"""
    
    if hasattr(call, 'transcription'):
        info_text += f"\n✅ Транскрипция: Готова"
        info_text += f"\n🎯 Уверенность: {call.transcription.confidence:.1f}%"
    else:
        info_text += f"\n⏳ Транскрипция: В процессе"
    
    if hasattr(call, 'analysis'):
        info_text += f"\n✅ Анализ: Готов"
        if call.analysis.category:
            info_text += f"\n📁 Категория: {call.analysis.get_category_display()}"
    else:
        info_text += f"\n⏳ Анализ: В процессе"
    
    return info_text


def format_statistics(stats, categories):
    """
    Форматирует статистику для отображения.
    """
    stats_text = f"""
📊 <b>Ваша статистика</b>

📞 Всего звонков: {stats['total_calls']}
✅ Завершено: {stats['completed']}
⏳ В обработке: {stats['pending']}
❌ Ошибок: {stats['failed']}

⏱ Общая длительность: {stats['total_duration']:.1f} сек
📈 Средняя длительность: {stats['avg_duration']:.1f} сек
"""
    
    if categories:
        stats_text += "\n📁 <b>По категориям:</b>\n"
        for cat in categories[:5]:
            category_name = {
                'complaint': '😠 Жалобы',
                'order': '🛒 Заказы',
                'support': '💬 Поддержка',
                'inquiry': '❓ Запросы',
                'other': '📋 Другое'
            }.get(cat['category'], cat['category'])
            
            stats_text += f"  {category_name}: {cat['count']}\n"
    
    return stats_text


async def download_file(bot, file_id):
    """
    Скачивает файл из Telegram.
    """
    file = await bot.get_file(file_id)
    return await bot.download_file(file.file_path)
