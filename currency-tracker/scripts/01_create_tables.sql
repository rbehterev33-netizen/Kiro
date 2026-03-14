-- ============================================
-- Создание таблиц Currency Tracker
-- ============================================

-- Расширения
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gist;

-- ============================================
-- 1. Справочник валют
-- ============================================

CREATE TABLE currencies (
    currency_id SERIAL PRIMARY KEY,
    code VARCHAR(3) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    symbol VARCHAR(10),
    country VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE currencies IS 'Справочник валют';
COMMENT ON COLUMN currencies.code IS 'Код валюты ISO 4217 (USD, EUR, RUB)';
COMMENT ON COLUMN currencies.name IS 'Полное название валюты';
COMMENT ON COLUMN currencies.symbol IS 'Символ валюты ($, €, ₽)';

-- ============================================
-- 2. Источники данных
-- ============================================

CREATE TABLE data_sources (
    source_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    url VARCHAR(500),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE data_sources IS 'Источники данных о курсах валют';
COMMENT ON COLUMN data_sources.priority IS 'Приоритет источника (1 - высший)';

-- ============================================
-- 3. Курсы валют (основная таблица)
-- ============================================

CREATE TABLE exchange_rates (
    rate_id BIGSERIAL PRIMARY KEY,
    base_currency VARCHAR(3) NOT NULL,
    target_currency VARCHAR(3) NOT NULL,
    rate DECIMAL(18, 8) NOT NULL,
    rate_date DATE NOT NULL,
    source_id INTEGER REFERENCES data_sources(source_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_positive_rate CHECK (rate > 0),
    CONSTRAINT chk_different_currencies CHECK (base_currency != target_currency)
);

COMMENT ON TABLE exchange_rates IS 'Исторические данные курсов валют';
COMMENT ON COLUMN exchange_rates.base_currency IS 'Базовая валюта (из которой конвертируем)';
COMMENT ON COLUMN exchange_rates.target_currency IS 'Целевая валюта (в которую конвертируем)';
COMMENT ON COLUMN exchange_rates.rate IS 'Курс обмена';

-- ============================================
-- 4. Статистика по валютным парам
-- ============================================

CREATE TABLE currency_statistics (
    stat_id SERIAL PRIMARY KEY,
    currency_pair VARCHAR(7) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    avg_rate DECIMAL(18, 8),
    min_rate DECIMAL(18, 8),
    max_rate DECIMAL(18, 8),
    opening_rate DECIMAL(18, 8),
    closing_rate DECIMAL(18, 8),
    volatility DECIMAL(10, 4),
    total_records INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_period CHECK (period_start <= period_end)
);

COMMENT ON TABLE currency_statistics IS 'Агрегированная статистика по валютным парам';
COMMENT ON COLUMN currency_statistics.currency_pair IS 'Валютная пара (USD/RUB)';
COMMENT ON COLUMN currency_statistics.volatility IS 'Волатильность (стандартное отклонение)';

-- ============================================
-- 5. Лог парсинга
-- ============================================

CREATE TABLE parsing_log (
    log_id BIGSERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES data_sources(source_id),
    parse_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL,
    records_added INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    error_message TEXT,
    execution_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_status CHECK (status IN ('success', 'partial', 'failed'))
);

COMMENT ON TABLE parsing_log IS 'Журнал работы парсера';
COMMENT ON COLUMN parsing_log.status IS 'Статус выполнения: success, partial, failed';
