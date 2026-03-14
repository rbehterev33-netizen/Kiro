-- ============================================
-- Полезные функции для работы с курсами
-- ============================================

-- Функция конвертации валют
CREATE OR REPLACE FUNCTION convert_currency(
    p_amount DECIMAL,
    p_from_currency VARCHAR(3),
    p_to_currency VARCHAR(3),
    p_date DATE DEFAULT CURRENT_DATE
)
RETURNS DECIMAL AS $$
DECLARE
    v_rate DECIMAL;
    v_result DECIMAL;
BEGIN
    -- Если валюты одинаковые
    IF p_from_currency = p_to_currency THEN
        RETURN p_amount;
    END IF;
    
    -- Получаем курс
    SELECT rate INTO v_rate
    FROM exchange_rates
    WHERE base_currency = p_from_currency
      AND target_currency = p_to_currency
      AND rate_date <= p_date
    ORDER BY rate_date DESC, created_at DESC
    LIMIT 1;
    
    IF v_rate IS NULL THEN
        RAISE EXCEPTION 'Курс не найден для пары %/%', p_from_currency, p_to_currency;
    END IF;
    
    v_result := p_amount * v_rate;
    RETURN ROUND(v_result, 2);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION convert_currency IS 'Конвертация суммы из одной валюты в другую';

-- Функция получения кросс-курса
CREATE OR REPLACE FUNCTION get_cross_rate(
    p_from_currency VARCHAR(3),
    p_to_currency VARCHAR(3),
    p_base_currency VARCHAR(3) DEFAULT 'USD',
    p_date DATE DEFAULT CURRENT_DATE
)
RETURNS DECIMAL AS $$
DECLARE
    v_rate_from DECIMAL;
    v_rate_to DECIMAL;
    v_cross_rate DECIMAL;
BEGIN
    -- Получаем курсы к базовой валюте
    SELECT rate INTO v_rate_from
    FROM exchange_rates
    WHERE base_currency = p_from_currency
      AND target_currency = p_base_currency
      AND rate_date <= p_date
    ORDER BY rate_date DESC, created_at DESC
    LIMIT 1;
    
    SELECT rate INTO v_rate_to
    FROM exchange_rates
    WHERE base_currency = p_to_currency
      AND target_currency = p_base_currency
      AND rate_date <= p_date
    ORDER BY rate_date DESC, created_at DESC
    LIMIT 1;
    
    IF v_rate_from IS NULL OR v_rate_to IS NULL THEN
        RAISE EXCEPTION 'Не удалось получить кросс-курс';
    END IF;
    
    v_cross_rate := v_rate_from / v_rate_to;
    RETURN ROUND(v_cross_rate, 6);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_cross_rate IS 'Расчет кросс-курса через базовую валюту';

-- Функция прогнозирования курса (простое скользящее среднее)
CREATE OR REPLACE FUNCTION predict_rate_sma(
    p_base_currency VARCHAR(3),
    p_target_currency VARCHAR(3),
    p_days INTEGER DEFAULT 7
)
RETURNS DECIMAL AS $$
DECLARE
    v_predicted_rate DECIMAL;
BEGIN
    SELECT AVG(rate) INTO v_predicted_rate
    FROM (
        SELECT rate
        FROM exchange_rates
        WHERE base_currency = p_base_currency
          AND target_currency = p_target_currency
        ORDER BY rate_date DESC
        LIMIT p_days
    ) recent_rates;
    
    RETURN ROUND(v_predicted_rate, 4);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION predict_rate_sma IS 'Прогноз курса на основе скользящего среднего';

-- Функция определения тренда
CREATE OR REPLACE FUNCTION get_trend(
    p_base_currency VARCHAR(3),
    p_target_currency VARCHAR(3),
    p_days INTEGER DEFAULT 7
)
RETURNS VARCHAR AS $$
DECLARE
    v_first_rate DECIMAL;
    v_last_rate DECIMAL;
    v_change_percent DECIMAL;
BEGIN
    -- Получаем первый курс периода
    SELECT rate INTO v_first_rate
    FROM exchange_rates
    WHERE base_currency = p_base_currency
      AND target_currency = p_target_currency
      AND rate_date >= CURRENT_DATE - p_days
    ORDER BY rate_date ASC, created_at ASC
    LIMIT 1;
    
    -- Получаем последний курс
    SELECT rate INTO v_last_rate
    FROM exchange_rates
    WHERE base_currency = p_base_currency
      AND target_currency = p_target_currency
    ORDER BY rate_date DESC, created_at DESC
    LIMIT 1;
    
    IF v_first_rate IS NULL OR v_last_rate IS NULL THEN
        RETURN 'unknown';
    END IF;
    
    v_change_percent := ((v_last_rate - v_first_rate) / v_first_rate) * 100;
    
    IF v_change_percent > 1 THEN
        RETURN 'uptrend';
    ELSIF v_change_percent < -1 THEN
        RETURN 'downtrend';
    ELSE
        RETURN 'stable';
    END IF;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_trend IS 'Определение тренда валютной пары';

-- Функция расчета RSI (Relative Strength Index)
CREATE OR REPLACE FUNCTION calculate_rsi(
    p_base_currency VARCHAR(3),
    p_target_currency VARCHAR(3),
    p_period INTEGER DEFAULT 14
)
RETURNS DECIMAL AS $$
DECLARE
    v_avg_gain DECIMAL;
    v_avg_loss DECIMAL;
    v_rs DECIMAL;
    v_rsi DECIMAL;
BEGIN
    WITH price_changes AS (
        SELECT 
            rate,
            rate - LAG(rate) OVER (ORDER BY rate_date) AS change
        FROM exchange_rates
        WHERE base_currency = p_base_currency
          AND target_currency = p_target_currency
        ORDER BY rate_date DESC
        LIMIT p_period + 1
    ),
    gains_losses AS (
        SELECT 
            CASE WHEN change > 0 THEN change ELSE 0 END AS gain,
            CASE WHEN change < 0 THEN ABS(change) ELSE 0 END AS loss
        FROM price_changes
        WHERE change IS NOT NULL
    )
    SELECT 
        AVG(gain),
        AVG(loss)
    INTO v_avg_gain, v_avg_loss
    FROM gains_losses;
    
    IF v_avg_loss = 0 THEN
        RETURN 100;
    END IF;
    
    v_rs := v_avg_gain / v_avg_loss;
    v_rsi := 100 - (100 / (1 + v_rs));
    
    RETURN ROUND(v_rsi, 2);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_rsi IS 'Расчет индекса относительной силы (RSI)';

-- Функция поиска арбитражных возможностей
CREATE OR REPLACE FUNCTION find_arbitrage_opportunities(
    p_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE(
    currency_a VARCHAR(3),
    currency_b VARCHAR(3),
    currency_c VARCHAR(3),
    profit_percent DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    WITH latest_rates AS (
        SELECT DISTINCT ON (base_currency, target_currency)
            base_currency,
            target_currency,
            rate
        FROM exchange_rates
        WHERE rate_date = p_date
        ORDER BY base_currency, target_currency, created_at DESC
    )
    SELECT 
        r1.base_currency AS currency_a,
        r1.target_currency AS currency_b,
        r2.target_currency AS currency_c,
        ROUND(((r1.rate * r2.rate * r3.rate - 1) * 100)::NUMERIC, 4) AS profit_percent
    FROM latest_rates r1
    JOIN latest_rates r2 ON r1.target_currency = r2.base_currency
    JOIN latest_rates r3 ON r2.target_currency = r3.base_currency 
                         AND r3.target_currency = r1.base_currency
    WHERE (r1.rate * r2.rate * r3.rate - 1) * 100 > 0.1
    ORDER BY profit_percent DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION find_arbitrage_opportunities IS 'Поиск арбитражных возможностей';

-- Функция получения исторических данных в JSON
CREATE OR REPLACE FUNCTION get_rate_history_json(
    p_base_currency VARCHAR(3),
    p_target_currency VARCHAR(3),
    p_days INTEGER DEFAULT 30
)
RETURNS JSON AS $$
BEGIN
    RETURN (
        SELECT json_agg(
            json_build_object(
                'date', rate_date,
                'rate', rate,
                'change', rate - LAG(rate) OVER (ORDER BY rate_date)
            )
        )
        FROM exchange_rates
        WHERE base_currency = p_base_currency
          AND target_currency = p_target_currency
          AND rate_date >= CURRENT_DATE - p_days
        ORDER BY rate_date
    );
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_rate_history_json IS 'Получение истории курсов в формате JSON';
