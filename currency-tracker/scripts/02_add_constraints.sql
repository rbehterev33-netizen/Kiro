-- ============================================
-- Добавление ограничений целостности
-- ============================================

-- Внешние ключи для exchange_rates
ALTER TABLE exchange_rates
    ADD CONSTRAINT fk_base_currency 
    FOREIGN KEY (base_currency) 
    REFERENCES currencies(code) 
    ON DELETE RESTRICT;

ALTER TABLE exchange_rates
    ADD CONSTRAINT fk_target_currency 
    FOREIGN KEY (target_currency) 
    REFERENCES currencies(code) 
    ON DELETE RESTRICT;

-- Уникальность записи курса (одна запись на дату + пара + источник)
CREATE UNIQUE INDEX idx_unique_rate 
    ON exchange_rates(base_currency, target_currency, rate_date, source_id);

-- Уникальность статистики (одна запись на период + пара)
CREATE UNIQUE INDEX idx_unique_stat 
    ON currency_statistics(currency_pair, period_start, period_end);

-- Уникальность лога парсинга
CREATE UNIQUE INDEX idx_unique_parse_log 
    ON parsing_log(source_id, parse_date, created_at);
