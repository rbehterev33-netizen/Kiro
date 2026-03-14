#!/bin/bash

# ============================================
# Скрипт развертывания Currency Tracker
# ============================================

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Параметры подключения
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-postgres}"
DB_NAME="currency_tracker"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Currency Tracker - Развертывание БД${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Проверка наличия psql
if ! command -v psql &> /dev/null; then
    echo -e "${RED}Ошибка: psql не найден${NC}"
    echo "Установите PostgreSQL client"
    exit 1
fi

echo -e "${YELLOW}Параметры подключения:${NC}"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  User: $DB_USER"
echo "  Database: $DB_NAME"
echo ""

# Функция выполнения SQL файла
execute_sql() {
    local file=$1
    local description=$2
    
    echo -e "${YELLOW}Выполнение: $description${NC}"
    
    if [ ! -f "$file" ]; then
        echo -e "${RED}Ошибка: файл $file не найден${NC}"
        exit 1
    fi
    
    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$file" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Успешно${NC}"
    else
        echo -e "${RED}✗ Ошибка при выполнении $file${NC}"
        exit 1
    fi
}

# Создание базы данных
echo -e "${YELLOW}Создание базы данных...${NC}"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -f "00_create_database.sql" > /dev/null 2>&1 || true
echo -e "${GREEN}✓ База данных готова${NC}"
echo ""

# Выполнение миграций
execute_sql "01_create_tables.sql" "Создание таблиц"
execute_sql "02_add_constraints.sql" "Добавление ограничений"
execute_sql "03_create_indexes.sql" "Создание индексов"
execute_sql "04_create_triggers.sql" "Создание триггеров"
execute_sql "05_insert_test_data.sql" "Вставка тестовых данных"
execute_sql "06_create_views.sql" "Создание представлений"
execute_sql "08_create_functions.sql" "Создание функций"
execute_sql "09_create_alerts.sql" "Создание системы алертов"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Развертывание завершено успешно!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Вывод статистики
echo -e "${YELLOW}Статистика базы данных:${NC}"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "
SELECT 
    'Валюты' AS \"Таблица\", 
    COUNT(*) AS \"Записей\" 
FROM currencies
UNION ALL
SELECT 'Источники данных', COUNT(*) FROM data_sources
UNION ALL
SELECT 'Курсы валют', COUNT(*) FROM exchange_rates
UNION ALL
SELECT 'Статистика', COUNT(*) FROM currency_statistics
UNION ALL
SELECT 'Лог парсинга', COUNT(*) FROM parsing_log;
"

echo ""
echo -e "${GREEN}Готово! Подключитесь к БД:${NC}"
echo "  psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"
