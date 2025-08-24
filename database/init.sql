-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Companies/Issuers table
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Credit scores time series
CREATE TABLE credit_scores (
    time TIMESTAMPTZ NOT NULL,
    company_id INTEGER REFERENCES companies(id),
    score DECIMAL(5,2) NOT NULL,
    confidence DECIMAL(5,2),
    model_version VARCHAR(50),
    PRIMARY KEY (time, company_id)
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('credit_scores', 'time');

-- Feature importance for explainability
CREATE TABLE feature_importance (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    timestamp TIMESTAMPTZ NOT NULL,
    feature_name VARCHAR(100) NOT NULL,
    importance_value DECIMAL(10,6) NOT NULL,
    shap_value DECIMAL(10,6),
    feature_value DECIMAL(15,6)
);

-- Financial data time series
CREATE TABLE financial_data (
    time TIMESTAMPTZ NOT NULL,
    company_id INTEGER REFERENCES companies(id),
    metric_name VARCHAR(100) NOT NULL,
    value DECIMAL(20,6),
    source VARCHAR(50),
    PRIMARY KEY (time, company_id, metric_name)
);

SELECT create_hypertable('financial_data', 'time');

-- News and events
CREATE TABLE news_events (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    timestamp TIMESTAMPTZ NOT NULL,
    headline TEXT NOT NULL,
    content TEXT,
    source VARCHAR(100),
    sentiment_score DECIMAL(5,2),
    impact_score DECIMAL(5,2),
    event_type VARCHAR(50),
    processed BOOLEAN DEFAULT FALSE
);

-- Market data
CREATE TABLE market_data (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    open_price DECIMAL(15,6),
    high_price DECIMAL(15,6),
    low_price DECIMAL(15,6),
    close_price DECIMAL(15,6),
    volume BIGINT,
    PRIMARY KEY (time, symbol)
);

SELECT create_hypertable('market_data', 'time');

-- Model performance tracking
CREATE TABLE model_performance (
    id SERIAL PRIMARY KEY,
    model_version VARCHAR(50) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    accuracy DECIMAL(5,4),
    precision_score DECIMAL(5,4),
    recall DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    training_samples INTEGER,
    validation_samples INTEGER
);

-- Data source status
CREATE TABLE data_source_status (
    id SERIAL PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,
    last_update TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'active',
    error_count INTEGER DEFAULT 0,
    last_error TEXT
);

-- Indexes for performance
CREATE INDEX idx_credit_scores_company_time ON credit_scores (company_id, time DESC);
CREATE INDEX idx_financial_data_company_metric ON financial_data (company_id, metric_name, time DESC);
CREATE INDEX idx_news_events_company_time ON news_events (company_id, timestamp DESC);
CREATE INDEX idx_market_data_symbol_time ON market_data (symbol, time DESC);

-- Insert sample companies
INSERT INTO companies (symbol, name, sector, industry, market_cap) VALUES
('AAPL', 'Apple Inc.', 'Technology', 'Consumer Electronics', 3000000000000),
('MSFT', 'Microsoft Corporation', 'Technology', 'Software', 2800000000000),
('GOOGL', 'Alphabet Inc.', 'Technology', 'Internet Services', 1700000000000),
('TSLA', 'Tesla Inc.', 'Consumer Cyclical', 'Auto Manufacturers', 800000000000),
('JPM', 'JPMorgan Chase & Co.', 'Financial Services', 'Banks', 450000000000);

-- Insert initial data source status
INSERT INTO data_source_status (source_name, status) VALUES
('yahoo_finance', 'active'),
('alpha_vantage', 'active'),
('sec_edgar', 'active'),
('news_api', 'active');