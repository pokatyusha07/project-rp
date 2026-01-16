"""
Обработчики команд и сообщений Telegram бота.
"""
import logging
from aiogram import types
from aiogram.fsm.context import FSMContext
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
import tempfile
import os

from .keyboards import (
    get_main_keyboard,
    get_calls_keyboard,
    get_call_detail_keyboard,
    get_settings_keyboard
)
from .utils import (
    get_or_create_user,
    format_call_info,
    format_statistics,
    download_file
)

User = get_user_model()
logger = logging.getLogger(__name__)


async def start_handler(message: types.Message):
    """
    Обработчик команды /start.
    Приветствует пользователя и регистрирует его в системе.
    """
    telegram_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    
    # Получаем или создаем пользователя
    user, created = await get_or_create_user(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name
    )
    
    welcome_text = f"""
👋 Добро пожаловать в систему обработки звонков!

{'🎉 Вы успешно зарегистрированы!' if created else 'С возвращением!'}

📱 Что я могу делать:
• 🎤 Отправьте мне голосовое сообщение - я его транскрибирую
• 📊 Посмотрите статистику по вашим звонкам
• 🔍 Ищите по транскрипциям
• 📝 Получайте уведомления о готовности обработки

Используйте кнопки ниже или команды:
/help - помощь
/calls - мои звонки
/stats - статистика
/search - поиск
/settings - настройки
"""
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard()
    )


async def help_handler(message: types.Message):
    """
    Обработчик команды /help.
    Показывает справку по использованию бота.
    """
    help_text = """
📖 Справка по использованию бота

🎤 <b>Загрузка звонков:</b>
Просто отправьте голосовое сообщение или аудио файл.
Бот автоматически:
• Транскрибирует речь
• Проанализирует содержание
• Выделит ключевые слова
• Определит категорию и тональность

📋 <b>Команды:</b>
/start - Начать работу
/calls - Список ваших звонков
/stats - Статистика
/search - Поиск по звонкам
/settings - Настройки уведомлений
/cancel - Отменить текущую операцию

🔍 <b>Поиск:</b>
Используйте /search и введите ключевое слово
для поиска по транскрипциям звонков.

⚙️ <b>Настройки:</b>
/settings - включить/выключить уведомления
о готовности транскрипции.

💡 <b>Совет:</b>
Говорите четко для лучшего качества
распознавания речи!
"""
    
    await message.answer(help_text, parse_mode="HTML")


async def register_handler(message: types.Message):
    """
    Обработчик команды /register.
    Регистрирует пользователя в системе.
    """
    telegram_id = message.from_user.id
    
    # Проверяем, существует ли пользователь
    user = await sync_to_async(User.objects.filter(telegram_id=telegram_id).first)()
    
    if user:
        await message.answer("✅ Вы уже зарегистрированы в системе!")
    else:
        # Создаем пользователя
        user, created = await get_or_create_user(
            telegram_id=telegram_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name or "",
            last_name=message.from_user.last_name or ""
        )
        
        if created:
            await message.answer("🎉 Регистрация успешно завершена!")
        else:
            await message.answer("✅ Вы уже зарегистрированы!")


async def upload_voice_handler(message: types.Message):
    """
    Обработчик голосовых сообщений и аудио файлов.
    Загружает файл и запускает процесс транскрипции.
    """
    telegram_id = message.from_user.id
    
    # Получаем пользователя
    user = await sync_to_async(User.objects.filter(telegram_id=telegram_id).first)()
    
    if not user:
        await message.answer(
            "❌ Вы не зарегистрированы. Используйте /start для регистрации."
        )
        return
    
    # Определяем тип файла
    if message.voice:
        file_id = message.voice.file_id
        file_type = "voice"
        duration = message.voice.duration
    elif message.audio:
        file_id = message.audio.file_id
        file_type = "audio"
        duration = message.audio.duration
    else:
        await message.answer("❌ Неподдерживаемый тип файла.")
        return
    
    # Отправляем подтверждение
    status_message = await message.answer("⏳ Загружаю файл...")
    
    try:
        # Скачиваем файл
        from aiogram import Bot
        bot = message.bot
        file = await bot.get_file(file_id)
        
        # Создаем временный файл
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix='.ogg' if file_type == 'voice' else '.mp3'
        )
        
        await bot.download_file(file.file_path, temp_file.name)
        
        # Создаем запись звонка
        from calls.models import Call
        from calls.tasks import process_call_task
        from django.core.files import File
        
        with open(temp_file.name, 'rb') as audio_file:
            call = await sync_to_async(Call.objects.create)(
                user=user,
                audio_file=File(audio_file, name=f'telegram_{file_id}.ogg'),
                source='telegram',
                language='ru',
                status='pending'
            )
        
        # Удаляем временный файл
        os.unlink(temp_file.name)
        
        # Запускаем обработку
        process_call_task.delay(str(call.id))
        
        # Обновляем сообщение
        await status_message.edit_text(
            f"✅ Файл загружен!\n"
            f"🆔 ID звонка: {call.id}\n"
            f"⏱ Длительность: {duration} сек\n\n"
            f"⏳ Обработка началась...\n"
            f"Вы получите уведомление, когда транскрипция будет готова."
        )
        
        logger.info(f"Звонок {call.id} создан пользователем {user.username} через Telegram")
        
    except Exception as e:
        logger.error(f"Ошибка загрузки файла: {e}")
        await status_message.edit_text(
            f"❌ Произошла ошибка при загрузке файла.\n"
            f"Попробуйте еще раз позже."
        )


async def my_calls_handler(message: types.Message, page: int = 1):
    """
    Обработчик команды /calls.
    Показывает список звонков пользователя.
    """
    telegram_id = message.from_user.id
    
    # Получаем пользователя
    user = await sync_to_async(User.objects.filter(telegram_id=telegram_id).first)()
    
    if not user:
        await message.answer("❌ Вы не зарегистрированы. Используйте /start")
        return
    
    # Получаем звонки пользователя
    from calls.models import Call
    
    calls = await sync_to_async(
        lambda: list(
            Call.objects.filter(user=user)
            .order_by('-created_at')[:10]
        )
    )()
    
    if not calls:
        await message.answer(
            "📭 У вас пока нет звонков.\n\n"
            "Отправьте голосовое сообщение для создания первого звонка!"
        )
        return
    
    # Формируем список звонков
    calls_text = "📞 <b>Ваши звонки:</b>\n\n"
    
    for i, call in enumerate(calls, 1):
        status_emoji = {
            'pending': '⏳',
            'processing': '🔄',
            'completed': '✅',
            'failed': '❌'
        }.get(call.status, '❓')
        
        calls_text += (
            f"{i}. {status_emoji} <b>ID:</b> <code>{call.id}</code>\n"
            f"   📅 {call.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"   📊 Статус: {call.get_status_display()}\n\n"
        )
    
    await message.answer(
        calls_text,
        parse_mode="HTML",
        reply_markup=get_calls_keyboard(calls)
    )


async def call_detail_handler(call_id: str, message: types.Message):
    """
    Показывает детальную информацию о звонке.
    """
    telegram_id = message.from_user.id
    
    # Получаем пользователя
    user = await sync_to_async(User.objects.filter(telegram_id=telegram_id).first)()
    
    if not user:
        await message.answer("❌ Вы не зарегистрированы.")
        return
    
    # Получаем звонок
    from calls.models import Call
    
    call = await sync_to_async(
        lambda: Call.objects.filter(id=call_id, user=user)
        .select_related('transcription', 'analysis')
        .first()
    )()
    
    if not call:
        await message.answer("❌ Звонок не найден.")
        return
    
    # Формируем информацию
    info_text = format_call_info(call)
    
    await message.answer(
        info_text,
        parse_mode="HTML",
        reply_markup=get_call_detail_keyboard(call_id)
    )


async def statistics_handler(message: types.Message):
    """
    Обработчик команды /stats.
    Показывает статистику пользователя.
    """
    telegram_id = message.from_user.id
    
    # Получаем пользователя
    user = await sync_to_async(User.objects.filter(telegram_id=telegram_id).first)()
    
    if not user:
        await message.answer("❌ Вы не зарегистрированы. Используйте /start")
        return
    
    # Получаем статистику
    from calls.models import Call, CallAnalysis
    from django.db.models import Count, Avg, Sum
    
    stats = await sync_to_async(lambda: {
        'total_calls': Call.objects.filter(user=user).count(),
        'completed': Call.objects.filter(user=user, status='completed').count(),
        'pending': Call.objects.filter(user=user, status='pending').count(),
        'failed': Call.objects.filter(user=user, status='failed').count(),
        'total_duration': Call.objects.filter(user=user).aggregate(Sum('duration'))['duration__sum'] or 0,
        'avg_duration': Call.objects.filter(user=user).aggregate(Avg('duration'))['duration__avg'] or 0,
    })()
    
    # Получаем категории
    categories = await sync_to_async(
        lambda: list(
            CallAnalysis.objects.filter(call__user=user)
            .values('category')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
    )()
    
    stats_text = format_statistics(stats, categories)
    
    await message.answer(stats_text, parse_mode="HTML")


async def search_handler(message: types.Message, state: FSMContext):
    """
    Обработчик команды /search.
    Запускает процесс поиска по звонкам.
    """
    await message.answer(
        "🔍 <b>Поиск по звонкам</b>\n\n"
        "Введите ключевое слово для поиска по транскрипциям:",
        parse_mode="HTML"
    )
    
    from .bot import BotStates
    await state.set_state(BotStates.waiting_for_search_query)


async def settings_handler(message: types.Message):
    """
    Обработчик команды /settings.
    Показывает настройки пользователя.
    """
    telegram_id = message.from_user.id
    
    # Получаем пользователя
    user = await sync_to_async(User.objects.filter(telegram_id=telegram_id).first)()
    
    if not user:
        await message.answer("❌ Вы не зарегистрированы. Используйте /start")
        return
    
    settings_text = f"""
⚙️ <b>Настройки</b>

🔔 Уведомления: {'✅ Включены' if user.notifications_enabled else '❌ Выключены'}

Используйте кнопки ниже для изменения настроек.
"""
    
    await message.answer(
        settings_text,
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(user.notifications_enabled)
    )


async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Обработчик команды /cancel.
    Отменяет текущую операцию.
    """
    current_state = await state.get_state()
    
    if current_state is None:
        await message.answer("Нет активной операции для отмены.")
        return
    
    await state.clear()
    await message.answer(
        "✅ Операция отменена.",
        reply_markup=get_main_keyboard()
    )
