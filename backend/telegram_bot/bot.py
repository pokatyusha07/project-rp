"""
Главный модуль Telegram бота с использованием aiogram.
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from django.conf import settings
import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'call_system.settings')
django.setup()

from .handlers import (
    start_handler,
    help_handler,
    register_handler,
    upload_voice_handler,
    my_calls_handler,
    call_detail_handler,
    statistics_handler,
    search_handler,
    settings_handler,
    cancel_handler
)
from .keyboards import get_main_keyboard

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BotStates(StatesGroup):
    """Состояния бота для FSM (Finite State Machine)."""
    waiting_for_voice = State()
    waiting_for_search_query = State()
    waiting_for_registration = State()


def setup_bot():
    """
    Инициализирует и настраивает Telegram бота.
    
    Returns:
        tuple: (Bot, Dispatcher)
    """
    # Создаем экземпляр бота
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    
    # Создаем диспетчер с хранилищем состояний
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрируем обработчики команд
    dp.message.register(start_handler, Command('start'))
    dp.message.register(help_handler, Command('help'))
    dp.message.register(register_handler, Command('register'))
    dp.message.register(my_calls_handler, Command('calls'))
    dp.message.register(statistics_handler, Command('stats'))
    dp.message.register(search_handler, Command('search'))
    dp.message.register(settings_handler, Command('settings'))
    dp.message.register(cancel_handler, Command('cancel'))
    
    # Регистрируем обработчики голосовых сообщений
    dp.message.register(upload_voice_handler, F.voice)
    dp.message.register(upload_voice_handler, F.audio)
    
    # Регистрируем обработчики callback'ов
    from .callbacks import register_callbacks
    register_callbacks(dp)
    
    logger.info("Telegram бот инициализирован")
    
    return bot, dp


async def start_bot():
    """
    Запускает Telegram бота.
    """
    bot, dp = setup_bot()
    
    try:
        logger.info("Запуск Telegram бота...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start_bot())
