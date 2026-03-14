-- ============================================
-- Полезные запросы для анализа данных
-- ============================================

-- ============================================
-- 1. БАЗОВЫЕ ЗАПРОСЫ
-- ============================================

-- Все доступные валюты
SELECT * FROM currencies WHERE is_active = TRUE ORDER BY code;

-- Последние курсы
SELECT * FROM v_latest_rates ORDER BY currency_pair;

-- Курс USD/RUB за последние 7 дней
SELECT 
    rate_date,
    rate,
    rate - LAG(rate) OVER (ORDER BY rate_date) AS daily_change
FROM exchange_rates
WHERE base_currency = 'USD' 
  AND target_currency = 'RUB'
  AND rate_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY rate_date DESC;

-- ============================================
-- 2. АНАЛИТИКА И ТРЕНДЫ
-- ============================================

-- Динамика курса с процентным изменением
SELECT 
    rate_date,
    rate,
    rate - LAG(rate) OVER (ORDER BY rate_date) AS absolute_change,
    ROUND(
        (rate - LAG(rate) OVER (ORDER BY rate_date)) / 
        LAG(rate) OVER (ORDER BY rate_date) * 100, 
        2
    ) AS percent_change
FROM exchange_rates
WHERE base_currency = 'USD' 
  AND target_currency = 'EUR'
  AND rate_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY rate_date;

-- Скользящее среднее за 7 дней
SELECT 
    rate_date,
    rate,
    ROUND(
        AVG(rate) OVER (
            ORDER BY rate_date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        )::NUMERIC, 
        4
    ) AS moving_avg_7d
FROM exchange_rates
WHERE base_currency = 'USD' 
  AND target_currency = 'RUB'
ORDER BY rate_date DESC
LIMIT 30;

-- Корреляция между валютными парами
WITH usd_rub AS (
    SELECT rate_date, rate AS usd_rate
    FROM exchange_rates
    WHERE base_currency = 'USD' AND target_currency = 'RUB'
),
eur_rub AS (
    SELECT rate_date, rate AS eur_rate
    FROM exchange_rates
    WHERE base_currency = 'EUR' AND target_currency = 'RUB'
)
SELECT 
    ROUND(CORR(u.usd_rate, e.eur_rate)::NUMERIC, 4) AS correlation
FROM usd_rub u
JOIN eur_rub e ON u.rate_date = e.rate_date;

-- ============================================
-- 3. СТАТИСТИКА
-- ============================================

-- Статистика за последний месяц по всем парам
SELECT * FROM v_monthly_statistics;

-- Самые стабильные валютные пары (низкая волатильность)
SELECT 
    currency_pair,
    volatility,
    avg_rate
FROM v_weekly_statistics
WHERE volatility IS NOT NULL
ORDER BY volatility ASC
LIMIT 5;

-- Самые волатильные пары
SELECT * FROM v_top_volatile_pairs;

-- Максимальное и минимальное значение курса за все время
SELECT 
    base_currency || '/' || target_currency AS currency_pair,
    MIN(rate) AS all_time_min,
    MAX(rate) AS all_time_max,
    MAX(rate) - MIN(rate) AS total_spread,
    MIN(rate_date) AS first_date,
    MAX(rate_date) AS last_date
FROM exchange_rates
GROUP BY base_currency, target_currency
ORDER BY total_spread DESC;

-- ============================================
-- 4. СРАВНЕНИЕ ПЕРИОДОВ
-- ============================================

-- Сравнение текущей недели с предыдущей
WITH current_week AS (
    SELECT 
        base_currency,
        target_currency,
        AVG(rate) AS avg_rate
    FROM exchange_rates
    WHERE rate_date >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY base_currency, target_currency
),
previous_week AS (
    SELECT 
        base_currency,
        target_currency,
        AVG(rate) AS avg_rate
    FROM exchange_rates
    WHERE rate_date >= CURRENT_DATE - INTERVAL '14 days'
      AND rate_date < CURRENT_DATE - INTERVAL '7 days'
    GROUP BY base_currency, target_currency
)
SELECT 
    cw.base_currency || '/' || cw.target_currency AS currency_pair,
    ROUND(pw.avg_rate::NUMERIC, 4) AS prev_week_avg,
    ROUND(cw.avg_rate::NUMERIC, 4) AS curr_week_avg,
    ROUND((cw.avg_rate - pw.avg_rate)::NUMERIC, 4) AS change,
    ROUND(((cw.avg_rate - pw.avg_rate) / pw.avg_rate * 100)::NUMERIC, 2) AS change_percent
FROM current_week cw
JOIN previous_week pw 
    ON cw.base_currency = pw.base_currency 
    AND cw.target_currency = pw.target_currency
ORDER BY ABS((cw.avg_rate - pw.avg_rate) / pw.avg_rate) DESC;

-- ============================================
-- 5. МОНИТОРИНГ ПАРСЕРА
-- ============================================

-- Статистика работы парсера
SELECT * FROM v_source_activity;

-- Последние запуски парсера
SELECT 
    ds.name AS source_name,
    pl.parse_date,
    pl.status,
    pl.records_added,
    pl.execution_time_ms,
    pl.error_message,
    pl.created_at
FROM parsing_log pl
JOIN data_sources ds ON pl.source_id = ds.source_id
ORDER BY pl.created_at DESC
LIMIT 20;

-- Ошибки парсинга
SELECT 
    ds.name AS source_name,
    pl.parse_date,
    pl.error_message,
    pl.created_at
FROM parsing_log pl
JOIN data_sources ds ON pl.source_id = ds.source_id
WHERE pl.status = 'failed'
ORDER BY pl.created_at DESC;

-- ============================================
-- 6. СЛУЖЕБНЫЕ ЗАПРОСЫ
-- ============================================

-- Размер таблиц
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Количество записей в таблицах
SELECT 
    'currencies' AS table_name, 
    COUNT(*) AS records 
FROM currencies
UNION ALL
SELECT 'data_sources', COUNT(*) FROM data_sources
UNION ALL
SELECT 'exchange_rates', COUNT(*) FROM exchange_rates
UNION ALL
SELECT 'currency_statistics', COUNT(*) FROM currency_statistics
UNION ALL
SELECT 'parsing_log', COUNT(*) FROM parsing_log;

-- Проверка индексов
SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
