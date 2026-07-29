# Entity Relationship Diagram & Join Strategy - Mutual Fund Analytics

This document defines the relational database model (ERD), relationships, indexing rules, and join strategy designed for the Mutual Fund Analytics Platform.

---

## 1. Dataset Relationship Diagram

This diagram shows how the pre-packaged raw datasets map to each other at a business concept level:

```mermaid
graph TD
    FM[01_fund_master] -->|amfi_code| NH[02_nav_history]
    FM -->|amfi_code| SP[07_scheme_performance]
    FM -->|amfi_code| IT[08_investor_transactions]
    FM -->|amfi_code| PH[09_portfolio_holdings]
    FM -->|fund_house| AUM[03_aum_by_fund_house]
    BI[10_benchmark_indices] -->|date| NH
```

---

## 2. Entity Relationship Diagram (ERD)

The structured star schema is represented below. It translates raw files into standard normalized dimensions (`dim_`) and transaction/price facts (`fact_`):

```mermaid
erDiagram
    dim_fund {
        INT amfi_code PK
        VARCHAR fund_house
        VARCHAR scheme_name
        VARCHAR category
        VARCHAR sub_category
        VARCHAR plan
        DATE launch_date
        VARCHAR benchmark
        DECIMAL expense_ratio_pct
        DECIMAL exit_load_pct
        DECIMAL min_sip_amount
        DECIMAL min_lumpsum_amount
        VARCHAR fund_manager
        VARCHAR risk_category
        VARCHAR sebi_category_code
    }

    dim_date {
        DATE date_id PK
        INT year
        INT month
        INT quarter
        BOOLEAN is_weekday
    }

    fact_nav {
        INT amfi_code FK, PK
        DATE date_id FK, PK
        DECIMAL nav
        DECIMAL daily_return_pct
    }

    fact_transactions {
        VARCHAR tx_id PK
        VARCHAR investor_id
        INT amfi_code FK
        DATE transaction_date FK
        VARCHAR transaction_type
        INT amount_inr
        VARCHAR state
        VARCHAR city
        VARCHAR city_tier
        VARCHAR age_group
        VARCHAR gender
        DECIMAL annual_income_lakh
        VARCHAR payment_mode
        VARCHAR kyc_status
    }

    fact_performance {
        INT amfi_code PK, FK
        DECIMAL return_1yr_pct
        DECIMAL return_3yr_pct
        DECIMAL return_5yr_pct
        DECIMAL benchmark_3yr_pct
        DECIMAL alpha
        DECIMAL beta
        DECIMAL sharpe_ratio
        DECIMAL sortino_ratio
        DECIMAL std_dev_ann_pct
        DECIMAL max_drawdown_pct
        INT morningstar_rating
        VARCHAR risk_grade
    }

    fact_portfolio {
        INT amfi_code PK, FK
        VARCHAR stock_symbol PK
        VARCHAR stock_name
        VARCHAR sector
        DECIMAL weight_pct
        DECIMAL market_value_cr
        DECIMAL current_price_inr
        DATE portfolio_date PK, FK
    }

    fact_aum {
        VARCHAR fund_house PK, FK
        DATE date_id PK, FK
        DECIMAL aum_lakh_crore
        DECIMAL aum_crore
        INT num_schemes
    }

    dim_fund ||--o{ fact_nav : "references"
    dim_fund ||--o{ fact_transactions : "references"
    dim_fund ||--|| fact_performance : "references"
    dim_fund ||--o{ fact_portfolio : "references"
    dim_date ||--o{ fact_nav : "references"
    dim_date ||--o{ fact_transactions : "references"
    dim_date ||--o{ fact_aum : "references"
```

---

## 3. Recommended SQL Join Strategy

1. **NAV and Benchmark Joins (For Alpha/Beta & Tracking Error):**
   * Join `fact_nav` and `fact_nav` of the benchmark index (via `10_benchmark_indices`) on the `date` key. Use an `INNER JOIN` to align active trading dates.
   * *SQL Pattern:*
     ```sql
     SELECT n.date, n.amfi_code, n.nav, b.close_value AS benchmark_close
     FROM fact_nav n
     INNER JOIN fact_benchmark b ON n.date_id = b.date_id AND b.index_name = n.benchmark_name;
     ```

2. **Investor Transactions to Fund Metadata (For Demographic segmentation):**
   * Join `fact_transactions` to `dim_fund` using an `INNER JOIN` on `amfi_code` to enrich investor cohorts with fund risk categories, fund houses, and expense ratios.
   * *SQL Pattern:*
     ```sql
     SELECT t.*, f.risk_category, f.fund_house
     FROM fact_transactions t
     INNER JOIN dim_fund f ON t.amfi_code = f.amfi_code;
     ```

3. **Portfolio Concentration Join (HHI computation):**
   * Join `fact_portfolio` with `dim_fund` on `amfi_code` to filter equity holdings by category (e.g. Large vs Mid Cap) and group weight distributions.
   * *SQL Pattern:*
     ```sql
     SELECT p.amfi_code, f.scheme_name, p.sector, sum(p.weight_pct) as sector_weight
     FROM fact_portfolio p
     INNER JOIN dim_fund f ON p.amfi_code = f.amfi_code
     GROUP BY p.amfi_code, f.scheme_name, p.sector;
     ```

---

## 4. Indexing Recommendations

To support sub-second query performance for the analytics dashboard, implement the following indexes:

1. **`idx_fact_nav_composite`:** Create a composite index on `fact_nav(amfi_code, date_id)`. Since historical NAV is queried chronologically per scheme, this index enables high-performance ranges and CAGR lookups.
2. **`idx_fact_transactions_amfi`:** Index `fact_transactions(amfi_code)` and `fact_transactions(transaction_date)` to speed up aggregation runs for transaction timelines.
3. **`idx_fact_portfolio_composite`:** Composite index on `fact_portfolio(amfi_code, portfolio_date)` for portfolio snapshot retrievals.
4. **`idx_fact_benchmark_index`:** Composite index on `fact_benchmark(index_name, date_id)` to speed up benchmark regressions.
