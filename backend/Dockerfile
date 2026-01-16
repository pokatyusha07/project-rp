FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements и устанавливаем Python зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Загружаем spaCy модели
RUN python -m spacy download ru_core_news_sm-3.8.0
RUN python -m spacy download zh_core_web_sm-3.8.0

# Копируем код приложения
COPY . .

# Создаем директории для медиа файлов
RUN mkdir -p media staticfiles

#RUN python manage.py makemigrations
#RUN python manage.py migrate
#RUN python manage.py createsuperuser

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "call_system.asgi:application"]
