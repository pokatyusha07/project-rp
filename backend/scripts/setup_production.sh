#!/bin/bash

# Скрипт для первоначальной настройки продакшн окружения

set -e

echo "Настройка продакшн окружения..."

# Создание директорий
echo "Создание директорий..."
mkdir -p logs
mkdir -p media
mkdir -p staticfiles

# Установка зависимостей
echo "Установка зависимостей..."
pip install -r requirements.txt

# Загрузка моделей spaCy
echo "Загрузка NLP моделей..."
python -m spacy download ru_core_news_sm
python -m spacy download en_core_web_sm

# Создание миграций
echo "Применение миграций..."
python manage.py makemigrations
python manage.py migrate

# Сбор статических файлов
echo "Сбор статических файлов..."
python manage.py collectstatic --noinput

# Создание суперпользователя (если нужно)
echo "Создание суперпользователя..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell

echo "Настройка завершена!"
echo "Для запуска системы используйте: ./scripts/run_all.sh"
