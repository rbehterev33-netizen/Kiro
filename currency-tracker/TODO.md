# TODO — Currency Tracker

## Состояние проекта (14.03.2026)

### Стек

- **БД**: PostgreSQL 16, порт 5433, база `currency_tracker`
- **Python**: 3.14.3 — `C:\Users\1\AppData\Local\Python\pythoncore-3.14-64\python.exe`
- **Сервер**: FastAPI + Uvicorn, порт 8000
- **Фронтенд**: Jinja2 + Chart.js (CDN), без Node.js
- **Данные**: 7036 записей, 15.09.2025 — 14.03.2026, 66 валют, 5 источников

### Запуск проекта

```bash
# Из папки currency-tracker/parser/
python fastapi_server.py           # сервер → http://localhost:8000
python load_history.py             # перезагрузить историю 6 мес
python load_history.py 365         # загрузить год
python load_history.py --no-clear  # дополнить без очистки
python main.py                     # разовый парсинг всех источников
```

### Источники данных (все активны)

| Источник | URL | Данные |
|---|---|---|
| ЦБ РФ | cbr.ru/scripts/XML_daily.asp | 32 валюты к RUB |
| ЕЦБ | ecb.europa.eu/stats/eurofxref | ~30 валют к EUR |
| MOEX | iss.moex.com/iss | USD/CNY/TRY к RUB (биржевые) |
| CoinGecko | api.coingecko.com/api/v3 | BTC/ETH/USDT/BNB/SOL/XRP/TON к USD/RUB/EUR |

### Страницы сайта

| URL | Описание |
|---|---|
| `/` | Дашборд — статистика, волатильность, график, таблица курсов |
| `/rates` | Все курсы с историей и фильтрами |
| `/converter` | Конвертер валют |
| `/analysis` | Анализ пары: тренд, RSI, прогноз, корреляция |
| `/compare` | Сравнение ЦБ РФ vs MOEX, спред |
| `/crypto` | Криптовалюты с графиком |
| `/logs` | Логи парсера |
| `/docs` | Swagger API документация |

---

## Сделано ✅

- [x] PostgreSQL схема: таблицы, индексы, триггеры, вьюхи, функции, алерты
- [x] Парсер ЦБ РФ (XML_daily.asp + XML_dynamic.asp для истории)
- [x] Парсер ЕЦБ (eurofxref-daily.xml + eurofxref-hist.xml)
- [x] Парсер MOEX (ISS API — реальные биржевые курсы)
- [x] Парсер CoinGecko (крипто: BTC, ETH, USDT, BNB, SOL, XRP, TON)
- [x] FastAPI сервер с 20+ эндпоинтами
- [x] Веб-интерфейс: 7 страниц (dashboard, rates, converter, analysis, compare, crypto, logs)
- [x] Планировщик: парсинг в 09:00, проверка алертов каждый час
- [x] Загрузка истории за 6 месяцев (7036 записей)
- [x] Аналитика: тренд, RSI, прогноз, корреляция, волатильность, арбитраж
- [x] Экспорт в CSV
- [x] Страница сравнения источников (ЦБ vs MOEX) с графиком и спредом
- [x] Страница криптовалют с графиком и статами

---

## Приоритет: Высокий

- [ ] **Telegram-бот для алертов**
  - Таблица `currency_alerts` и функция `check_alerts()` уже готовы
  - Нужно только добавить отправку через `python-telegram-bot`
  - Токен бота через `.env` → `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`

- [ ] **Банки РФ — курсы покупки/продажи**
  - Сбербанк: `https://www.sberbank.ru/ru/quotes/currencies`
  - ВТБ: API или парсинг страницы
  - Добавить на страницу `/compare` рядом с ЦБ и MOEX

- [ ] **Авторизация**
  - API полностью открыт — POST-эндпоинты без защиты
  - JWT-токены для `/api/parse/*`, `/api/alerts`
  - Личный кабинет с настройкой алертов

---

## Приоритет: Средний

- [ ] **Расширить аналитику**
  - Bollinger Bands на графике
  - MACD индикатор
  - Корреляционная матрица всех пар (тепловая карта)
  - Сезонность — сравнение одного месяца по разным годам

- [ ] **Улучшить графики**
  - Свечной график (candlestick) — MOEX отдаёт OHLC через candles.json
  - Наложение двух пар на один график
  - Zoom и pan мышью (Chart.js zoom plugin)

- [ ] **Экспорт и отчёты**
  - PDF-отчёт по паре за период (reportlab или weasyprint)
  - Excel-выгрузка с форматированием (openpyxl)

- [ ] **Кэширование**
  - Redis или простой in-memory кэш для `/api/rates/latest`
  - TTL 60 сек — снизит нагрузку на БД

---

## Приоритет: Низкий

- [ ] **Docker**
  - `docker-compose.yml` с PostgreSQL + Python сервером
  - Упростит развёртывание

- [ ] **Тесты**
  - Unit-тесты для новых парсеров (MOEX, CoinGecko)
  - `test_server.py` уже есть — расширить на новые эндпоинты

- [ ] **Документация API**
  - Swagger на `/docs` уже есть
  - Добавить описания полей в Pydantic-моделях

- [ ] **Node.js фронтенд** (когда установят Node.js)
  - React + Recharts или Vue + ECharts
  - PWA

---

## Известные проблемы / Заметки

- ЦБ РФ публикует курс на **следующий** рабочий день после ~15:30 — расхождение с рынком это норма
- MOEX в выходные торги не идут — `LAST` может быть `None`, парсер это обрабатывает
- ЕЦБ не публикует данные в выходные — пропуски в истории по сб/вс это норма
- `ON CONFLICT DO UPDATE` в `database.py` — курс за текущую дату обновляется при каждом запуске
- Flask (`api_server.py`) существует параллельно с FastAPI — можно удалить, не используется
- CoinGecko бесплатный API имеет rate limit ~30 req/min — при частых запросах может вернуть 429
