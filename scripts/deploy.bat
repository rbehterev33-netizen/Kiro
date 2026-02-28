@echo off
REM ============================================
REM Скрипт автоматического развёртывания SmartOffice для Windows
REM ============================================

setlocal enabledelayedexpansion

REM Параметры подключения (можно переопределить)
if "%DB_HOST%"=="" set DB_HOST=localhost
if "%DB_PORT%"=="" set DB_PORT=5432
if "%DB_USER%"=="" set DB_USER=postgres
if "%DB_NAME%"=="" set DB_NAME=SmartOffice

echo ========================================
echo SmartOffice Database Deployment
echo ========================================
echo.

REM Проверка наличия psql
where psql >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Ошибка: psql не найден. Установите PostgreSQL client.
    exit /b 1
)

echo Параметры подключения:
echo   Host: %DB_HOST%
echo   Port: %DB_PORT%
echo   User: %DB_USER%
echo   Database: %DB_NAME%
echo.

REM Проверка существования базы данных
echo Проверка существования базы данных...
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -lqt | findstr /C:"%DB_NAME%" >nul
if %ERRORLEVEL% NEQ 0 (
    echo Создание базы данных %DB_NAME%...
    psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -f "00_create_database.sql"
    if %ERRORLEVEL% NEQ 0 (
        echo Ошибка создания базы данных
        exit /b 1
    )
    echo База данных создана
) else (
    echo База данных %DB_NAME% уже существует
)
echo.

REM Выполнение миграций
call :execute_sql "01_create_tables.sql" "Создание таблиц"
call :execute_sql "02_add_constraints.sql" "Добавление ограничений"
call :execute_sql "03_create_indexes.sql" "Создание индексов"
call :execute_sql "04_create_triggers.sql" "Создание триггеров"
call :execute_sql "05_insert_test_data.sql" "Вставка тестовых данных"
call :execute_sql "06_views.sql" "Создание представлений"

echo ========================================
echo Развёртывание завершено успешно!
echo ========================================
echo.

REM Статистика
echo Статистика:
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -c "SELECT 'Таблиц' AS metric, COUNT(*)::text AS value FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE' UNION ALL SELECT 'Представлений', COUNT(*)::text FROM information_schema.views WHERE table_schema = 'public' UNION ALL SELECT 'Сотрудников', COUNT(*)::text FROM employees;"

echo.
echo Готово! Можете подключаться к базе данных.
echo Команда для подключения:
echo   psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME%

exit /b 0

:execute_sql
set file=%~1
set description=%~2

echo Выполняется: %description%
echo   Файл: %file%

if not exist "%file%" (
    echo   Ошибка: файл не найден!
    exit /b 1
)

psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -f "%file%" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo   Ошибка выполнения
    exit /b 1
)

echo   Успешно выполнено
echo.
exit /b 0
