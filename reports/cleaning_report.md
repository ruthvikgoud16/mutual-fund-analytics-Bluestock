# Mutual Fund Analytics - Data Cleaning & DB Load Report

This report outlines the results of the cleaning operations, row count profile transformations, and database loading statistics for Day 2.

## 1. Cleaning & Row Counts Summary

| Dataset File | Raw Rows | Processed Rows | Difference | Status |
| :--- | :--- | :--- | :--- | :--- |
| 01_fund_master.csv | 40 | 40 | 0 | Loaded |
| 02_nav_history.csv | 46000 | 64320 | +18320 | Processed |
| 03_aum_by_fund_house.csv | 90 | 90 | 0 | Processed |
| 04_monthly_sip_inflows.csv | 48 | 48 | 0 | Processed |
| 05_category_inflows.csv | 144 | 144 | 0 | Processed |
| 06_industry_folio_count.csv | 21 | 21 | 0 | Processed |
| 07_scheme_performance.csv | 40 | 40 | 0 | Processed |
| 08_investor_transactions.csv | 32778 | 32778 | 0 | Processed |
| 09_portfolio_holdings.csv | 322 | 322 | 0 | Processed |
| 10_benchmark_indices.csv | 8050 | 8050 | 0 | Processed |

> [!NOTE]
> `02_nav_history.csv` row count increased because it was reindexed to cover all trading/calendar days and forward-filled to eliminate weekend/holiday gaps.

## 2. Database Load Statistics

- **SQL Engine:** SQLite
- **File Location:** `/Users/ruthvikgoud/Applications/mutual-fund-analytics-Bluestock/mutual_fund_analytics.db`
- **Date Calendar Range size:** 1608 unique dates loaded.