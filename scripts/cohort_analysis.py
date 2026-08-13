"""Cohort Analysis and Advanced Risk Engine.

Implements all Day 6 tasks from Bluestock Capstone Handbook:
- Task 1: 95% Historical VaR & CVaR across all 40 schemes.
- Task 2: 90-Day Rolling Sharpe ratio time series for 5 representative funds.
- Task 3: Investor cohort analysis grouped by first transaction year.
- Task 4: SIP continuation gap analysis flagging investors with >35 day gaps as at-risk.
- Task 6: Sector concentration analysis (Herfindahl-Hirschman Index - HHI).
"""

import sqlite3
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sys.path.append(str(Path(__file__).resolve().parent))

from config import DATABASE_PATH, PROJECT_ROOT
from risk_metrics import (
    calculate_daily_returns,
    calculate_diversification_score,
    calculate_hhi,
    calculate_var_cvar,
)
from utils import ensure_directory, setup_logging

logger = setup_logging("cohort_analysis")
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = PROJECT_ROOT / "figures"
RISK_FIGURES_DIR = PROJECT_ROOT / "figures" / "risk_metrics"

ensure_directory(REPORTS_DIR)
ensure_directory(FIGURES_DIR)
ensure_directory(RISK_FIGURES_DIR)


def run_var_cvar_analysis(conn: sqlite3.Connection) -> pd.DataFrame:
    """Task 1: Compute 95% Historical VaR and CVaR for all 40 schemes."""
    logger.info("Executing Task 1: 95% Historical VaR & CVaR Analysis...")
    query_schemes = "SELECT amfi_code, scheme_name, category FROM dim_fund"
    df_schemes = pd.read_sql_query(query_schemes, conn)

    records = []
    for _, row in df_schemes.iterrows():
        code = int(row["amfi_code"])
        df_nav = pd.read_sql_query(
            f"SELECT nav FROM fact_nav WHERE amfi_code = {code} ORDER BY date_id ASC",
            conn,
        )
        if len(df_nav) > 30:
            daily_ret = calculate_daily_returns(df_nav["nav"])
            var_95, cvar_95 = calculate_var_cvar(daily_ret, confidence_level=0.95)
            records.append(
                {
                    "amfi_code": code,
                    "scheme_name": row["scheme_name"],
                    "category": row["category"],
                    "var_95_pct": round(var_95, 4),
                    "cvar_95_pct": round(cvar_95, 4),
                }
            )

    df_var = pd.DataFrame(records)
    df_var.to_csv(REPORTS_DIR / "var_cvar_report.csv", index=False)
    logger.info(f"VaR/CVaR Report written to {REPORTS_DIR / 'var_cvar_report.csv'}")
    return df_var


def run_rolling_sharpe_analysis(
    conn: sqlite3.Connection, window_days: int = 90, rf_rate: float = 0.065
) -> str:
    """Task 2: Generate 90-day rolling Sharpe ratio time series for 5 key funds."""
    logger.info("Executing Task 2: 90-Day Rolling Sharpe Analysis for 5 key funds...")
    # 5 Key Representative Funds
    key_codes = [119551, 125497, 120503, 100033, 118632]

    plt.figure(figsize=(12, 6))
    daily_rf = ((1.0 + rf_rate) ** (1.0 / 252)) - 1.0

    for code in key_codes:
        query = f"SELECT date_id as date, nav FROM fact_nav WHERE amfi_code = {code} ORDER BY date_id ASC"
        df_nav = pd.read_sql_query(query, conn)
        query_name = f"SELECT scheme_name FROM dim_fund WHERE amfi_code = {code}"
        res = conn.execute(query_name).fetchone()
        scheme_name = res[0][:25] if res else str(code)

        if len(df_nav) > window_days:
            df_nav["date"] = pd.to_datetime(df_nav["date"])
            df_nav["daily_ret"] = df_nav["nav"].pct_change()

            # Rolling 90-day Sharpe formula: mean(excess) / std * sqrt(252)
            excess = df_nav["daily_ret"] - daily_rf
            roll_mean = excess.rolling(window_days).mean()
            roll_std = df_nav["daily_ret"].rolling(window_days).std()
            roll_sharpe = (roll_mean / roll_std) * np.sqrt(252)

            plt.plot(df_nav["date"], roll_sharpe, label=scheme_name, linewidth=2.0)

    plt.axhline(0, color="black", linestyle="--", alpha=0.5)
    plt.title(
        f"Rolling {window_days}-Day Sharpe Ratio Time Series (Rf = {rf_rate*100:.1f}%)",
        fontsize=14,
        fontweight="bold",
    )
    plt.xlabel("Date")
    plt.ylabel("Rolling Sharpe Ratio")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

    path1 = RISK_FIGURES_DIR / "rolling_sharpe_chart.png"
    path2 = FIGURES_DIR / "rolling_sharpe_chart.png"
    path3 = RISK_FIGURES_DIR / "02_rolling_sharpe.png"

    plt.savefig(path1, bbox_inches="tight", dpi=300)
    plt.savefig(path2, bbox_inches="tight", dpi=300)
    plt.savefig(path3, bbox_inches="tight", dpi=300)
    plt.close()

    logger.info(f"Rolling Sharpe chart saved to {path1}")
    return str(path1)


def run_cohort_analysis(conn: sqlite3.Connection) -> pd.DataFrame:
    """Task 3: Group investors by first transaction year and compute stats."""
    logger.info("Executing Task 3: Investor Cohort Analysis...")
    query = """
        SELECT investor_id, transaction_date, amfi_code, transaction_type, amount_inr, state, age_group
        FROM fact_transactions
    """
    df_tx = pd.read_sql_query(query, conn)
    df_tx["transaction_date"] = pd.to_datetime(df_tx["transaction_date"])

    # Determine first transaction year per investor
    first_tx = df_tx.groupby("investor_id")["transaction_date"].min().reset_index()
    first_tx["cohort_year"] = first_tx["transaction_date"].dt.year
    first_tx_map = dict(zip(first_tx["investor_id"], first_tx["cohort_year"]))

    df_tx["cohort_year"] = df_tx["investor_id"].map(first_tx_map)

    cohort_stats = []
    for cohort, group in df_tx.groupby("cohort_year"):
        sip_group = group[group["transaction_type"].str.upper() == "SIP"]
        top_scheme_code = (
            group["amfi_code"].value_counts().index[0] if not group.empty else None
        )

        # Fetch scheme name
        scheme_name = "N/A"
        if top_scheme_code:
            cur = conn.cursor()
            cur.execute(
                "SELECT scheme_name FROM dim_fund WHERE amfi_code = ?",
                (int(top_scheme_code),),
            )
            res = cur.fetchone()
            if res:
                scheme_name = res[0]

        stats = {
            "cohort_year": int(cohort),
            "total_investors": int(group["investor_id"].nunique()),
            "total_transactions": len(group),
            "total_invested_inr": float(group["amount_inr"].sum()),
            "avg_sip_amount_inr": (
                round(float(sip_group["amount_inr"].mean()), 2)
                if not sip_group.empty
                else 0.0
            ),
            "median_sip_amount_inr": (
                round(float(sip_group["amount_inr"].median()), 2)
                if not sip_group.empty
                else 0.0
            ),
            "preferred_amfi_code": top_scheme_code,
            "preferred_scheme_name": scheme_name,
        }
        cohort_stats.append(stats)

    df_cohort = pd.DataFrame(cohort_stats)
    df_cohort.to_csv(REPORTS_DIR / "cohort_analysis.csv", index=False)
    logger.info(f"Cohort Analysis written to {REPORTS_DIR / 'cohort_analysis.csv'}")
    return df_cohort


def run_sip_continuation_analysis(conn: sqlite3.Connection) -> pd.DataFrame:
    """Task 4: Analyze SIP inter-transaction gap for investors with >=6 transactions."""
    logger.info("Executing Task 4: SIP Continuation Analysis...")
    query = """
        SELECT investor_id, transaction_date, amount_inr
        FROM fact_transactions
        WHERE UPPER(transaction_type) = 'SIP'
        ORDER BY investor_id, transaction_date ASC
    """
    df_sip = pd.read_sql_query(query, conn)
    df_sip["transaction_date"] = pd.to_datetime(df_sip["transaction_date"])

    records = []
    for inv_id, group in df_sip.groupby("investor_id"):
        tx_count = len(group)
        if tx_count < 6:
            continue

        gaps = group["transaction_date"].diff().dt.days.dropna()
        avg_gap = float(gaps.mean())
        max_gap = int(gaps.max()) if not gaps.empty else 0
        is_at_risk = bool(avg_gap > 35.0 or max_gap > 45.0)

        records.append(
            {
                "investor_id": inv_id,
                "sip_count": tx_count,
                "avg_gap_days": round(avg_gap, 2),
                "max_gap_days": max_gap,
                "status": "at-risk" if is_at_risk else "active",
                "last_sip_date": group["transaction_date"].max().strftime("%Y-%m-%d"),
            }
        )

    df_continuity = pd.DataFrame(records)
    df_continuity.to_csv(REPORTS_DIR / "sip_continuity.csv", index=False)
    logger.info(
        f"SIP Continuation Analysis written to {REPORTS_DIR / 'sip_continuity.csv'}"
    )
    return df_continuity


def run_sector_hhi_analysis(conn: sqlite3.Connection) -> pd.DataFrame:
    """Task 6: Compute Herfindahl-Hirschman Index (HHI) for equity fund sector weights."""
    logger.info("Executing Task 6: Sector HHI Analysis...")
    query = """
        SELECT p.amfi_code, f.scheme_name, p.sector, SUM(p.weight_pct) as sector_weight
        FROM fact_portfolio p
        JOIN dim_fund f ON p.amfi_code = f.amfi_code
        GROUP BY p.amfi_code, f.scheme_name, p.sector
    """
    df_port = pd.read_sql_query(query, conn)

    records = []
    for (amfi_code, scheme_name), group in df_port.groupby(
        ["amfi_code", "scheme_name"]
    ):
        hhi = calculate_hhi(group["sector_weight"])
        div_score = calculate_diversification_score(hhi, len(group))
        top_sector = group.sort_values("sector_weight", ascending=False).iloc[0][
            "sector"
        ]

        records.append(
            {
                "amfi_code": amfi_code,
                "scheme_name": scheme_name,
                "hhi_sector": round(hhi, 2),
                "diversification_score": round(div_score, 2),
                "num_sectors": len(group),
                "top_sector": top_sector,
                "concentration_level": (
                    "High" if hhi > 2500 else ("Moderate" if hhi > 1500 else "Low")
                ),
            }
        )

    df_hhi = pd.DataFrame(records)
    df_hhi.to_csv(REPORTS_DIR / "sector_hhi.csv", index=False)

    # Generate Visualization
    plt.figure(figsize=(10, 6))
    sns.barplot(
        x="hhi_sector",
        y="scheme_name",
        hue="concentration_level",
        data=df_hhi.sort_values("hhi_sector", ascending=False).head(10),
        palette="viridis",
    )
    plt.title("Sector Concentration HHI Index Across Top Schemes", fontweight="bold")
    plt.xlabel("Sector HHI Score")
    plt.ylabel("Scheme Name")

    chart_path1 = RISK_FIGURES_DIR / "portfolio_hhi_chart.png"
    chart_path2 = FIGURES_DIR / "sector_hhi_chart.png"
    plt.savefig(chart_path1, bbox_inches="tight", dpi=300)
    plt.savefig(chart_path2, bbox_inches="tight", dpi=300)
    plt.close()

    logger.info(f"Sector HHI Analysis written to {REPORTS_DIR / 'sector_hhi.csv'}")
    return df_hhi


def main():
    """Run all Day 6 advanced analytics functions."""
    conn = sqlite3.connect(DATABASE_PATH)
    run_var_cvar_analysis(conn)
    run_rolling_sharpe_analysis(conn)
    run_cohort_analysis(conn)
    run_sip_continuation_analysis(conn)
    run_sector_hhi_analysis(conn)
    conn.close()
    logger.info("Day 6 Advanced Analytics executed successfully.")


if __name__ == "__main__":
    main()
