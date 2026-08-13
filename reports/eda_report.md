# Phase 3: Exploratory Data Analysis (EDA) Verification Report

## 1. Executive Summary
This report presents the verified Exploratory Data Analysis (EDA) for the **Bluestock Mutual Fund Analytics Platform**. The analysis investigates 40 mutual fund schemes, 64,320 daily NAV observations, 90 quarterly AUM snapshots, 48 monthly SIP flow metrics, 21 industry folio milestones, 32,778 investor transactions, and 322 equity portfolio holdings stored in normalized relational structures (`mutual_fund_analytics.db`).

---

## 2. Requirement Verification & Key Analytical Metrics

### 1. NAV Trend Analysis (REQ-01)
- **Dataset**: `02_nav_history.csv` / `fact_nav` (64,320 rows, 40 schemes, Jan 3, 2022 to May 29, 2026).
- **Key Observation**: Average NAV across categories expanded from ~Rs. 42.50 to ~Rs. 89.40. Shaded annotations highlight the **2023 Bull Run** (March-December 2023) where equity NAVs rallied over +28%, and the **2024 Market Correction** (June-November 2024) which saw temporary drawdowns of 6-8%.

### 2. AUM Growth by AMC (REQ-02)
- **Dataset**: `03_aum_by_fund_house.csv` / `fact_aum` (90 rows, 10 AMCs, 2022-2025).
- **Key Observation**: Industry AUM is highly concentrated. SBI Mutual Fund maintains total market dominance, reaching **Rs. 12.50 Lakh Crore (Rs. 12,50,000 Cr)** in Q1 & Q4 2025, followed by ICICI Prudential (~Rs. 10.74L Cr) and HDFC Mutual Fund (~Rs. 9.30L Cr).

### 3. Monthly SIP Inflow Time Series (REQ-03)
- **Dataset**: `04_monthly_sip_inflows.csv` / `fact_sip_industry` (48 rows, Jan 2022 - Dec 2025).
- **Key Observation**: Monthly SIP inflows increased continuously from Rs. 11,517 Cr in Jan 2022 to an **all-time high of Rs. 31,002 Cr in Dec 2025**, representing a CAGR of ~28% in retail systematic accumulation.

### 4. Category-Wise Inflow Heatmap (REQ-04)
- **Dataset**: `05_category_inflows.csv` (144 rows, FY 2024-25).
- **Key Observation**: Sectoral/Thematic funds (peak Rs. 18,117 Cr in June 2024) and Small Cap funds (average ~Rs. 3,200 Cr/month) registered the highest net inflows, while Large Cap funds experienced moderate, steady inflows.

### 5. Investor Demographics (REQ-05)
- **Dataset**: `08_investor_transactions.csv` / `fact_transactions` (32,778 rows).
- **Key Observation**: 
  - **Age Group**: Investors aged 26-35 represent the single largest demographic cohort (41.1% of transactions), followed by 36-45 (24.9%).
  - **SIP Ticket Size**: Investors in the 46-55 age bracket exhibit the highest median SIP amount (~Rs. 8,500/month).
  - **Gender Split**: Male investors account for 66.5% (21,809) of transactions versus 33.5% (10,969) Female investors.

### 6. Geographic Distribution (REQ-06)
- **Dataset**: `08_investor_transactions.csv`.
- **Key Observation**: 
  - **Top States by SIP Amount**: Madhya Pradesh (Rs. 2.07 Cr), Punjab (Rs. 2.01 Cr), Telangana (Rs. 1.86 Cr), Tamil Nadu (Rs. 1.84 Cr), and Gujarat (Rs. 1.84 Cr).
  - **City Tier Split**: Top 30 (T30) cities drive 66.3% (21,719) of total transactions, while Beyond 30 (B30) cities contribute 33.7% (11,059).

### 7. Industry Folio Count Growth (REQ-07)
- **Dataset**: `06_industry_folio_count.csv` (21 rows, Jan 2022 - Dec 2025).
- **Key Observation**: Total mutual fund folios expanded from **13.26 Crore in Jan 2022 to 26.12 Crore in Dec 2025** (nearly doubling), driven primarily by Equity folios rising from 9.28 Cr to 18.28 Cr.

### 8. Pairwise NAV Return Correlation (REQ-08)
- **Dataset**: `02_nav_history.csv`.
- **Key Observation**: Daily returns across top equity funds (e.g., SBI Bluechip, HDFC Top 100, ICICI Pru Large Cap) demonstrate strong positive pairwise correlations (r = 0.82 to 0.94), reflecting underlying broad market co-movement.

### 9. Top Holdings Sector Allocation (REQ-09)
- **Dataset**: `09_portfolio_holdings.csv` / `fact_portfolio` (322 rows).
- **Key Observation**: Banking & Financial Services represents the largest sector exposure (~28.4%), followed by Information Technology (~19.8%) and Pharmaceuticals (~17.7%).

### 10. Risk-Adjusted Returns & Benchmark Comparison (REQ-10)
- **Dataset**: `07_scheme_performance.csv` / `fact_performance`.
- **Key Observation**: Over 82% of equity schemes outperformed their 3-year benchmark index CAGR, generating positive Alpha (ranging from +1.2% to +5.8%).

---

## 3. Artifact Deliverables Verified
- `notebooks/EDA_Analysis.ipynb`: Fully executable notebook with Plotly and Seaborn code cells and 10 explicit finding markdown cells.
- `notebooks/EDA.ipynb`: Synchronized backward-compatible executable notebook.
- `figures/`: 18 publication-quality PNG figures (300 DPI) matching all handbook specs.
- `reports/phase3_rtm.md`: Requirement Traceability Matrix.
- `reports/phase3_gap_analysis.md`: Gap Analysis documentation.
