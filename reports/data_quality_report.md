# Mutual Fund Analytics - Data Quality Report

This report summarizes the data profiling and quality metrics collected during the Day 1 Ingestion pipeline run.

## 1. Executive Summary Table

| Dataset Name | Row Count | Column Count | Memory (MB) | Duplicate Rows | Null Columns | Quality Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 01_fund_master.csv | 40 | 15 | 0.0284 | 0 | 0 | 🟢 Pass |
| 02_nav_history.csv | 46000 | 3 | 3.6413 | 0 | 0 | 🟢 Pass |
| 03_aum_by_fund_house.csv | 90 | 5 | 0.0142 | 0 | 0 | 🟢 Pass |
| 04_monthly_sip_inflows.csv | 48 | 6 | 0.0049 | 0 | 0 | ⚠️ Warnings |
| 05_category_inflows.csv | 144 | 3 | 0.0191 | 0 | 0 | 🟢 Pass |
| 06_industry_folio_count.csv | 21 | 6 | 0.0022 | 0 | 0 | 🟢 Pass |
| 07_scheme_performance.csv | 40 | 19 | 0.0183 | 0 | 0 | 🟢 Pass |
| 08_investor_transactions.csv | 32778 | 13 | 20.6887 | 0 | 0 | 🟢 Pass |
| 09_portfolio_holdings.csv | 322 | 8 | 0.0930 | 0 | 0 | 🟢 Pass |
| 10_benchmark_indices.csv | 8050 | 3 | 1.0947 | 0 | 0 | 🟢 Pass |


## 2. Referential Integrity Check

> [!NOTE]
> Referential integrity check passed. All scheme codes in the fund master exist in the NAV history.

## 3. Detailed Findings per Dataset

### 01_fund_master.csv
- **Row count:** 40
- **Column count:** 15
- **Duplicates detected:** 0
- **Null values detailed count:** None
- **Datatype warnings:** None

---
### 02_nav_history.csv
- **Row count:** 46000
- **Column count:** 3
- **Duplicates detected:** 0
- **Null values detailed count:** None
- **Datatype warnings:** None

---
### 03_aum_by_fund_house.csv
- **Row count:** 90
- **Column count:** 5
- **Duplicates detected:** 0
- **Null values detailed count:** None
- **Datatype warnings:** None

---
### 04_monthly_sip_inflows.csv
- **Row count:** 48
- **Column count:** 6
- **Duplicates detected:** 0
- **Null values detailed count:**
  - `yoy_growth_pct`: 12 nulls
- **Datatype warnings:** None

---
### 05_category_inflows.csv
- **Row count:** 144
- **Column count:** 3
- **Duplicates detected:** 0
- **Null values detailed count:** None
- **Datatype warnings:** None

---
### 06_industry_folio_count.csv
- **Row count:** 21
- **Column count:** 6
- **Duplicates detected:** 0
- **Null values detailed count:** None
- **Datatype warnings:** None

---
### 07_scheme_performance.csv
- **Row count:** 40
- **Column count:** 19
- **Duplicates detected:** 0
- **Null values detailed count:** None
- **Datatype warnings:** None

---
### 08_investor_transactions.csv
- **Row count:** 32778
- **Column count:** 13
- **Duplicates detected:** 0
- **Null values detailed count:** None
- **Datatype warnings:** None

---
### 09_portfolio_holdings.csv
- **Row count:** 322
- **Column count:** 8
- **Duplicates detected:** 0
- **Null values detailed count:** None
- **Datatype warnings:** None

---
### 10_benchmark_indices.csv
- **Row count:** 8050
- **Column count:** 3
- **Duplicates detected:** 0
- **Null values detailed count:** None
- **Datatype warnings:** None

---