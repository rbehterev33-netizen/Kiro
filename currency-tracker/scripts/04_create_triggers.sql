-- ============================================
-- Создание триггеров
-- ============================================

-- Функция обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггер для currencies
CREATE TRIGGER trg_currencies_updated_at
    BEFORE UPDATE ON currencies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Функция автоматического расчета статистики
CREATE OR REPLACE FUNCTION calculate_currency_statistics(
    p_currency_pair VARCHAR(7),
    p_start_date DATE,
    p_end_date DATE
)
RETURNS void AS $$
DECLARE
    v_base VARCHAR(3);
    v_target VARCHAR(3);
BEGIN
    -- Разбиваем пару на базовую и целевую валюту
    v_base := SPLIT_PART(p_currency_pair, '/', 1);
    v_target := SPLIT_PART(p_currency_pair, '/', 2);
    
    -- Удаляем старую статистику если есть
    DELETE FROM currency_statistics 
    WHERE currency_pair = p_currency_pair 
      AND period_start = p_start_date 
      AND period_end = p_end_date;
    
    -- Вставляем новую статистику
    INSERT INTO currency_statistics (
        currency_pair,
        period_start,
        period_end,
        avg_rate,
        min_rate,
        max_rate,
        opening_rate,
        closing_rate,
        volatility,
        total_records
    )
    SELECT 
        p_currency_pair,
        p_start_date,
        p_end_date,
        AVG(rate),
        MIN(rate),
        MAX(rate),
        (SELECT rate FROM exchange_rates 
         WHERE base_currency = v_base 
           AND target_currency = v_target 
           AND rate_date = p_start_date 
         ORDER BY created_at DESC LIMIT 1),
        (SELECT rate FROM exchange_rates 
         WHERE base_currency = v_base 
           AND target_currency = v_target 
           AND rate_date = p_end_date 
         ORDER BY created_at DESC LIMIT 1),
        STDDEV(rate),
        COUNT(*)
    FROM exchange_rates
    WHERE base_currency = v_base
      AND target_currency = v_target
      AND rate_date BETWEEN p_start_date AND p_end_date;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_currency_statistics IS 'Расчет статистики по валютной паре за период';
