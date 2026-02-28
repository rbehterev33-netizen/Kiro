# 🚀 Быстрый старт SmartOffice

Это краткое руководство поможет вам развернуть SmartOffice за 5 минут.

## Предварительные требования

- PostgreSQL 12+ установлен и запущен
- Доступ к командной строке
- Права на создание базы данных

## Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/your-org/smartoffice.git
cd smartoffice
```

## Шаг 2: Автоматическое развёртывание

### Linux / macOS

```bash
cd scripts
chmod +x deploy.sh
./deploy.sh
```

### Windows

```cmd
cd scripts
deploy.bat
```

### Ручное развёртывание

Если автоматический скрипт не работает, выполните команды вручную:

```bash
# 1. Создайте базу данных
psql -U postgres -f scripts/00_create_database.sql

# 2. Подключитесь к базе
psql -U postgres -d SmartOffice

# 3. Выполните миграции
\i scripts/01_create_tables.sql
\i scripts/02_add_constraints.sql
\i scripts/03_create_indexes.sql
\i scripts/04_create_triggers.sql
\i scripts/05_insert_test_data.sql
\i scripts/06_views.sql
```

## Шаг 3: Проверка установки

```sql
-- Подключитесь к базе
psql -U postgres -d SmartOffice

-- Проверьте таблицы
\dt

-- Проверьте данные
SELECT COUNT(*) FROM employees;

-- Посмотрите список сотрудников
SELECT * FROM v_employee_info;
```

## Шаг 4: Первые запросы

### Список всех сотрудников

```sql
SELECT 
    personnel_number,
    full_name,
    department,
    position
FROM v_employee_info
ORDER BY full_name;
```

### Текущие оклады

```sql
SELECT * FROM v_current_salaries
ORDER BY current_salary DESC;
```

### Активные проекты

```sql
SELECT 
    name,
    start_date,
    status,
    budget
FROM projects
WHERE status = 'active';
```

### Загруженность сотрудников

```sql
SELECT * FROM v_employee_task_load
ORDER BY active_tasks DESC;
```

## Шаг 5: Настройка безопасности (опционально)

```sql
-- Создайте роли
CREATE ROLE hr_manager LOGIN PASSWORD 'secure_password';
CREATE ROLE employee_readonly LOGIN PASSWORD 'secure_password';

-- Выдайте права
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO hr_manager;
GRANT SELECT ON v_employee_info TO employee_readonly;
```

## Полезные команды

### Резервное копирование

```bash
# Создать бэкап
pg_dump -U postgres SmartOffice > backup_$(date +%Y%m%d).sql

# Восстановить из бэкапа
psql -U postgres -d SmartOffice < backup_20260228.sql
```

### Очистка и оптимизация

```sql
-- Обновить статистику
ANALYZE;

-- Очистить мёртвые строки
VACUUM ANALYZE;

-- Проверить размер таблиц
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Мониторинг производительности

```sql
-- Установить расширение для статистики
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Топ-10 медленных запросов
SELECT 
    query,
    calls,
    mean_exec_time,
    total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

## Что дальше?

1. Изучите [полную документацию](README.md)
2. Посмотрите [примеры запросов](scripts/07_useful_queries.sql)
3. Настройте [расширения PostgreSQL](scripts/08_extensions.sql)
4. Адаптируйте схему под свои нужды

## Получение помощи

- 📧 Email: support@smartoffice.ru
- 💬 Telegram: @smartoffice_support
- 📚 Документация: https://docs.smartoffice.ru
- 🐛 Issues: https://github.com/your-org/smartoffice/issues

## Частые проблемы

### Ошибка: "database already exists"

База данных уже создана. Пропустите шаг создания БД или удалите существующую:

```sql
DROP DATABASE IF EXISTS SmartOffice;
```

### Ошибка: "extension does not exist"

Установите необходимые расширения:

```bash
# Ubuntu/Debian
sudo apt install postgresql-contrib-16

# Затем в psql
CREATE EXTENSION pg_trgm;
CREATE EXTENSION btree_gist;
```

### Ошибка: "permission denied"

Убедитесь, что у пользователя есть права:

```sql
GRANT ALL PRIVILEGES ON DATABASE SmartOffice TO postgres;
```

---

**Готово!** Теперь у вас работает SmartOffice. 🎉
