"""Cohort Analysis and SIP Continuation Analysis Engine.

Implements Day 6 tasks from Bluestock Capstone Handbook:
- Task 3: Investor cohort analysis grouped by first transaction year.
- Task 4: SIP continuation gap analysis flagging investors with >35 day gaps as at-risk.
- Task 6: Sector concentration analysis (HHI of sector weights).
"""

import sqlite3
import sys
from pathlib import Path

import matplotlib.pyplot as plt
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


def run_cohort_analysis(conn: sqlite3.Connection) -> pd.DataFrame:
    """Group investors by first transaction year (2024/2025).

    Computes average SIP amount, total invested, and primary fund preference per cohort.

    Args:
        conn: SQLite database connection.

    Returns:
        pd.DataFrame: Cohort summary dataset.
    """
    logger.info("Executing Investor Cohort Analysis...")
    query = """
        SELECT investor_id, transaction_date, amfi_code, transaction_type, amount_inr, state, age_group
        FROM fact_transactions
    """
    df_tx = pd.read_sql_query(query, conn)
    df_tx["transaction_date"] = pd.to_datetime(df_tx["transaction_date"])
    df_tx["year"] = df_tx["transaction_date"].dt.year

    # Determine first transaction year per investor
    first_tx = df_tx.groupby("investor_id")["transaction_date"].min().reset_index()
    first_tx["cohort_year"] = first_tx["transaction_date"].dt.year
    first_tx_map = dict(zip(first_tx["investor_id"], first_tx["cohort_year"]))

    df_tx["cohort_year"] = df_tx["investor_id"].map(first_tx_map)

    # Compute aggregations
    sip_tx = df_tx[df_tx["transaction_type"].str.upper() == "SIP"]

    cohort_stats = []
    for cohort, group in df_tx.groupby("cohort_year"):
        sip_group = group[group["transaction_type"].str.upper() == "SIP"]
        top_scheme = (
            group["amfi_code"].value_counts().index[0] if not group.empty else None
        )

        # Fetch scheme name
        scheme_name = "N/A"
        if top_scheme:
            cur = conn.cursor()
            cur.execute(
                "SELECT scheme_name FROM dim_fund WHERE amfi_code = ?",
                (str(top_scheme),),
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
                float(sip_group["amount_inr"].mean()) if not sip_group.empty else 0.0
            ),
            "median_sip_amount_inr": (
                float(sip_group["amount_inr"].median()) if not sip_group.empty else 0.0
            ),
            "preferred_amfi_code": top_scheme,
            "preferred_scheme_name": scheme_name,
        }
        cohort_stats.append(stats)

    df_cohort = pd.DataFrame(cohort_stats)
    ensure_directory(REPORTS_DIR)
    df_cohort.to_csv(REPORTS_DIR / "cohort_analysis.csv", index=False)
    logger.info(f"Cohort Analysis written to {REPORTS_DIR / 'cohort_analysis.csv'}")
    return df_cohort


def run_sip_continuation_analysis(conn: sqlite3.Connection) -> pd.DataFrame:
    """Analyze SIP continuation gap between transactions for active investors.

    Flag investors with 6+ SIP transactions having average gap > 35 days as 'at-risk'.

    Args:
        conn: SQLite database connection.

    Returns:
        pd.DataFrame: SIP continuity analysis output.
    """
    logger.info("Executing SIP Continuation Analysis...")
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
        avg_gap = gaps.mean()
        max_gap = gaps.max()
        is_at_risk = bool(avg_gap > 35.0 or max_gap > 45.0)

        records.append(
            {
                "investor_id": inv_id,
                "sip_count": tx_count,
                "avg_gap_days": round(float(avg_gap), 2),
                "max_gap_days": int(max_gap),
                "status": "at-risk" if is_at_risk else "active",
                "last_sip_date": group["transaction_date"].max().strftime("%Y-%m-%d"),
            }
        )

    df_continuity = pd.DataFrame(records)
    ensure_directory(REPORTS_DIR)
    df_continuity.to_csv(REPORTS_DIR / "sip_continuity.csv", index=False)
    logger.info(
        f"SIP Continuation Analysis written to {REPORTS_DIR / 'sip_continuity.csv'}"
    )
    return df_continuity


def run_sector_hhi_analysis(conn: sqlite3.Connection) -> pd.DataFrame:
    """Compute Herfindahl-Hirschman Index (HHI) for equity fund sector weights.

    Args:
        conn: SQLite database connection.

    Returns:
        pd.DataFrame: Sector HHI output.
    """
    logger.info("Executing Sector HHI Analysis...")
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
    ensure_directory(REPORTS_DIR)
    df_hhi.to_csv(REPORTS_DIR / "sector_hhi.csv", index=False)

    # Generate Chart
    plt.figure(figsize=(10, 6))
    sns.barplot(
        x="hhi_sector",
        y="scheme_name",
        hue="concentration_level",
        data=df_hhi.sort_values("hhi_sector", ascending=False).head(10),
        palette="viridis",
    )
    plt.title("Sector Concentration HHI Index Across Top Schemes")
    plt.xlabel("Sector HHI Score")
    plt.ylabel("Scheme Name")
    plt.savefig(FIGURES_DIR / "sector_hhi_chart.png", bbox_inches="tight")
    plt.close()

    logger.info(f"Sector HHI Analysis written to {REPORTS_DIR / 'sector_hhi.csv'}")
    return df_hhi


def run_var_cvar_analysis(conn: sqlite3.Connection) -> pd.DataFrame:
    """Compute 95% Historical VaR and CVaR for all schemes.

    Args:
        conn: SQLite database connection.

    Returns:
        pd.DataFrame: VaR/CVaR report.
    """
    logger.info("Executing VaR & CVaR Analysis...")
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
    ensure_directory(REPORTS_DIR)
    df_var.to_csv(REPORTS_DIR / "var_cvar_report.csv", index=False)
    logger.info(f"VaR/CVaR Report written to {REPORTS_DIR / 'var_cvar_report.csv'}")
    return df_var


def main():
    """Run all Day 6 advanced analytics functions."""
    conn = sqlite3.connect(DATABASE_PATH)
    run_cohort_analysis(conn)
    run_sip_continuation_analysis(conn)
    run_sector_hhi_analysis(conn)
    run_var_cvar_analysis(conn)
    conn.close()
    logger.info("Day 6 Advanced Analytics executed successfully.")


if __name__ == "__main__":
    main()
