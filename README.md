# Bluestock Mutual Fund Analytics Platform

![Bluestock Fintech](https://img.shields.io/badge/Bluestock-Fintech%20Capstone-0066FF?style=for-the-badge)
![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue?style=for-the-badge&logo=python)
![SQLite](https://img.shields.io/badge/SQLite-Star%20Schema-003B57?style=for-the-badge&logo=sqlite)
![Streamlit](https://img.shields.io/badge/Streamlit-BI%20Dashboard-FF4B4B?style=for-the-badge&logo=streamlit)

Production-grade, full-stack **Mutual Fund Analytics Platform** built for **Bluestock Fintech**. The system ingests AMFI India market data, standardizes transaction logs, builds a normalized 5-table SQLite star schema, calculates 21 quantitative risk and return metrics, renders an interactive BI dashboard, and produces automated PDF reports and executive presentation decks.

---

## 🏛️ Project Architecture & Pipeline

The system strictly follows modern Data Engineering architecture: `Extract → Transform → Load → Analyze → Visualize`.

```text
mutual-fund-analytics-Bluestock/
├── data/
│   ├── raw/                # 10 Provided CSV Datasets + Live NAV API Dumps
│   └── processed/          # Cleaned, standardized CSV flat-files
├── dashboard/              # Streamlit Multipage BI Application
│   ├── app.py              # Main dashboard entrypoint & theme setup
│   └── pages/              # 4 Pages: Industry, Performance, Investor, Trends
├── docs/                   # PDF Handbook, Specs & PowerPoint Presentation Deck
├── figures/                # 40+ PNG Visualizations (EDA, Risk Metrics, Dashboard)
├── notebooks/              # Executed Jupyter Notebooks (EDA, Risk, Advanced Analytics)
├── reports/                # PDF Reports (Data Quality, EDA, Final Report, Dashboard.pdf)
├── scripts/                # Modular Python Engineering Libraries
│   ├── config.py           # Environment paths & database settings
│   ├── utils.py            # Structured logging & filesystem utilities
│   ├── validation.py       # Data quality & referential integrity checks
│   ├── data_ingestion.py   # Raw CSV discovery & profiling engine
│   ├── live_nav_fetch.py   # REST API client for mfapi.in live NAV values
│   ├── cleaning.py         # Null handling, date parsing & ffill gap filling
│   ├── database.py         # SQLAlchemy Star Schema ORM Models
│   ├── load_sql.py         # Data cleaning & SQLite database loader engine
│   ├── generate_eda.py     # 18-figure EDA visualization generator
│   ├── risk_metrics.py     # 21 Risk/Return metrics library & DB persistence
│   ├── generate_risk_charts.py # 15 Risk visualization charts generator
│   ├── cohort_analysis.py  # Investor cohort, SIP continuity & VaR/CVaR engine
│   ├── recommender.py      # Multi-factor fund recommendation engine
│   ├── export_dashboard_pdf.py # Static Dashboard PDF & screenshot builder
│   ├── generate_final_pdf.py   # ReportLab 15-20 page Final Report builder
│   └── generate_presentation.py # 12-slide PowerPoint presentation generator
├── sql/                    # SQL DDL schemas, constraints, indexes & analytical queries
├── tests/                  # Unit test suite (14 tests covering math & analytics)
├── run_pipeline.py         # Master 1-Command Pipeline Orchestrator
├── requirements.txt        # Production dependencies
└── README.md               # Production documentation
```

---

## ⚡ Quick Start: Master 1-Command Execution

To run the entire end-to-end pipeline (Ingestion → Cleaning → DB Load → EDA → Risk Metrics → Cohorts → PDF Reports → Presentation Deck):

```bash
# 1. Clone repository
git clone https://github.com/ruthvikgoud16/mutual-fund-analytics-Bluestock.git
cd mutual-fund-analytics-Bluestock

# 2. Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Execute Master Pipeline
python3 run_pipeline.py
```

### Launch Interactive BI Dashboard
To run the interactive Streamlit Web Application:
```bash
streamlit run dashboard/app.py
```

### Run Unit Test Suite
```bash
python3 -m unittest discover tests
```

---

## 📊 Database Schema (Star Schema)

The SQLite database (`mutual_fund_analytics.db`) implements a 5-table star schema indexed for high-performance querying:

1. **`dim_fund`**: Scheme master list (AMFI code, AMC, category, sub-category, plan, launch date, expense ratio, SEBI risk grade).
2. **`dim_date`**: Date dimension table (date_id, year, month, quarter, weekday indicator).
3. **`fact_nav`**: Daily NAV valuations and percentage returns across 40 schemes (64,000+ records).
4. **`fact_transactions`**: Investor transaction logs (32,000+ rows: SIP, Lumpsum, Redemption, State, Age, City Tier).
5. **`fact_performance` / `fact_risk_metrics`**: Scheme performance summary, Sharpe/Sortino ratios, Alpha, Beta, VaR, HHI.

---

## 📈 Key Analytics & Risk Metrics Implemented

- **Return Metrics**: Daily Return, Weekly Return, Monthly Return, Annual Return, CAGR (exact 365.25 day scaling), 1-Yr Rolling Returns.
- **Risk Metrics**: Annualized Volatility, Standard Deviation, Downside Deviation, Max Drawdown, Drawdown Duration, Historical 95% Value at Risk (VaR), Conditional VaR (CVaR / Expected Shortfall).
- **Benchmark Sensitivity**: Jensen's Alpha ($\alpha$), Market Beta ($\beta$), Tracking Error, Information Ratio.
- **Risk-Adjusted Ratios**: Sharpe Ratio ($R_f = 6.0\%$), Sortino Ratio, Treynor Ratio, Calmar Ratio.
- **Portfolio Concentration**: Sector Herfindahl-Hirschman Index (HHI), Diversification Score (0..100).
- **Investor Analytics**: Cohort retention by initial transaction year, SIP continuation analysis flagging at-risk accounts (>35 days gap).
- **Recommendation Engine**: Multi-factor Sharpe-based scheme selection filtered by investor risk appetite (`Low`, `Moderate`, `High`).

---

## 📄 Key Deliverables Produced

- `reports/Final_Report.pdf`: 15-20 page comprehensive PDF report generated via ReportLab.
- `reports/Dashboard.pdf`: 4-page static BI dashboard report export.
- `docs/Bluestock_MF_Presentation.pptx`: 12-slide executive presentation deck.
- `notebooks/`: 3 executed Jupyter notebooks (`EDA.ipynb`, `Risk_Analytics.ipynb`, `05_advanced_analytics.ipynb`).
- `figures/`: 40+ high-resolution PNG charts covering EDA, risk metrics, and dashboard screens.

---

## 📜 License & Acknowledgments

Sourced from AMFI India, NSE, BSE, and open APIs (`mfapi.in`). Developed for educational and analytics engineering demonstration purposes as part of the **Bluestock Fintech Capstone Project**.