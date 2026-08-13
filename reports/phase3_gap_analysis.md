# Phase 3 Gap Analysis Report

## Executive Summary
A comprehensive audit of the Bluestock Mutual Fund Analytics Platform repository against the official Capstone Handbook (`docs/Bluestock_MF_Capstone_Project.pdf`) and prompt specifications revealed several critical and major gaps in the Phase 3 (Exploratory Data Analysis) implementation. While Phase 1 (ETL) and Phase 2 (Database & Cleaning) are fully intact, Phase 3 deliverables (`scripts/generate_eda.py` and `notebooks/EDA.ipynb`) were relying on static PNG loading, mismatched chart types, missing metrics, and missing requirements.

---

## Issue Classification

### Critical Gaps
1. **Missing Notebook Deliverable Name & Code Execution**:
   - *Requirement*: The official deliverable is `notebooks/EDA_Analysis.ipynb` (Capstone PDF p.12).
   - *Current State*: Repo contains `notebooks/EDA.ipynb` which merely displays static pre-rendered PNG files via `IPython.display.Image` rather than executing actual Pandas/Seaborn/Plotly analytical code.
   - *Fix Needed*: Create `notebooks/EDA_Analysis.ipynb` with full executable Python/Seaborn/Plotly code cells that load from `mutual_fund_analytics.db` / `data/processed/`, render plots live, save high-res PNGs to `figures/`, and include 10 structured markdown findings cells. Also maintain `notebooks/EDA.ipynb` for backward compatibility.

2. **Completely Omitted Category-Wise Inflow Heatmap (REQ-04)**:
   - *Requirement*: Heatmap with Months on X-axis, Fund Categories on Y-axis, and Net Inflow as color intensity using Seaborn (Dataset: `05_category_inflows.csv`).
   - *Current State*: Totally missing from `generate_eda.py`, `EDA.ipynb`, and `figures/`.
   - *Fix Needed*: Implement Seaborn heatmap aggregating net inflows by month and category, save to `figures/04_category_inflow_heatmap.png`.

3. **Missing Investor Demographic Visualizations (REQ-05)**:
   - *Requirement*: Age-group distribution pie chart, SIP amount box plot by age group, and Gender split visualization (Dataset: `08_investor_transactions.csv`).
   - *Current State*: `generate_eda.py` only had transaction type pie chart and a total transaction box plot. Age group distribution pie chart, age-wise SIP box plot, and gender split chart were missing.
   - *Fix Needed*: Implement Age group pie chart, Age group vs SIP amount boxplot, and Gender split bar/pie chart.

---

### Major Gaps
4. **NAV Trend Analysis & Plotly Interactive Chart (REQ-01)**:
   - *Requirement*: Plot daily NAV for all 40 schemes (2022–2026), highlight 2023 bull run and 2024 market corrections, using Plotly.
   - *Current State*: `generate_eda.py` plotted a single static average NAV line with Matplotlib without Plotly, multi-scheme clarity, or highlighting periods.
   - *Fix Needed*: Implement Plotly interactive line chart for scheme/category NAV trends with explicit shapes/annotations highlighting the 2023 Bull Run and 2024 Market Corrections, plus export static PNG.

5. **AUM Growth Grouped Bar Chart by Year (REQ-02)**:
   - *Requirement*: Grouped bar chart of AUM by Fund House across years 2022–2025 using Seaborn, highlighting SBI dominance at ~₹12.5L Cr in 2025.
   - *Current State*: `generate_eda.py` plotted a single snapshot bar chart for the latest date.
   - *Fix Needed*: Pivot `03_aum_by_fund_house.csv` / `fact_aum` by year and fund house, create Seaborn grouped bar chart (2022-2025), and annotate SBI's ₹12.5L Cr dominance.

6. **SIP Inflow Time Series Plotly Chart & Annotation (REQ-03)**:
   - *Requirement*: Monthly SIP inflows (Jan 2022 -> Dec 2025) using Plotly, with explicit annotation for the ₹31,002 Cr all-time high in Dec 2025.
   - *Current State*: Static Matplotlib plot without Plotly or ₹31,002 Cr milestone annotation.
   - *Fix Needed*: Create Plotly line chart with explicit annotation arrow/marker for ₹31,002 Cr in Dec 2025.

7. **Geographic Distribution Metrics & City Tier Pie Chart (REQ-06)**:
   - *Requirement*: Horizontal bar chart of SIP amount by state & T30 vs B30 city-tier pie chart.
   - *Current State*: `generate_eda.py` used total transaction amount instead of filtering specifically for SIP amount, and T30 vs B30 pie chart was missing.
   - *Fix Needed*: Filter transactions for SIP, plot top states by SIP amount, and generate T30 vs B30 city-tier pie chart.

8. **Folio Count Growth Plotly Line Chart (REQ-07)**:
   - *Requirement*: Line chart for total industry folios (Jan 2022 -> Dec 2025) from ~13.26 Cr to ~26.12 Cr using Plotly with key milestones.
   - *Current State*: `generate_eda.py` plotted active SIP accounts from a different file instead of industry folio counts (`06_industry_folio_count.csv`).
   - *Fix Needed*: Implement Plotly line chart for total folios (13.26 Cr -> 26.12 Cr) with key growth milestones annotated.

9. **Pairwise NAV Return Correlation Heatmap across 10 Selected Funds (REQ-08)**:
   - *Requirement*: Daily returns computed across 10 selected funds, pairwise correlation matrix, Seaborn heatmap.
   - *Current State*: `generate_eda.py` correlated 9 static performance metrics (Sharpe, Sortino, Alpha, etc.), NOT daily NAV return time series across 10 funds.
   - *Fix Needed*: Compute daily percentage returns from `02_nav_history.csv` for 10 representative schemes, compute correlation matrix, and plot Seaborn heatmap.

10. **Structured 10 Key EDA Findings Cells (REQ-10)**:
    - *Requirement*: Notebook must contain 10 explicit Markdown finding cells, each containing: (1) One concise insight sentence, (2) Supporting chart reference, (3) Interpretation grounded in actual data.
    - *Current State*: Notebook contained generic bullet points in a single summary section.
    - *Fix Needed*: Restructure notebook with 10 explicit finding cells adhering strictly to the 3-part format.

---

### Minor Gaps
11. **Chart Naming & Organization**:
    - Ensure all generated PNG files under `figures/` match standardized, clear names corresponding to the 10 requirements and additional analytical charts (at least 15+ publication-quality charts).

---

### No Action Items
- **Phase 1 ETL (`scripts/data_ingestion.py`, `scripts/cleaning.py`)**: Operating correctly, datasets parsed cleanly into `data/processed/`.
- **Phase 2 Star Schema Database (`bluestock_mf.db`, `mutual_fund_analytics.db`)**: Schema design (`dim_fund`, `dim_date`, `fact_nav`, `fact_aum`, `fact_sip_industry`, `fact_performance`, `fact_transactions`, `fact_portfolio`) is accurate and populated.
- **Phase 4 & Phase 6 Risk Metrics and Advanced Analytics**: Intact and covered by tests.
