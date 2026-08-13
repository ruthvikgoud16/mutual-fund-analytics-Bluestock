"""Main script to clean, validate, and load mutual fund datasets into SQLite.

This module orchestrates raw data loading, cleaning transformations, database
schema creation, relational population, DDL file export, and generates a
data cleaning validation report.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

# Ensure scripts folder is on PATH
sys.path.append(str(Path(__file__).resolve().parent))

from cleaning import clean_dataframe, clean_nav_history_gaps, parse_and_validate_dates
from config import (
    DATABASE_PATH,
    DATABASE_URL,
    PROCESSED_DATA_DIR,
    PROJECT_ROOT,
    RAW_DATA_DIR,
    REPORTS_DIR,
)
from database import (
    Base,
    DimDate,
    DimFund,
    FactAum,
    FactNav,
    FactPerformance,
    FactPortfolio,
    FactSipIndustry,
    FactTransactions,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils import ensure_directory, setup_logging

logger = setup_logging("load_sql")
SQL_DIR = PROJECT_ROOT / "sql"


def export_sql_ddl_files(sql_dir: Path) -> None:
    """Create and write static SQL DDL files representing the database design.

    Args:
        sql_dir: Path to write SQL scripts.
    """
    ensure_directory(sql_dir)

    # 1. create_tables.sql
    create_tables_sql = """-- SQL DDL script to create Star Schema Tables
-- Target Engine: SQLite/PostgreSQL compliant

CREATE TABLE dim_fund (
    amfi_code INTEGER PRIMARY KEY,
    fund_house TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
    category TEXT NOT NULL,
    sub_category TEXT NOT NULL,
    plan TEXT NOT NULL,
    launch_date DATE,
    benchmark TEXT,
    expense_ratio_pct REAL,
    exit_load_pct REAL,
    min_sip_amount REAL,
    min_lumpsum_amount REAL,
    fund_manager TEXT,
    risk_category TEXT,
    sebi_category_code TEXT
);

CREATE TABLE dim_date (
    date_id DATE PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    is_weekday BOOLEAN NOT NULL
);

CREATE TABLE fact_nav (
    amfi_code INTEGER NOT NULL,
    date_id DATE NOT NULL,
    nav REAL NOT NULL,
    daily_return_pct REAL,
    PRIMARY KEY (amfi_code, date_id),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id)
);

CREATE TABLE fact_transactions (
    tx_id TEXT PRIMARY KEY,
    investor_id TEXT NOT NULL,
    amfi_code INTEGER NOT NULL,
    transaction_date DATE NOT NULL,
    transaction_type TEXT NOT NULL,
    amount_inr INTEGER NOT NULL,
    state TEXT,
    city TEXT,
    city_tier TEXT,
    age_group TEXT,
    gender TEXT,
    annual_income_lakh REAL,
    payment_mode TEXT,
    kyc_status TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (transaction_date) REFERENCES dim_date(date_id)
);

CREATE TABLE fact_performance (
    amfi_code INTEGER PRIMARY KEY,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    benchmark_3yr_pct REAL,
    alpha REAL,
    beta REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    std_dev_ann_pct REAL,
    max_drawdown_pct REAL,
    morningstar_rating INTEGER,
    risk_grade TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE fact_portfolio (
    amfi_code INTEGER NOT NULL,
    stock_symbol TEXT NOT NULL,
    stock_name TEXT NOT NULL,
    sector TEXT NOT NULL,
    weight_pct REAL NOT NULL,
    market_value_cr REAL,
    current_price_inr REAL,
    portfolio_date DATE NOT NULL,
    PRIMARY KEY (amfi_code, stock_symbol, portfolio_date),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (portfolio_date) REFERENCES dim_date(date_id)
);

CREATE TABLE fact_aum (
    fund_house TEXT NOT NULL,
    date_id DATE NOT NULL,
    aum_lakh_crore REAL,
    aum_crore REAL,
    num_schemes INTEGER,
    PRIMARY KEY (fund_house, date_id),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id)
);

CREATE TABLE fact_sip_industry (
    month TEXT PRIMARY KEY,
    sip_inflow_crore REAL,
    active_sip_accounts_crore REAL,
    new_sip_accounts_lakh REAL,
    sip_aum_lakh_crore REAL,
    yoy_growth_pct REAL
);
"""

    # 2. constraints.sql
    constraints_sql = """-- SQL constraints definitions
-- Detail reference mapping for table constraints and business rules

-- fact_transactions transaction_type constraint
-- CHECK (transaction_type IN ('Sip', 'Lumpsum', 'Redemption'))

-- fact_transactions kyc_status constraint
-- CHECK (kyc_status IN ('Verified', 'Pending'))

-- fact_performance rating range constraint
-- CHECK (morningstar_rating >= 1 AND morningstar_rating <= 5)
"""

    # 3. indexes.sql
    indexes_sql = """-- Performance optimization indexes

-- Index for fast NAV history range queries
CREATE INDEX idx_fact_nav_composite ON fact_nav (amfi_code, date_id);

-- Index for investor transactions aggregation
CREATE INDEX idx_fact_transactions_amfi ON fact_transactions (amfi_code);
CREATE INDEX idx_fact_transactions_date ON fact_transactions (transaction_date);

-- Index for portfolio snapshot calculations
CREATE INDEX idx_fact_portfolio_composite ON fact_portfolio (amfi_code, portfolio_date);
"""

    with open(sql_dir / "create_tables.sql", "w") as f:
        f.write(create_tables_sql)
    with open(sql_dir / "constraints.sql", "w") as f:
        f.write(constraints_sql)
    with open(sql_dir / "indexes.sql", "w") as f:
        f.write(indexes_sql)

    logger.info("Exported SQL DDL scripts successfully.")


def build_calendar_dimension(unique_dates: set[str]) -> list[dict[str, Any]]:
    """Generate calendar dimension rows from unique string dates.

    Args:
        unique_dates: Set of date strings (YYYY-MM-DD).

    Returns:
        List[Dict[str, Any]]: Calendar dimension records.
    """
    records = []
    for dt_str in sorted(unique_dates):
        if pd.isna(dt_str) or not dt_str:
            continue
        try:
            dt = datetime.strptime(dt_str, "%Y-%m-%d").date()  # noqa: DTZ007
            records.append(
                {
                    "date_id": dt,
                    "year": dt.year,
                    "month": dt.month,
                    "quarter": (dt.month - 1) // 3 + 1,
                    "is_weekday": dt.weekday() < 5,
                }
            )
        except (ValueError, TypeError) as e:
            logger.warning(f"Error parsing date string '{dt_str}': {e}")
    return records


def main() -> None:
    """Main pipeline execution for cleaning, schema validation, and SQL database loading."""
    logger.info("Initializing database pipeline engine...")
    ensure_directory(PROCESSED_DATA_DIR)

    # 1. SQLAlchemy database setup
    # If DB exists, delete it first to ensure a clean load
    if DATABASE_PATH.exists():
        try:
            DATABASE_PATH.unlink()
            logger.info("Deleted existing SQLite database for fresh reload.")
        except OSError as e:
            logger.warning(f"Could not delete existing DB: {e}")

    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    logger.info("Database connection and tables created.")

    # 2. File list mapping
    raw_files = sorted(RAW_DATA_DIR.glob("*.csv"))
    cleaning_stats = []
    unique_dates = set()

    # Pre-load fund master to check categories
    fund_master_path = RAW_DATA_DIR / "01_fund_master.csv"
    fund_master_raw = pd.read_csv(fund_master_path)
    fund_master_clean = clean_dataframe(fund_master_raw, "01_fund_master.csv")
    fund_master_clean = parse_and_validate_dates(fund_master_clean, ["launch_date"])
    fund_master_clean.to_csv(PROCESSED_DATA_DIR / "01_fund_master.csv", index=False)

    # Write to dim_fund
    for _, row in fund_master_clean.iterrows():
        fund_record = DimFund(
            amfi_code=int(row["amfi_code"]),
            fund_house=row["fund_house"],
            scheme_name=row["scheme_name"],
            category=row["category"],
            sub_category=row["sub_category"],
            plan=row["plan"],
            launch_date=(
                pd.to_datetime(row["launch_date"]).date()
                if not pd.isna(row["launch_date"])
                else None
            ),
            benchmark=row["benchmark"],
            expense_ratio_pct=(
                float(row["expense_ratio_pct"])
                if not pd.isna(row["expense_ratio_pct"])
                else None
            ),
            exit_load_pct=(
                float(row["exit_load_pct"])
                if not pd.isna(row["exit_load_pct"])
                else None
            ),
            min_sip_amount=(
                float(row["min_sip_amount"])
                if not pd.isna(row["min_sip_amount"])
                else None
            ),
            min_lumpsum_amount=(
                float(row["min_lumpsum_amount"])
                if not pd.isna(row["min_lumpsum_amount"])
                else None
            ),
            fund_manager=row["fund_manager"],
            risk_category=row["risk_category"],
            sebi_category_code=row["sebi_category_code"],
        )
        session.add(fund_record)

    cleaning_stats.append(
        {
            "dataset": "01_fund_master.csv",
            "raw_rows": len(fund_master_raw),
            "clean_rows": len(fund_master_clean),
            "status": "Loaded",
        }
    )

    # Loop over other files
    for filepath in raw_files:
        if filepath.name == "01_fund_master.csv":
            continue

        prefix = filepath.name.split(".")[0]
        raw_df = pd.read_csv(filepath)
        cleaned_df = clean_dataframe(raw_df, filepath.name)

        # Parse dates based on dataset fields
        date_cols = [c for c in cleaned_df.columns if "date" in c or c == "month"]
        cleaned_df = parse_and_validate_dates(cleaned_df, date_cols)

        # Specific cleaning transformations
        if prefix == "02_nav_history":
            cleaned_df = clean_nav_history_gaps(cleaned_df)

        # Collect unique dates for calendar dimension
        for col in date_cols:
            if col != "month":  # exclude monthly string formats like YYYY-MM
                unique_dates.update(cleaned_df[col].dropna().unique())

        # Save processed CSV
        processed_path = PROCESSED_DATA_DIR / filepath.name
        cleaned_df.to_csv(processed_path, index=False)
        logger.info(f"Saved processed CSV: {processed_path}")

        cleaning_stats.append(
            {
                "dataset": filepath.name,
                "raw_rows": len(raw_df),
                "clean_rows": len(cleaned_df),
                "status": "Processed",
            }
        )

        # Load dataset into database using models
        if prefix == "02_nav_history":
            for _, row in cleaned_df.iterrows():
                rec = FactNav(
                    amfi_code=int(row["amfi_code"]),
                    date_id=pd.to_datetime(row["date"]).date(),
                    nav=float(row["nav"]),
                    daily_return_pct=None,  # will be computed in Day 4
                )
                session.add(rec)
        elif prefix == "03_aum_by_fund_house":
            for _, row in cleaned_df.iterrows():
                rec = FactAum(
                    fund_house=row["fund_house"],
                    date_id=pd.to_datetime(row["date"]).date(),
                    aum_lakh_crore=(
                        float(row["aum_lakh_crore"])
                        if not pd.isna(row["aum_lakh_crore"])
                        else None
                    ),
                    aum_crore=(
                        float(row["aum_crore"])
                        if not pd.isna(row["aum_crore"])
                        else None
                    ),
                    num_schemes=(
                        int(row["num_schemes"])
                        if not pd.isna(row["num_schemes"])
                        else None
                    ),
                )
                session.add(rec)
        elif prefix == "04_monthly_sip_inflows":
            for _, row in cleaned_df.iterrows():
                rec = FactSipIndustry(
                    month=row["month"],
                    sip_inflow_crore=(
                        float(row["sip_inflow_crore"])
                        if not pd.isna(row["sip_inflow_crore"])
                        else None
                    ),
                    active_sip_accounts_crore=(
                        float(row["active_sip_accounts_crore"])
                        if not pd.isna(row["active_sip_accounts_crore"])
                        else None
                    ),
                    new_sip_accounts_lakh=(
                        float(row["new_sip_accounts_lakh"])
                        if not pd.isna(row["new_sip_accounts_lakh"])
                        else None
                    ),
                    sip_aum_lakh_crore=(
                        float(row["sip_aum_lakh_crore"])
                        if not pd.isna(row["sip_aum_lakh_crore"])
                        else None
                    ),
                    yoy_growth_pct=(
                        float(row["yoy_growth_pct"])
                        if not pd.isna(row["yoy_growth_pct"])
                        else None
                    ),
                )
                session.add(rec)
        elif prefix == "07_scheme_performance":
            for _, row in cleaned_df.iterrows():
                rec = FactPerformance(
                    amfi_code=int(row["amfi_code"]),
                    return_1yr_pct=(
                        float(row["return_1yr_pct"])
                        if not pd.isna(row["return_1yr_pct"])
                        else None
                    ),
                    return_3yr_pct=(
                        float(row["return_3yr_pct"])
                        if not pd.isna(row["return_3yr_pct"])
                        else None
                    ),
                    return_5yr_pct=(
                        float(row["return_5yr_pct"])
                        if not pd.isna(row["return_5yr_pct"])
                        else None
                    ),
                    benchmark_3yr_pct=(
                        float(row["benchmark_3yr_pct"])
                        if not pd.isna(row["benchmark_3yr_pct"])
                        else None
                    ),
                    alpha=float(row["alpha"]) if not pd.isna(row["alpha"]) else None,
                    beta=float(row["beta"]) if not pd.isna(row["beta"]) else None,
                    sharpe_ratio=(
                        float(row["sharpe_ratio"])
                        if not pd.isna(row["sharpe_ratio"])
                        else None
                    ),
                    sortino_ratio=(
                        float(row["sortino_ratio"])
                        if not pd.isna(row["sortino_ratio"])
                        else None
                    ),
                    std_dev_ann_pct=(
                        float(row["std_dev_ann_pct"])
                        if not pd.isna(row["std_dev_ann_pct"])
                        else None
                    ),
                    max_drawdown_pct=(
                        float(row["max_drawdown_pct"])
                        if not pd.isna(row["max_drawdown_pct"])
                        else None
                    ),
                    morningstar_rating=(
                        int(row["morningstar_rating"])
                        if not pd.isna(row["morningstar_rating"])
                        else None
                    ),
                    risk_grade=row["risk_grade"],
                )
                session.add(rec)
        elif prefix == "08_investor_transactions":
            for idx, row in cleaned_df.iterrows():
                rec = FactTransactions(
                    tx_id=f"TX{idx:06d}",
                    investor_id=row["investor_id"],
                    amfi_code=int(row["amfi_code"]),
                    transaction_date=pd.to_datetime(row["transaction_date"]).date(),
                    transaction_type=row["transaction_type"],
                    amount_inr=int(row["amount_inr"]),
                    state=row["state"],
                    city=row["city"],
                    city_tier=row["city_tier"],
                    age_group=row["age_group"],
                    gender=row["gender"],
                    annual_income_lakh=(
                        float(row["annual_income_lakh"])
                        if not pd.isna(row["annual_income_lakh"])
                        else None
                    ),
                    payment_mode=row["payment_mode"],
                    kyc_status=row["kyc_status"],
                )
                session.add(rec)
        elif prefix == "09_portfolio_holdings":
            for _, row in cleaned_df.iterrows():
                rec = FactPortfolio(
                    amfi_code=int(row["amfi_code"]),
                    stock_symbol=row["stock_symbol"],
                    stock_name=row["stock_name"],
                    sector=row["sector"],
                    weight_pct=float(row["weight_pct"]),
                    market_value_cr=(
                        float(row["market_value_cr"])
                        if not pd.isna(row["market_value_cr"])
                        else None
                    ),
                    current_price_inr=(
                        float(row["current_price_inr"])
                        if not pd.isna(row["current_price_inr"])
                        else None
                    ),
                    portfolio_date=pd.to_datetime(row["portfolio_date"]).date(),
                )
                session.add(rec)

    # 3. Load Calendar Dimension
    calendar_records = build_calendar_dimension(unique_dates)
    for cal in calendar_records:
        rec = DimDate(
            date_id=cal["date_id"],
            year=cal["year"],
            month=cal["month"],
            quarter=cal["quarter"],
            is_weekday=cal["is_weekday"],
        )
        session.add(rec)
    logger.info(f"Populated dim_date with {len(calendar_records)} records.")

    # 4. Commit session
    session.commit()
    session.close()
    logger.info("Successfully committed all records to database.")

    # 5. Export SQL DDL Scripts
    export_sql_ddl_files(SQL_DIR)

    # 6. Generate reports/cleaning_report.md
    ensure_directory(REPORTS_DIR)
    report_path = REPORTS_DIR / "cleaning_report.md"

    report_lines = []
    report_lines.append("# Mutual Fund Analytics - Data Cleaning & DB Load Report\n")
    report_lines.append(
        "This report outlines the results of the cleaning operations, row count profile transformations, and database loading statistics for Day 2.\n"
    )

    report_lines.append("## 1. Cleaning & Row Counts Summary\n")
    report_lines.append(
        "| Dataset File | Raw Rows | Processed Rows | Difference | Status |"
    )
    report_lines.append("| :--- | :--- | :--- | :--- | :--- |")
    for stat in cleaning_stats:
        diff = stat["clean_rows"] - stat["raw_rows"]
        diff_str = f"+{diff}" if diff > 0 else str(diff)
        report_lines.append(
            f"| {stat['dataset']} | {stat['raw_rows']} | {stat['clean_rows']} | {diff_str} | {stat['status']} |"
        )
    report_lines.append(
        "\n> [!NOTE]\n> `02_nav_history.csv` row count increased because it was reindexed to cover all trading/calendar days and forward-filled to eliminate weekend/holiday gaps.\n"
    )

    report_lines.append("## 2. Database Load Statistics\n")
    report_lines.append("- **SQL Engine:** SQLite")
    report_lines.append(f"- **File Location:** `{DATABASE_PATH}`")
    report_lines.append(
        f"- **Date Calendar Range size:** {len(calendar_records)} unique dates loaded."
    )

    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))

    logger.info(f"Data Cleaning Report written to {report_path}")
    logger.info("Day 2 Database Load Complete.")


if __name__ == "__main__":
    main()
