#!/bin/bash

# Скрипт для запуска Telegram бота

echo "Запуск Telegram бота..."

# Активируем виртуальное окружение если оно есть
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Запускаем бота
python -m telegram_bot.bot
