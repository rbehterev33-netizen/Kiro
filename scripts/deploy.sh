#!/bin/bash

# ============================================
# Скрипт автоматического развёртывания SmartOffice
# ============================================

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Параметры подключения (можно переопределить через переменные окружения)
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_USER=${DB_USER:-postgres}
DB_NAME=${DB_NAME:-SmartOffice}

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}SmartOffice Database Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Проверка наличия psql
if ! command -v psql &> /dev/null; then
    echo -e "${RED}Ошибка: psql не найден. Установите PostgreSQL client.${NC}"
    exit 1
fi

echo -e "${YELLOW}Параметры подключения:${NC}"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  User: $DB_USER"
echo "  Database: $DB_NAME"
echo ""

# Функция для выполнения SQL файла
execute_sql() {
    local file=$1
    local description=$2
    
    echo -e "${YELLOW}Выполняется: $description${NC}"
    echo "  Файл: $file"
    
    if [ ! -f "$file" ]; then
        echo -e "${RED}  Ошибка: файл не найден!${NC}"
        exit 1
    fi
    
    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$file" > /dev/null 2>&1; then
        echo -e "${GREEN}  ✓ Успешно выполнено${NC}"
    else
        echo -e "${RED}  ✗ Ошибка выполнения${NC}"
        exit 1
    fi
    echo ""
}

# Проверка существования базы данных
echo -e "${YELLOW}Проверка существования базы данных...${NC}"
if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo -e "${GREEN}База данных $DB_NAME уже существует${NC}"
else
    echo -e "${YELLOW}Создание базы данных $DB_NAME...${NC}"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -f "00_create_database.sql"
    echo -e "${GREEN}База данных создана${NC}"
fi
echo ""

# Выполнение миграций
execute_sql "01_create_tables.sql" "Создание таблиц"
execute_sql "02_add_constraints.sql" "Добавление ограничений"
execute_sql "03_create_indexes.sql" "Создание индексов"
execute_sql "04_create_triggers.sql" "Создание триггеров"
execute_sql "05_insert_test_data.sql" "Вставка тестовых данных"
execute_sql "06_views.sql" "Создание представлений"

# Проверка результата
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Развёртывание завершено успешно!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Статистика
echo -e "${YELLOW}Статистика:${NC}"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "
SELECT 
    'Таблиц' AS metric, 
    COUNT(*)::text AS value 
FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
UNION ALL
SELECT 
    'Представлений', 
    COUNT(*)::text 
FROM information_schema.views 
WHERE table_schema = 'public'
UNION ALL
SELECT 
    'Сотрудников', 
    COUNT(*)::text 
FROM employees;
"

echo ""
echo -e "${GREEN}Готово! Можете подключаться к базе данных.${NC}"
echo -e "${YELLOW}Команда для подключения:${NC}"
echo "  psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"
