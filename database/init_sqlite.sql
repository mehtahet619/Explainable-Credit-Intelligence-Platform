-- SQLite-compatible schema for CredTech Platform

-- Companies table
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Market data table
CREATE TABLE IF NOT EXISTS market_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time DATETIME NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    open_price DECIMAL(15,4),
    high_price DECIMAL(15,4),
    low_price DECIMAL(15,4),
    close_price DECIMAL(15,4),
    volume BIGINT,
    UNIQUE(time, symbol)
);

-- Financial data table
CREATE TABLE IF NOT EXISTS financial_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time DATETIME NOT NULL,
    company_id INTEGER NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    value DECIMAL(20,4),
    source VARCHAR(50),
    FOREIGN KEY (company_id) REFERENCES companies(id),
    UNIQUE(time, company_id, metric_name)
);

-- News events table
CREATE TABLE IF NOT EXISTS news_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    timestamp DATETIME NOT NULL,
    headline TEXT NOT NULL,
    content TEXT,
    source VARCHAR(100),
    sentiment_score DECIMAL(5,2) DEFAULT 50.0,
    impact_score DECIMAL(5,2) DEFAULT 30.0,
    event_type VARCHAR(50) DEFAULT 'general',
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- Credit scores table
CREATE TABLE IF NOT EXISTS credit_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time DATETIME NOT NULL,
    company_id INTEGER NOT NULL,
    score DECIMAL(5,2) NOT NULL,
    confidence DECIMAL(5,4),
    model_version VARCHAR(50),
    FOREIGN KEY (company_id) REFERENCES companies(id),
    UNIQUE(time, company_id)
);

-- Feature importance table
CREATE TABLE IF NOT EXISTS feature_importance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    timestamp DATETIME NOT NULL,
    feature_name VARCHAR(100) NOT NULL,
    importance_value DECIMAL(10,6),
    shap_value DECIMAL(10,6),
    feature_value DECIMAL(15,4),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- Model performance table
CREATE TABLE IF NOT EXISTS model_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_version VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    accuracy DECIMAL(5,4),
    precision_score DECIMAL(5,4),
    recall DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    training_samples INTEGER,
    validation_samples INTEGER
);

-- Data source status
CREATE TABLE IF NOT EXISTS data_source_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name VARCHAR(100) NOT NULL UNIQUE,
    last_update DATETIME,
    status VARCHAR(20) DEFAULT 'active',
    error_count INTEGER DEFAULT 0,
    last_error TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_credit_scores_company_time ON credit_scores (company_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_financial_data_company_metric ON financial_data (company_id, metric_name, time DESC);
CREATE INDEX IF NOT EXISTS idx_news_events_company_time ON news_events (company_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_market_data_symbol_time ON market_data (symbol, time DESC);

-- Insert sample companies
INSERT OR IGNORE INTO companies (symbol, name, sector, industry, market_cap) VALUES
('AAPL', 'Apple Inc.', 'Technology', 'Consumer Electronics', 3000000000000),
('MSFT', 'Microsoft Corporation', 'Technology', 'Software', 2800000000000),
('GOOGL', 'Alphabet Inc.', 'Technology', 'Internet Services', 1700000000000),
('TSLA', 'Tesla Inc.', 'Consumer Cyclical', 'Auto Manufacturers', 800000000000),
('AMZN', 'Amazon.com Inc.', 'Consumer Cyclical', 'Internet Retail', 1500000000000);