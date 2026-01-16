-- SQL скрипт для инициализации базы данных

-- Создание базы данных
CREATE DATABASE call_system_db;

-- Подключение к базе
\c call_system_db;

-- Создание расширений PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- Для полнотекстового поиска

-- Предоставление прав
GRANT ALL PRIVILEGES ON DATABASE call_system_db TO postgres;
