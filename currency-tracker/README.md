# 💱 Currency Tracker

> Автоматический парсинг и анализ курсов валют с сохранением в PostgreSQL

[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](../LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

## 📋 Описание проекта

`Currency Tracker` — система для автоматического сбора, хранения и анализа данных о курсах валют. 

Проект предназначен для ежедневного парсинга актуальных курсов валют с последующей выгрузкой в базу данных PostgreSQL для дальнейшего анализа и построения отчётов.

### Основные возможности

- 📊 Ежедневный парсинг курсов валют из различных источников
- 💾 Хранение исторических данных в PostgreSQL
- 📈 Анализ динамики изменения курсов
- 🔍 Построение аналитических отчётов
- ⚡ Оптимизированная структура БД с индексами
- 🔄 Автоматизация процесса сбора данных

## Целевая аудитория

- Финансовые аналитики
- Трейдеры и инвесторы
- Разработчики финансовых приложений
- Студенты, изучающие работу с данными
- Компании, работающие с валютными операциями

## 🏗️ Архитектура

```
┌─────────────────┐
│  Источники      │
│  данных о       │
│  валютах        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Парсер         │
│  (Python/Node)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PostgreSQL     │
│  Database       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Аналитика      │
│  и отчёты       │
└─────────────────┘
```

## 🗄️ Структура базы данных

### Основные таблицы

#### currencies (Валюты)
Справочник валют с основной информацией
```sql
currency_id    SERIAL PRIMARY KEY
code           VARCHAR(3) UNIQUE      -- USD, EUR, RUB
name           VARCHAR(100)           -- Доллар США
symbol         VARCHAR(10)            -- $
country        VARCHAR(100)           -- США
```

#### exchange_rates (Курсы валют)
Исторические данные о курсах
```sql
rate_id        SERIAL PRIMARY KEY
base_currency  VARCHAR(3)             -- Базовая валюта
target_currency VARCHAR(3)            -- Целевая валюта
rate           DECIMAL(18,8)          -- Курс обмена
rate_date      DATE                   -- Дата курса
source         VARCHAR(100)           -- Источник данных
created_at     TIMESTAMP              -- Время записи
```

#### currency_statistics (Статистика)
Агрегированные данные для аналитики
```sql
stat_id        SERIAL PRIMARY KEY
currency_pair  VARCHAR(7)             -- USD/EUR
period_start   DATE
period_end     DATE
avg_rate       DECIMAL(18,8)
min_rate       DECIMAL(18,8)
max_rate       DECIMAL(18,8)
volatility     DECIMAL(10,4)
```

## 🚀 Быстрый старт

### Требования

- PostgreSQL 12+ (рекомендуется 16+)
- Python 3.8+ или Node.js 16+ (для парсера)
- Git

### Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/currency-tracker.git
cd currency-tracker
```

2. Создайте базу данных:
```bash
cd scripts
psql -U postgres -f 00_create_database.sql
```

3. Разверните структуру БД:
```bash
# Linux/Mac
./deploy.sh

# Windows
deploy.bat
```

4. Проверьте установку:
```bash
psql -U postgres -d currency_tracker -c "\dt"
```

### Первый запуск

```sql
-- Подключитесь к БД
psql -U postgres -d currency_tracker

-- Просмотрите доступные валюты
SELECT * FROM currencies;

-- Проверьте последние курсы
SELECT * FROM v_latest_rates LIMIT 10;

-- Получите статистику за неделю
SELECT * FROM v_weekly_statistics 
WHERE currency_pair = 'USD/RUB';
```

## 📊 Примеры использования

### Получение текущего курса

```sql
SELECT 
    base_currency,
    target_currency,
    rate,
    rate_date
FROM exchange_rates
WHERE base_currency = 'USD' 
  AND target_currency = 'RUB'
ORDER BY rate_date DESC
LIMIT 1;
```

### Анализ динамики за месяц

```sql
SELECT 
    rate_date,
    rate,
    rate - LAG(rate) OVER (ORDER BY rate_date) AS daily_change,
    ROUND(
        (rate - LAG(rate) OVER (ORDER BY rate_date)) / 
        LAG(rate) OVER (ORDER BY rate_date) * 100, 
        2
    ) AS change_percent
FROM exchange_rates
WHERE base_currency = 'USD' 
  AND target_currency = 'EUR'
  AND rate_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY rate_date;
```

### Топ-10 самых волатильных пар

```sql
SELECT 
    currency_pair,
    volatility,
    avg_rate,
    (max_rate - min_rate) AS rate_spread
FROM currency_statistics
WHERE period_start >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY volatility DESC
LIMIT 10;
```

## 🔧 Конфигурация парсера

### Настройка источников данных

```python
# config.py
SOURCES = {
    'cbr': {
        'url': 'https://www.cbr.ru/scripts/XML_daily.asp',
        'enabled': True,
        'priority': 1
    },
    'ecb': {
        'url': 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml',
        'enabled': True,
        'priority': 2
    }
}

DATABASE = {
    'host': 'localhost',
    'port': 5432,
    'database': 'currency_tracker',
    'user': 'postgres',
    'password': 'your_password'
}
```

### Автоматизация сбора данных

```bash
# Добавьте в crontab для ежедневного запуска в 9:00
0 9 * * * /usr/bin/python3 /path/to/parser.py >> /var/log/currency_parser.log 2>&1
```

## 📈 Аналитические представления

Проект включает готовые представления для анализа:

- `v_latest_rates` - последние курсы всех валют
- `v_daily_changes` - ежедневные изменения курсов
- `v_weekly_statistics` - статистика за неделю
- `v_monthly_trends` - тренды за месяц
- `v_currency_correlations` - корреляции между валютами

## 🛠️ Разработка

### Структура проекта

```
currency-tracker/
├── README.md                 # Этот файл
├── scripts/                  # SQL скрипты
│   ├── 00_create_database.sql
│   ├── 01_create_tables.sql
│   ├── 02_add_constraints.sql
│   ├── 03_create_indexes.sql
│   ├── 04_create_triggers.sql
│   ├── 05_insert_test_data.sql
│   ├── 06_create_views.sql
│   ├── 07_useful_queries.sql
│   ├── deploy.sh
│   └── deploy.bat
├── parser/                   # Парсер данных
│   ├── main.py
│   ├── config.py
│   └── requirements.txt
└── docs/                     # Документация
    ├── DATABASE_SCHEMA.md
    └── API.md
```

### Добавление нового источника данных

1. Создайте класс парсера в `parser/sources/`
2. Реализуйте методы `fetch()` и `parse()`
3. Добавьте конфигурацию в `config.py`
4. Обновите документацию

## 🔒 Безопасность

- Используйте переменные окружения для хранения паролей
- Настройте SSL-соединение с БД в продакшене
- Ограничьте права доступа к таблицам
- Регулярно создавайте резервные копии

```sql
-- Создание пользователя только для чтения
CREATE USER analyst WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE currency_tracker TO analyst;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyst;
```

## 📝 Лицензия

Проект распространяется под лицензией MIT. Подробности в файле [LICENSE](../LICENSE).

## 👥 Авторы

- **Преподаватель:** Дуплей Максим Игоревич
- **Студент:** Бехтерев Роман Евгеньевич

## 📞 Контакты

- 📧 Email: [email]
- 💬 Telegram: @username
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/currency-tracker/issues)

## 🙏 Благодарности

- Центральный Банк РФ за предоставление API
- European Central Bank за открытые данные
- PostgreSQL Community за отличную СУБД

---

**Версия:** 1.0.0  
**Дата:** 14.03.2026  
**Статус:** В разработке
