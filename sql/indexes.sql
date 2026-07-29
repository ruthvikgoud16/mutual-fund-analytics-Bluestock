-- Performance optimization indexes

-- Index for fast NAV history range queries
CREATE INDEX idx_fact_nav_composite ON fact_nav (amfi_code, date_id);

-- Index for investor transactions aggregation
CREATE INDEX idx_fact_transactions_amfi ON fact_transactions (amfi_code);
CREATE INDEX idx_fact_transactions_date ON fact_transactions (transaction_date);

-- Index for portfolio snapshot calculations
CREATE INDEX idx_fact_portfolio_composite ON fact_portfolio (amfi_code, portfolio_date);
