-- ============================================
-- Тестовые данные
-- ============================================

-- Валюты
INSERT INTO currencies (code, name, symbol, country) VALUES
('USD', 'US Dollar', '$', 'United States'),
('EUR', 'Euro', '€', 'European Union'),
('RUB', 'Russian Ruble', '₽', 'Russia'),
('GBP', 'British Pound', '£', 'United Kingdom'),
('JPY', 'Japanese Yen', '¥', 'Japan'),
('CNY', 'Chinese Yuan', '¥', 'China'),
('CHF', 'Swiss Franc', 'Fr', 'Switzerland'),
('CAD', 'Canadian Dollar', 'C$', 'Canada'),
('AUD', 'Australian Dollar', 'A$', 'Australia'),
('KZT', 'Kazakhstani Tenge', '₸', 'Kazakhstan');

-- Источники данных
INSERT INTO data_sources (name, url, description, priority) VALUES
('Central Bank of Russia', 'https://www.cbr.ru/scripts/XML_daily.asp', 'Официальные курсы ЦБ РФ', 1),
('European Central Bank', 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml', 'Официальные курсы ЕЦБ', 2),
('Exchange Rate API', 'https://api.exchangerate-api.com/v4/latest/', 'Публичный API курсов валют', 3);

-- Тестовые курсы за последние 7 дней
DO $$
DECLARE
    v_date DATE;
    v_source_id INTEGER;
BEGIN
    SELECT source_id INTO v_source_id FROM data_sources WHERE name = 'Central Bank of Russia';
    
    FOR i IN 0..6 LOOP
        v_date := CURRENT_DATE - i;
        
        -- USD/RUB
        INSERT INTO exchange_rates (base_currency, target_currency, rate, rate_date, source_id)
        VALUES ('USD', 'RUB', 92.50 + (RANDOM() * 2 - 1), v_date, v_source_id);
        
        -- EUR/RUB
        INSERT INTO exchange_rates (base_currency, target_currency, rate, rate_date, source_id)
        VALUES ('EUR', 'RUB', 100.20 + (RANDOM() * 2 - 1), v_date, v_source_id);
        
        -- USD/EUR
        INSERT INTO exchange_rates (base_currency, target_currency, rate, rate_date, source_id)
        VALUES ('USD', 'EUR', 0.92 + (RANDOM() * 0.02 - 0.01), v_date, v_source_id);
        
        -- GBP/RUB
        INSERT INTO exchange_rates (base_currency, target_currency, rate, rate_date, source_id)
        VALUES ('GBP', 'RUB', 117.30 + (RANDOM() * 2 - 1), v_date, v_source_id);
        
        -- CNY/RUB
        INSERT INTO exchange_rates (base_currency, target_currency, rate, rate_date, source_id)
        VALUES ('CNY', 'RUB', 12.80 + (RANDOM() * 0.5 - 0.25), v_date, v_source_id);
    END LOOP;
END $$;

-- Расчет статистики за неделю
SELECT calculate_currency_statistics('USD/RUB', CURRENT_DATE - 6, CURRENT_DATE);
SELECT calculate_currency_statistics('EUR/RUB', CURRENT_DATE - 6, CURRENT_DATE);
SELECT calculate_currency_statistics('USD/EUR', CURRENT_DATE - 6, CURRENT_DATE);

-- Лог парсинга
INSERT INTO parsing_log (source_id, parse_date, status, records_added, execution_time_ms)
SELECT 
    source_id,
    CURRENT_DATE,
    'success',
    5,
    FLOOR(RANDOM() * 1000 + 100)::INTEGER
FROM data_sources
WHERE is_active = TRUE;

-- Вывод статистики
SELECT 
    'Currencies' AS table_name, 
    COUNT(*) AS records 
FROM currencies
UNION ALL
SELECT 'Data Sources', COUNT(*) FROM data_sources
UNION ALL
SELECT 'Exchange Rates', COUNT(*) FROM exchange_rates
UNION ALL
SELECT 'Statistics', COUNT(*) FROM currency_statistics
UNION ALL
SELECT 'Parsing Log', COUNT(*) FROM parsing_log;
