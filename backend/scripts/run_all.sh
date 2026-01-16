#!/bin/bash

# Скрипт для запуска всех компонентов системы

echo "Запуск системы обработки звонков..."

# Запускаем Django сервер
echo "Запуск Django сервера..."
python manage.py runserver &
DJANGO_PID=$!

# Запускаем Celery worker
echo "Запуск Celery worker..."
celery -A call_system worker -l info &
CELERY_WORKER_PID=$!

# Запускаем Celery beat
echo "Запуск Celery beat..."
celery -A call_system beat -l info &
CELERY_BEAT_PID=$!

# Запускаем Telegram бота
echo "Запуск Telegram бота..."
python manage_bot.py &
BOT_PID=$!

echo "Все компоненты запущены!"
echo "Django: PID $DJANGO_PID"
echo "Celery Worker: PID $CELERY_WORKER_PID"
echo "Celery Beat: PID $CELERY_BEAT_PID"
echo "Telegram Bot: PID $BOT_PID"

# Ожидание сигнала завершения
wait
