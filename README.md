# Mutual Fund Analytics

A production-quality Python project designed to analyze, visualize, and report on mutual fund performance. This repository is structured to support clean, scalable, and robust data engineering and data science pipelines.

## Project Overview

Mutual Fund Analytics provides a structured environment for:
* **Data Ingestion & Processing:** Fetching raw financial data and converting it into structured formats.
* **Database & Storage:** Persisting processed data using relational models.
* **Exploratory Data Analysis (EDA):** Notebooks for ad-hoc queries, trend analysis, and model prototyping.
* **Dashboarding & Reporting:** Building interactive web applications and generating static reports for stakeholders.

---

## Folder Structure

```text
mutual-fund-analytics/
├── data/
│   ├── raw/            # Raw data files (e.g., CSV, JSON, API dumps)
│   └── processed/      # Cleaned and structured data ready for analysis
├── notebooks/          # Jupyter notebooks for prototyping and EDA
├── sql/                # SQL scripts for database schemas and analytical queries
├── dashboard/          # Interactive dashboard code (e.g., Streamlit, Dash)
├── reports/            # Generated PDF/HTML reports and static assets
├── scripts/            # Executable scripts for ETL and automation
├── tests/              # Unit and integration tests
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
├── .gitignore          # Git exclusion rules
└── LICENSE             # Project license
```

---

## Installation

### Prerequisites
* Python 3.12 or higher

### Setup Steps
1. **Clone the repository:**
   ```bash
   git clone https://github.com/ruthvikgoud16/mutual-fund-analytics-Bluestock.git
   cd mutual-fund-analytics-Bluestock
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## Usage

* **Data Engineering (ETL):** Run ingestion and processing scripts from the `scripts/` directory.
* **Exploratory Analysis:** Launch Jupyter to work on notebooks:
  ```bash
  jupyter notebook
  ```
* **Dashboards:** Run dashboard applications from the `dashboard/` directory.
* **Testing:** Run pytest to verify functionality:
  ```bash
  pytest
  ```

---

## Technologies Used

* **Language:** Python 3.12+
* **Data Processing & Analytics:** Pandas, NumPy, SciPy
* **Data Visualization:** Matplotlib, Seaborn, Plotly
* **Database Interaction:** SQLAlchemy
* **APIs & Requests:** Requests
* **Development & Prototyping:** Jupyter Notebook

---

## Future Work

* **ETL Pipelines:** Automate raw mutual fund data fetch via public APIs.
* **Relational Database Schema:** Design optimized SQL schemas for mutual fund performance metrics.
* **Interactive Dashboard:** Build a comprehensive dashboard for key metrics like CAGR, Standard Deviation, Sharpe Ratio, and rolling returns.
* **Unit Testing:** Implement robust coverage for data quality checks and analytics computations.