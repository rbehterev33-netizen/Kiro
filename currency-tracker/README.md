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
- 📉 Расчет технических индикаторов (RSI, SMA)
- 🎯 Определение трендов и прогнозирование
- 💱 Поиск арбитражных возможностей
- 🔔 Система алертов и уведомлений
- 📊 Визуализация данных
- 🌐 REST API для интеграции
- 📤 Экспорт данных в CSV/JSON

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
- Python 3.8+
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

4. Установите зависимости Python:
```bash
cd ../parser
pip install -r requirements.txt
```

5. Настройте конфигурацию:
```bash
cp .env.example .env
# Отредактируйте .env с вашими параметрами БД
```

6. Запустите парсер:
```bash
python main.py
```

### Проверка установки

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

### Настройка переменных окружения

Создайте файл `.env` в папке `parser/`:

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=currency_tracker
DB_USER=postgres
DB_PASSWORD=your_password

PARSE_INTERVAL_HOURS=24
LOG_LEVEL=INFO
```

### Источники данных

Парсер поддерживает:
- Центральный Банк России (ЦБ РФ)
- Европейский Центральный Банк (ЕЦБ)

Настройка в `parser/config.py`

### Запуск парсера

```bash
# Установка зависимостей
cd parser
pip install -r requirements.txt

# Настройка конфигурации
cp .env.example .env
# Отредактируйте .env файл с вашими параметрами БД

# Запуск парсера
python main.py
```

### Автоматизация сбора данных

```bash
# Linux/Mac - добавьте в crontab для ежедневного запуска в 9:00
0 9 * * * cd /path/to/currency-tracker/parser && /usr/bin/python3 main.py >> /var/log/currency_parser.log 2>&1

# Windows - создайте задачу в планировщике задач
# Программа: python
# Аргументы: C:\path\to\currency-tracker\parser\main.py
# Расписание: ежедневно в 9:00
```

## 📈 Расширенная аналитика

### Представления
- `v_latest_rates` - последние курсы всех валют
- `v_daily_changes` - ежедневные изменения курсов
- `v_weekly_statistics` - статистика за неделю
- `v_monthly_statistics` - статистика за месяц
- `v_source_activity` - активность источников данных
- `v_top_volatile_pairs` - топ волатильных пар

### Функции
- `convert_currency()` - конвертация валют
- `get_cross_rate()` - расчет кросс-курсов
- `predict_rate_sma()` - прогноз на основе SMA
- `get_trend()` - определение тренда
- `calculate_rsi()` - расчет RSI индикатора
- `find_arbitrage_opportunities()` - поиск арбитража
- `get_rate_history_json()` - экспорт в JSON

### CLI интерфейс
```bash
# Анализ тренда
python cli.py trend USD/RUB 7

# Поиск арбитража
python cli.py arbitrage

# Рейтинг волатильности
python cli.py volatility 7

# Генерация отчета
python cli.py report EUR/RUB 30

# Проверка алертов
python cli.py alerts

# Визуализация графика
python cli.py visualize USD/RUB 30

# Экспорт данных
python cli.py export csv USD/RUB 30
python cli.py export json EUR/RUB 30
```

### REST API
```bash
# Запуск API сервера
python api_server.py

# Примеры запросов
curl http://localhost:5000/api/rates/latest
curl http://localhost:5000/api/rates/USD-RUB?days=30
curl http://localhost:5000/api/convert?amount=100&from=USD&to=RUB
curl http://localhost:5000/api/analysis/USD-RUB?days=30
curl http://localhost:5000/api/arbitrage
curl http://localhost:5000/api/volatility?days=7
```

### Планировщик задач
```bash
# Автоматический запуск парсинга, проверки алертов и расчета статистики
python scheduler.py
```

### Система алертов
Настройка уведомлений о важных событиях:
- Превышение/падение курса ниже порога
- Резкие изменения курса (в процентах)
- Высокая волатильность

## 🛠️ Разработка

### Структура проекта

```
currency-tracker/
├── README.md                 # Документация
├── LICENSE                   # Лицензия MIT (EN)
├── LICENSE_RU                # Лицензия MIT (RU)
├── CHANGELOG.md              # История изменений
├── .gitignore                # Игнорируемые файлы
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
└── parser/                   # Парсер данных
    ├── main.py               # Главный файл парсера
    ├── config.py             # Конфигурация
    ├── database.py           # Работа с БД
    ├── analyzer.py           # Модуль анализа
    ├── visualizer.py         # Визуализация
    ├── exporter.py           # Экспорт данных
    ├── api_server.py         # REST API
    ├── scheduler.py          # Планировщик
    ├── cli.py                # CLI интерфейс
    ├── requirements.txt      # Зависимости
    ├── .env.example          # Пример конфигурации
    └── parsers/              # Парсеры источников
        ├── __init__.py
        ├── cbr_parser.py     # ЦБ РФ
        └── ecb_parser.py     # ЕЦБ
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
