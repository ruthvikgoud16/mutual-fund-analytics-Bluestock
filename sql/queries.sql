-- ==========================================
-- Mutual Fund Analytics Platform - SQL Queries
-- Target Engine: SQLite/PostgreSQL
-- ==========================================

-- 1. Top Fund Houses by Latest AUM
-- Purpose: Retrieves the latest quarterly AUM for each fund house, sorted from highest to lowest.
SELECT 
    fund_house,
    date_id AS reporting_date,
    aum_crore,
    num_schemes
FROM fact_aum
WHERE date_id = (SELECT MAX(date_id) FROM fact_aum)
ORDER BY aum_crore DESC;

-- 2. Average NAV by Fund Category
-- Purpose: Calculates the average NAV across all schemes grouped by their primary SEBI category.
SELECT 
    f.category,
    COUNT(DISTINCT f.amfi_code) AS total_schemes,
    ROUND(AVG(n.nav), 4) AS avg_nav,
    ROUND(MIN(n.nav), 4) AS min_nav,
    ROUND(MAX(n.nav), 4) AS max_nav
FROM dim_fund f
INNER JOIN fact_nav n ON f.amfi_code = n.amfi_code
GROUP BY f.category
ORDER BY avg_nav DESC;

-- 3. Monthly Industry SIP Inflow Trends
-- Purpose: Evaluates month-on-month industry SIP inflows, active SIP accounts, and YoY growth rates.
SELECT 
    month,
    sip_inflow_crore,
    active_sip_accounts_crore,
    new_sip_accounts_lakh,
    yoy_growth_pct
FROM fact_sip_industry
ORDER BY month DESC;

-- 4. Transaction Volume and Total Amount by State and Investor Demographics
-- Purpose: Summarizes transaction activities (count, average volume, total amount) across different states.
SELECT 
    state,
    transaction_type,
    COUNT(tx_id) AS total_transactions,
    ROUND(AVG(amount_inr), 2) AS avg_transaction_amount,
    SUM(amount_inr) AS total_amount_inr
FROM fact_transactions
WHERE kyc_status = 'Verified'
GROUP BY state, transaction_type
HAVING total_transactions > 5
ORDER BY total_amount_inr DESC;

-- 5. Top 5 Best-Performing Schemes Based on 3-Year Return
-- Purpose: Ranks and selects the top 5 mutual fund schemes by 3-year performance, including risk assessment.
SELECT 
    f.scheme_name,
    f.category,
    p.return_3yr_pct,
    p.benchmark_3yr_pct,
    p.alpha,
    p.sharpe_ratio,
    p.risk_grade
FROM dim_fund f
INNER JOIN fact_performance p ON f.amfi_code = p.amfi_code
ORDER BY p.return_3yr_pct DESC
LIMIT 5;

-- 6. Schemes Outperforming Their Benchmark (3-Year CAGR)
-- Purpose: Lists schemes that have generated positive alpha over their index benchmark over 3 years.
SELECT 
    f.scheme_name,
    f.benchmark,
    p.return_3yr_pct AS scheme_return_3yr,
    p.benchmark_3yr_pct AS benchmark_return_3yr,
    ROUND(p.return_3yr_pct - p.benchmark_3yr_pct, 2) AS alpha_generated
FROM dim_fund f
INNER JOIN fact_performance p ON f.amfi_code = p.amfi_code
WHERE p.return_3yr_pct > p.benchmark_3yr_pct
ORDER BY alpha_generated DESC;

-- 7. Portfolio Concentration: Top 3 Stock Holdings per Fund
-- Purpose: Finds the top 3 stock allocations by weight for each mutual fund using window functions.
WITH RankedHoldings AS (
    SELECT 
        f.scheme_name,
        p.stock_symbol,
        p.stock_name,
        p.sector,
        p.weight_pct,
        ROW_NUMBER() OVER (PARTITION BY p.amfi_code ORDER BY p.weight_pct DESC) as rank
    FROM fact_portfolio p
    INNER JOIN dim_fund f ON p.amfi_code = f.amfi_code
)
SELECT 
    scheme_name,
    stock_name,
    sector,
    weight_pct,
    rank
FROM RankedHoldings
WHERE rank <= 3
ORDER BY scheme_name, rank;

-- 8. Category and Sub-category Distribution of Schemes
-- Purpose: Displays a matrix of mutual fund scheme counts across categories and sub-categories.
SELECT 
    category,
    sub_category,
    COUNT(amfi_code) AS scheme_count,
    ROUND(AVG(expense_ratio_pct), 3) AS avg_expense_ratio_pct
FROM dim_fund
GROUP BY category, sub_category
ORDER BY category, scheme_count DESC;

-- 9. Latest Net Asset Value (NAV) per Scheme
-- Purpose: Retrieves the most recent NAV valuation for each scheme using a window ranking function.
WITH LatestNAV AS (
    SELECT 
        f.scheme_name,
        f.plan,
        n.date_id,
        n.nav,
        ROW_NUMBER() OVER (PARTITION BY n.amfi_code ORDER BY n.date_id DESC) as rn
    FROM fact_nav n
    INNER JOIN dim_fund f ON n.amfi_code = f.amfi_code
)
SELECT 
    scheme_name,
    plan,
    date_id AS valuation_date,
    nav
FROM LatestNAV
WHERE rn = 1
ORDER BY scheme_name;

-- 10. Cumulative Transaction Amount over Time by Payment Mode
-- Purpose: Calculates running/cumulative totals of transactions for payment options to analyze liquidity trends.
SELECT 
    transaction_date,
    payment_mode,
    SUM(amount_inr) AS daily_amount_inr,
    SUM(SUM(amount_inr)) OVER (PARTITION BY payment_mode ORDER BY transaction_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_amount_inr
FROM fact_transactions
GROUP BY transaction_date, payment_mode
ORDER BY payment_mode, transaction_date;
