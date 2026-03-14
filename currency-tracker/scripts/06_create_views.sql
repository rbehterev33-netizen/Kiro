-- ============================================
-- Создание представлений для аналитики
-- ============================================

-- Последние курсы всех валют
CREATE OR REPLACE VIEW v_latest_rates AS
SELECT DISTINCT ON (er.base_currency, er.target_currency)
    er.base_currency,
    er.target_currency,
    er.base_currency || '/' || er.target_currency AS currency_pair,
    er.rate,
    er.rate_date,
    ds.name AS source_name,
    er.created_at
FROM exchange_rates er
JOIN data_sources ds ON er.source_id = ds.source_id
ORDER BY er.base_currency, er.target_currency, er.rate_date DESC, er.created_at DESC;

COMMENT ON VIEW v_latest_rates IS 'Последние курсы всех валютных пар';

-- Ежедневные изменения курсов
CREATE OR REPLACE VIEW v_daily_changes AS
SELECT 
    base_currency,
    target_currency,
    base_currency || '/' || target_currency AS currency_pair,
    rate_date,
    rate AS current_rate,
    LAG(rate) OVER (PARTITION BY base_currency, target_currency ORDER BY rate_date) AS previous_rate,
    rate - LAG(rate) OVER (PARTITION BY base_currency, target_currency ORDER BY rate_date) AS absolute_change,
    ROUND(
        ((rate - LAG(rate) OVER (PARTITION BY base_currency, target_currency ORDER BY rate_date)) / 
        LAG(rate) OVER (PARTITION BY base_currency, target_currency ORDER BY rate_date) * 100)::NUMERIC, 
        4
    ) AS percent_change
FROM exchange_rates
ORDER BY rate_date DESC, base_currency, target_currency;

COMMENT ON VIEW v_daily_changes IS 'Ежедневные изменения курсов валют';

-- Статистика за неделю
CREATE OR REPLACE VIEW v_weekly_statistics AS
SELECT 
    base_currency || '/' || target_currency AS currency_pair,
    COUNT(*) AS days_count,
    ROUND(AVG(rate)::NUMERIC, 4) AS avg_rate,
    ROUND(MIN(rate)::NUMERIC, 4) AS min_rate,
    ROUND(MAX(rate)::NUMERIC, 4) AS max_rate,
    ROUND((MAX(rate) - MIN(rate))::NUMERIC, 4) AS rate_spread,
    ROUND(STDDEV(rate)::NUMERIC, 4) AS volatility,
    MIN(rate_date) AS period_start,
    MAX(rate_date) AS period_end
FROM exchange_rates
WHERE rate_date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY base_currency, target_currency
ORDER BY volatility DESC NULLS LAST;

COMMENT ON VIEW v_weekly_statistics IS 'Статистика курсов за последнюю неделю';

-- Статистика за месяц
CREATE OR REPLACE VIEW v_monthly_statistics AS
SELECT 
    base_currency || '/' || target_currency AS currency_pair,
    COUNT(*) AS days_count,
    ROUND(AVG(rate)::NUMERIC, 4) AS avg_rate,
    ROUND(MIN(rate)::NUMERIC, 4) AS min_rate,
    ROUND(MAX(rate)::NUMERIC, 4) AS max_rate,
    ROUND((MAX(rate) - MIN(rate))::NUMERIC, 4) AS rate_spread,
    ROUND(STDDEV(rate)::NUMERIC, 4) AS volatility,
    MIN(rate_date) AS period_start,
    MAX(rate_date) AS period_end
FROM exchange_rates
WHERE rate_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY base_currency, target_currency
ORDER BY volatility DESC NULLS LAST;

COMMENT ON VIEW v_monthly_statistics IS 'Статистика курсов за последний месяц';

-- Активность источников данных
CREATE OR REPLACE VIEW v_source_activity AS
SELECT 
    ds.name AS source_name,
    ds.is_active,
    COUNT(pl.log_id) AS total_parses,
    SUM(CASE WHEN pl.status = 'success' THEN 1 ELSE 0 END) AS successful_parses,
    SUM(CASE WHEN pl.status = 'failed' THEN 1 ELSE 0 END) AS failed_parses,
    SUM(pl.records_added) AS total_records_added,
    ROUND(AVG(pl.execution_time_ms)::NUMERIC, 2) AS avg_execution_time_ms,
    MAX(pl.parse_date) AS last_parse_date
FROM data_sources ds
LEFT JOIN parsing_log pl ON ds.source_id = pl.source_id
GROUP BY ds.source_id, ds.name, ds.is_active
ORDER BY ds.priority;

COMMENT ON VIEW v_source_activity IS 'Активность и статистика источников данных';

-- Топ волатильных пар
CREATE OR REPLACE VIEW v_top_volatile_pairs AS
SELECT 
    currency_pair,
    volatility,
    avg_rate,
    min_rate,
    max_rate,
    (max_rate - min_rate) AS rate_spread,
    period_start,
    period_end
FROM currency_statistics
WHERE period_start >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY volatility DESC NULLS LAST
LIMIT 10;

COMMENT ON VIEW v_top_volatile_pairs IS 'Топ-10 самых волатильных валютных пар';
