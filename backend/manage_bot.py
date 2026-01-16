"""
Утилита для управления Telegram ботом.
"""
import os
import django
import asyncio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'call_system.settings')
django.setup()

from telegram_bot.bot import start_bot

if __name__ == '__main__':
    print("🤖 Запуск Telegram бота...")
    asyncio.run(start_bot())
