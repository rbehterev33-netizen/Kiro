-- ============================================
-- Создание индексов для производительности
-- ============================================

-- Индексы для currencies
CREATE INDEX idx_currencies_code ON currencies(code);
CREATE INDEX idx_currencies_active ON currencies(is_active);
CREATE INDEX idx_currencies_name_trgm ON currencies USING gin (name gin_trgm_ops);

-- Индексы для exchange_rates
CREATE INDEX idx_rates_base_currency ON exchange_rates(base_currency);
CREATE INDEX idx_rates_target_currency ON exchange_rates(target_currency);
CREATE INDEX idx_rates_date ON exchange_rates(rate_date DESC);
CREATE INDEX idx_rates_source ON exchange_rates(source_id);
CREATE INDEX idx_rates_pair_date ON exchange_rates(base_currency, target_currency, rate_date DESC);
CREATE INDEX idx_rates_date_range ON exchange_rates USING btree (rate_date);

-- Индексы для currency_statistics
CREATE INDEX idx_stats_pair ON currency_statistics(currency_pair);
CREATE INDEX idx_stats_period ON currency_statistics(period_start, period_end);
CREATE INDEX idx_stats_volatility ON currency_statistics(volatility DESC);

-- Индексы для data_sources
CREATE INDEX idx_sources_active ON data_sources(is_active);
CREATE INDEX idx_sources_priority ON data_sources(priority);

-- Индексы для parsing_log
CREATE INDEX idx_log_source ON parsing_log(source_id);
CREATE INDEX idx_log_date ON parsing_log(parse_date DESC);
CREATE INDEX idx_log_status ON parsing_log(status);
CREATE INDEX idx_log_created ON parsing_log(created_at DESC);
