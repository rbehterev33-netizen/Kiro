# 🚀 Быстрый старт

## Шаг 1: Установка PostgreSQL

Убедитесь, что PostgreSQL установлен:
```bash
psql --version
```

## Шаг 2: Развертывание базы данных

### Windows
```cmd
cd scripts
deploy.bat
```

### Linux/Mac
```bash
cd scripts
chmod +x deploy.sh
./deploy.sh
```

## Шаг 3: Настройка парсера

```bash
cd parser
pip install -r requirements.txt
cp .env.example .env
```

Отредактируйте `.env` файл с вашими параметрами БД.

## Шаг 4: Запуск парсера

```bash
python main.py
```

## Шаг 5: Проверка данных

```bash
psql -U postgres -d currency_tracker
```

```sql
-- Просмотр последних курсов
SELECT * FROM v_latest_rates;

-- Статистика за неделю
SELECT * FROM v_weekly_statistics;
```

## Готово! 🎉

Теперь у вас работает система парсинга и анализа курсов валют.
