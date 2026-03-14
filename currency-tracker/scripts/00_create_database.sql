-- ============================================
-- Создание базы данных Currency Tracker
-- ============================================

-- Удаление БД если существует (осторожно!)
-- DROP DATABASE IF EXISTS currency_tracker;

-- Создание базы данных
CREATE DATABASE currency_tracker
    WITH 
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- Подключение к БД
\c currency_tracker

-- Комментарий к БД
COMMENT ON DATABASE currency_tracker IS 'База данных для хранения и анализа курсов валют';
