-- ============================================
-- Система алертов и уведомлений
-- ============================================

-- Таблица алертов
CREATE TABLE currency_alerts (
    alert_id SERIAL PRIMARY KEY,
    currency_pair VARCHAR(7) NOT NULL,
    alert_type VARCHAR(20) NOT NULL,
    threshold_value DECIMAL(18, 8),
    condition VARCHAR(20) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_triggered TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_alert_type CHECK (alert_type IN ('price', 'change_percent', 'volatility')),
    CONSTRAINT chk_condition CHECK (condition IN ('above', 'below', 'equals'))
);

COMMENT ON TABLE currency_alerts IS 'Настройки алертов для валютных пар';

-- Таблица истории срабатывания алертов
CREATE TABLE alert_history (
    history_id BIGSERIAL PRIMARY KEY,
    alert_id INTEGER REFERENCES currency_alerts(alert_id) ON DELETE CASCADE,
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actual_value DECIMAL(18, 8),
    message TEXT
);

COMMENT ON TABLE alert_history IS 'История срабатывания алертов';

-- Функция проверки алертов
CREATE OR REPLACE FUNCTION check_alerts()
RETURNS TABLE(
    alert_id INTEGER,
    currency_pair VARCHAR(7),
    alert_type VARCHAR(20),
    message TEXT
) AS $$
DECLARE
    v_alert RECORD;
    v_current_value DECIMAL;
    v_triggered BOOLEAN;
    v_message TEXT;
BEGIN
    FOR v_alert IN 
        SELECT * FROM currency_alerts WHERE is_active = TRUE
    LOOP
        v_triggered := FALSE;
        
        -- Проверка типа алерта
        IF v_alert.alert_type = 'price' THEN
            -- Получаем текущий курс
            SELECT rate INTO v_current_value
            FROM exchange_rates
            WHERE base_currency = SPLIT_PART(v_alert.currency_pair, '/', 1)
              AND target_currency = SPLIT_PART(v_alert.currency_pair, '/', 2)
            ORDER BY rate_date DESC, created_at DESC
            LIMIT 1;
            
            -- Проверяем условие
            IF v_alert.condition = 'above' AND v_current_value > v_alert.threshold_value THEN
                v_triggered := TRUE;
                v_message := format('Курс %s превысил %s (текущий: %s)', 
                    v_alert.currency_pair, v_alert.threshold_value, v_current_value);
            ELSIF v_alert.condition = 'below' AND v_current_value < v_alert.threshold_value THEN
                v_triggered := TRUE;
                v_message := format('Курс %s упал ниже %s (текущий: %s)', 
                    v_alert.currency_pair, v_alert.threshold_value, v_current_value);
            END IF;
            
        ELSIF v_alert.alert_type = 'change_percent' THEN
            -- Получаем изменение за день
            WITH daily_change AS (
                SELECT 
                    rate,
                    LAG(rate) OVER (ORDER BY rate_date) AS prev_rate
                FROM exchange_rates
                WHERE base_currency = SPLIT_PART(v_alert.currency_pair, '/', 1)
                  AND target_currency = SPLIT_PART(v_alert.currency_pair, '/', 2)
                ORDER BY rate_date DESC
                LIMIT 2
            )
            SELECT ((rate - prev_rate) / prev_rate * 100) INTO v_current_value
            FROM daily_change
            WHERE prev_rate IS NOT NULL;
            
            IF v_alert.condition = 'above' AND ABS(v_current_value) > v_alert.threshold_value THEN
                v_triggered := TRUE;
                v_message := format('Изменение курса %s составило %s%%', 
                    v_alert.currency_pair, ROUND(v_current_value, 2));
            END IF;
        END IF;
        
        -- Если алерт сработал
        IF v_triggered THEN
            -- Записываем в историю
            INSERT INTO alert_history (alert_id, actual_value, message)
            VALUES (v_alert.alert_id, v_current_value, v_message);
            
            -- Обновляем время последнего срабатывания
            UPDATE currency_alerts 
            SET last_triggered = CURRENT_TIMESTAMP
            WHERE currency_alerts.alert_id = v_alert.alert_id;
            
            -- Возвращаем результат
            RETURN QUERY SELECT 
                v_alert.alert_id,
                v_alert.currency_pair,
                v_alert.alert_type,
                v_message;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION check_alerts IS 'Проверка всех активных алертов';

-- Индексы для алертов
CREATE INDEX idx_alerts_active ON currency_alerts(is_active);
CREATE INDEX idx_alerts_pair ON currency_alerts(currency_pair);
CREATE INDEX idx_alert_history_alert ON alert_history(alert_id);
CREATE INDEX idx_alert_history_triggered ON alert_history(triggered_at DESC);

-- Примеры алертов
INSERT INTO currency_alerts (currency_pair, alert_type, threshold_value, condition) VALUES
('USD/RUB', 'price', 95.00, 'above'),
('EUR/RUB', 'price', 98.00, 'below'),
('USD/EUR', 'change_percent', 2.00, 'above');
