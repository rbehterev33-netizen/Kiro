@echo off
REM ============================================
REM Скрипт развертывания Currency Tracker (Windows)
REM ============================================

setlocal enabledelayedexpansion

REM Параметры подключения
set DB_HOST=localhost
set DB_PORT=5432
set DB_USER=postgres
set DB_NAME=currency_tracker

echo ========================================
echo Currency Tracker - Развертывание БД
echo ========================================
echo.

REM Проверка наличия psql
where psql >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Ошибка: psql не найден
    echo Установите PostgreSQL client
    exit /b 1
)

echo Параметры подключения:
echo   Host: %DB_HOST%
echo   Port: %DB_PORT%
echo   User: %DB_USER%
echo   Database: %DB_NAME%
echo.

REM Создание базы данных
echo Создание базы данных...
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d postgres -f "00_create_database.sql" >nul 2>&1
echo [OK] База данных готова
echo.

REM Выполнение миграций
call :execute_sql "01_create_tables.sql" "Создание таблиц"
call :execute_sql "02_add_constraints.sql" "Добавление ограничений"
call :execute_sql "03_create_indexes.sql" "Создание индексов"
call :execute_sql "04_create_triggers.sql" "Создание триггеров"
call :execute_sql "05_insert_test_data.sql" "Вставка тестовых данных"
call :execute_sql "06_create_views.sql" "Создание представлений"
call :execute_sql "08_create_functions.sql" "Создание функций"
call :execute_sql "09_create_alerts.sql" "Создание системы алертов"

echo.
echo ========================================
echo Развертывание завершено успешно!
echo ========================================
echo.

REM Вывод статистики
echo Статистика базы данных:
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -c "SELECT 'Валюты' AS \"Таблица\", COUNT(*) AS \"Записей\" FROM currencies UNION ALL SELECT 'Источники данных', COUNT(*) FROM data_sources UNION ALL SELECT 'Курсы валют', COUNT(*) FROM exchange_rates UNION ALL SELECT 'Статистика', COUNT(*) FROM currency_statistics UNION ALL SELECT 'Лог парсинга', COUNT(*) FROM parsing_log;"

echo.
echo Готово! Подключитесь к БД:
echo   psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME%

exit /b 0

:execute_sql
set file=%~1
set description=%~2

echo Выполнение: %description%

if not exist "%file%" (
    echo Ошибка: файл %file% не найден
    exit /b 1
)

psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -f "%file%" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ОШИБКА] при выполнении %file%
    exit /b 1
)

echo [OK] Успешно
exit /b 0
