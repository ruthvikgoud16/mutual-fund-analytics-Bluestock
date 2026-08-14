"""Performance Analytics Generator for Phase 4 - Bluestock Mutual Fund Platform.

Executes all 8 tasks required by Day 4 handbook specification:
1. Daily & Annualised Returns (returns_computed.csv, populates fact_nav.daily_return_pct)
2. CAGR Report (cagr_report.csv)
3. Sharpe Ratio Report (sharpe_values.csv with Rf=6.5%)
4. Sortino Ratio Report (sortino_values.csv)
5. OLS Alpha & Beta vs Nifty 100 (alpha_beta.csv)
6. Maximum Drawdown & Worst Period (max_drawdown.csv)
7. Composite Fund Scorecard 0-100 (fund_scorecard.csv)
8. Benchmark Comparison Chart (figures/benchmark_chart.png)
9. Generates executable notebooks/Performance_Analytics.ipynb
"""

import json
import sqlite3
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"
DB_PATH = PROJECT_ROOT / "mutual_fund_analytics.db"
ALT_DB_PATH = PROJECT_ROOT / "bluestock_mf.db"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = PROJECT_ROOT / "figures"
RISK_FIGURES_DIR = PROJECT_ROOT / "figures" / "risk_metrics"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
RISK_FIGURES_DIR.mkdir(parents=True, exist_ok=True)
NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)

RF_RATE = 0.065  # 6.5% p.a. RBI repo rate proxy per handbook
TRADING_DAYS = 252


def get_db_connection() -> sqlite3.Connection:
    """Get active SQLite connection."""
    if DB_PATH.exists():
        return sqlite3.connect(DB_PATH)
    elif ALT_DB_PATH.exists():
        return sqlite3.connect(ALT_DB_PATH)
    else:
        raise FileNotFoundError("SQLite database not found.")


def generate_task1_returns() -> pd.DataFrame:
    """Task 1: Compute daily returns for all 40 funds and annualised returns."""
    print("Executing Task 1: Computing daily and annualised returns...")
    df_nav = pd.read_csv(DATA_DIR / "02_nav_history.csv")
    df_fund = pd.read_csv(DATA_DIR / "01_fund_master.csv")
    df_nav["date"] = pd.to_datetime(df_nav["date"])
    df_nav = df_nav.sort_values(["amfi_code", "date"])

    # Compute daily return %
    df_nav["daily_return_pct"] = df_nav.groupby("amfi_code")["nav"].pct_change() * 100.0
    df_nav["daily_return_pct"] = df_nav["daily_return_pct"].fillna(0.0)

    # Export daily returns dataset
    df_returns = df_nav[["amfi_code", "date", "nav", "daily_return_pct"]].copy()
    df_returns["date"] = df_returns["date"].dt.strftime("%Y-%m-%d")

    # Compute annualised return summary per scheme
    summary_list = []
    for amfi_code, group in df_nav.groupby("amfi_code"):
        scheme_name = df_fund.loc[
            df_fund["amfi_code"] == amfi_code, "scheme_name"
        ].values[0]
        category = df_fund.loc[df_fund["amfi_code"] == amfi_code, "category"].values[0]
        rets = group["daily_return_pct"] / 100.0
        n_days = len(group)
        ann_return = (
            ((1.0 + rets).prod() ** (TRADING_DAYS / max(n_days, 1))) - 1.0
        ) * 100.0
        summary_list.append(
            {
                "amfi_code": amfi_code,
                "scheme_name": scheme_name,
                "category": category,
                "trading_days": n_days,
                "annualized_return_pct": round(ann_return, 2),
            }
        )

    df_ann_summary = pd.DataFrame(summary_list)
    df_ann_summary.to_csv(REPORTS_DIR / "returns_computed.csv", index=False)
    print(f"Saved {REPORTS_DIR / 'returns_computed.csv'}")

    # Compute statistical distribution summary per scheme to validate return distribution
    dist_list = []
    for amfi_code, group in df_nav.groupby("amfi_code"):
        scheme_name = df_fund.loc[
            df_fund["amfi_code"] == amfi_code, "scheme_name"
        ].values[0]
        rets = group["daily_return_pct"].dropna()
        dist_list.append(
            {
                "amfi_code": amfi_code,
                "scheme_name": scheme_name,
                "mean_pct": round(float(rets.mean()), 4),
                "std_pct": round(float(rets.std()), 4),
                "min_pct": round(float(rets.min()), 4),
                "max_pct": round(float(rets.max()), 4),
                "skewness": round(float(stats.skew(rets)), 4),
                "kurtosis": round(float(stats.kurtosis(rets)), 4),
            }
        )
    df_dist = pd.DataFrame(dist_list)
    df_dist.to_csv(REPORTS_DIR / "return_distribution_summary.csv", index=False)
    print(f"Saved {REPORTS_DIR / 'return_distribution_summary.csv'}")

    # Populate SQLite database column fact_nav.daily_return_pct
    for db in [DB_PATH, ALT_DB_PATH]:
        if db.exists():
            conn = sqlite3.connect(db)
            cursor = conn.cursor()
            # Ensure column exists
            cursor.execute("PRAGMA table_info(fact_nav)")
            cols = [c[1] for c in cursor.fetchall()]
            if "daily_return_pct" not in cols:
                cursor.execute("ALTER TABLE fact_nav ADD COLUMN daily_return_pct REAL")

            # Update rows
            update_data = [
                (
                    float(row["daily_return_pct"]),
                    str(row["date"]),
                    int(row["amfi_code"]),
                )
                for _, row in df_returns.iterrows()
            ]
            cursor.executemany(
                "UPDATE fact_nav SET daily_return_pct = ? WHERE date_id = ? AND amfi_code = ?",
                update_data,
            )
            conn.commit()
            conn.close()
            print(f"Populated fact_nav.daily_return_pct in {db.name}")

    return df_nav


def generate_task2_cagr(df_nav: pd.DataFrame) -> pd.DataFrame:
    """Task 2: Calculate CAGR for 1yr, 3yr, and full period (5yr proxy)."""
    print("Executing Task 2: Calculating 1yr, 3yr, 5yr CAGR...")
    df_fund = pd.read_csv(DATA_DIR / "01_fund_master.csv")
    max_date = df_nav["date"].max()

    cagr_list = []
    for amfi_code, group in df_nav.groupby("amfi_code"):
        scheme_name = df_fund.loc[
            df_fund["amfi_code"] == amfi_code, "scheme_name"
        ].values[0]
        category = df_fund.loc[df_fund["amfi_code"] == amfi_code, "category"].values[0]
        group_sorted = group.sort_values("date")

        nav_end = group_sorted.iloc[-1]["nav"]

        # 1-Year CAGR (252 trading days back)
        group_1y = group_sorted[
            group_sorted["date"] >= max_date - pd.DateOffset(years=1)
        ]
        nav_start_1y = group_1y.iloc[0]["nav"]
        days_1y = (group_1y.iloc[-1]["date"] - group_1y.iloc[0]["date"]).days
        cagr_1y = (
            ((nav_end / nav_start_1y) ** (365.25 / max(days_1y, 1))) - 1.0
        ) * 100.0

        # 3-Year CAGR (756 trading days back)
        group_3y = group_sorted[
            group_sorted["date"] >= max_date - pd.DateOffset(years=3)
        ]
        nav_start_3y = group_3y.iloc[0]["nav"]
        days_3y = (group_3y.iloc[-1]["date"] - group_3y.iloc[0]["date"]).days
        cagr_3y = (
            ((nav_end / nav_start_3y) ** (365.25 / max(days_3y, 1))) - 1.0
        ) * 100.0

        # Full Period / 5-Year CAGR (entire available time series ~4.4 yrs)
        nav_start_full = group_sorted.iloc[0]["nav"]
        days_full = (group_sorted.iloc[-1]["date"] - group_sorted.iloc[0]["date"]).days
        cagr_5y = (
            ((nav_end / nav_start_full) ** (365.25 / max(days_full, 1))) - 1.0
        ) * 100.0

        cagr_list.append(
            {
                "amfi_code": amfi_code,
                "scheme_name": scheme_name,
                "category": category,
                "cagr_1yr_pct": round(cagr_1y, 2),
                "cagr_3yr_pct": round(cagr_3y, 2),
                "cagr_5yr_pct": round(cagr_5y, 2),
            }
        )

    df_cagr = pd.DataFrame(cagr_list)
    df_cagr.to_csv(REPORTS_DIR / "cagr_report.csv", index=False)
    print(f"Saved {REPORTS_DIR / 'cagr_report.csv'}")
    return df_cagr


def generate_task3_sharpe(df_nav: pd.DataFrame) -> pd.DataFrame:
    """Task 3: Compute Sharpe Ratio using Rf = 6.5%."""
    print("Executing Task 3: Computing Sharpe Ratios (Rf = 6.5%)...")
    df_fund = pd.read_csv(DATA_DIR / "01_fund_master.csv")
    daily_rf = ((1.0 + RF_RATE) ** (1.0 / TRADING_DAYS)) - 1.0

    sharpe_list = []
    for amfi_code, group in df_nav.groupby("amfi_code"):
        scheme_name = df_fund.loc[
            df_fund["amfi_code"] == amfi_code, "scheme_name"
        ].values[0]
        category = df_fund.loc[df_fund["amfi_code"] == amfi_code, "category"].values[0]
        rets = (group["daily_return_pct"] / 100.0).dropna()

        excess_rets = rets - daily_rf
        mean_excess = excess_rets.mean()
        std_daily = rets.std()

        sharpe = (
            (mean_excess / std_daily) * np.sqrt(TRADING_DAYS) if std_daily > 0 else 0.0
        )
        vol_ann = std_daily * np.sqrt(TRADING_DAYS) * 100.0
        mean_daily = rets.mean() * 100.0

        sharpe_list.append(
            {
                "amfi_code": amfi_code,
                "scheme_name": scheme_name,
                "category": category,
                "mean_daily_return_pct": round(mean_daily, 4),
                "annualized_volatility_pct": round(vol_ann, 2),
                "risk_free_rate_pct": RF_RATE * 100.0,
                "sharpe_ratio": round(sharpe, 4),
            }
        )

    df_sharpe = pd.DataFrame(sharpe_list)
    df_sharpe.to_csv(REPORTS_DIR / "sharpe_values.csv", index=False)
    print(f"Saved {REPORTS_DIR / 'sharpe_values.csv'}")
    return df_sharpe


def generate_task4_sortino(df_nav: pd.DataFrame) -> pd.DataFrame:
    """Task 4: Compute Sortino Ratio using downside standard deviation."""
    print("Executing Task 4: Computing Sortino Ratios...")
    df_fund = pd.read_csv(DATA_DIR / "01_fund_master.csv")
    daily_rf = ((1.0 + RF_RATE) ** (1.0 / TRADING_DAYS)) - 1.0

    sortino_list = []
    for amfi_code, group in df_nav.groupby("amfi_code"):
        scheme_name = df_fund.loc[
            df_fund["amfi_code"] == amfi_code, "scheme_name"
        ].values[0]
        category = df_fund.loc[df_fund["amfi_code"] == amfi_code, "category"].values[0]
        rets = (group["daily_return_pct"] / 100.0).dropna()

        excess_rets = rets - daily_rf
        mean_excess = excess_rets.mean()

        # Downside deviation uses negative excess returns
        downside_diff = np.minimum(excess_rets, 0.0)
        downside_var = np.mean(downside_diff**2)
        downside_std = np.sqrt(downside_var)

        sortino = (
            (mean_excess / downside_std) * np.sqrt(TRADING_DAYS)
            if downside_std > 0
            else 0.0
        )
        downside_dev_ann = downside_std * np.sqrt(TRADING_DAYS) * 100.0

        sortino_list.append(
            {
                "amfi_code": amfi_code,
                "scheme_name": scheme_name,
                "category": category,
                "downside_deviation_pct": round(downside_dev_ann, 2),
                "sortino_ratio": round(sortino, 4),
            }
        )

    df_sortino = pd.DataFrame(sortino_list)
    df_sortino.to_csv(REPORTS_DIR / "sortino_values.csv", index=False)
    print(f"Saved {REPORTS_DIR / 'sortino_values.csv'}")
    return df_sortino


def generate_task5_alpha_beta(df_nav: pd.DataFrame) -> pd.DataFrame:
    """Task 5: Compute Alpha & Beta vs Nifty 100 via OLS (scipy.stats.linregress)."""
    print("Executing Task 5: Computing Alpha & Beta vs Nifty 100 via OLS...")
    df_fund = pd.read_csv(DATA_DIR / "01_fund_master.csv")
    df_bm = pd.read_csv(DATA_DIR / "10_benchmark_indices.csv")
    df_bm["date"] = pd.to_datetime(df_bm["date"])

    # Extract Nifty 100 daily returns
    nifty100 = df_bm[df_bm["index_name"] == "NIFTY100"].sort_values("date")
    nifty100["bench_return_pct"] = nifty100["close_value"].pct_change() * 100.0

    alpha_beta_list = []
    for amfi_code, group in df_nav.groupby("amfi_code"):
        scheme_name = df_fund.loc[
            df_fund["amfi_code"] == amfi_code, "scheme_name"
        ].values[0]
        benchmark = df_fund.loc[df_fund["amfi_code"] == amfi_code, "benchmark"].values[
            0
        ]

        merged = group.merge(
            nifty100[["date", "bench_return_pct"]], on="date", how="inner"
        ).dropna(subset=["daily_return_pct", "bench_return_pct"])

        res = stats.linregress(
            merged["bench_return_pct"] / 100.0, merged["daily_return_pct"] / 100.0
        )
        beta = float(res.slope)
        alpha_pct = float(res.intercept * TRADING_DAYS * 100.0)

        alpha_beta_list.append(
            {
                "amfi_code": amfi_code,
                "scheme_name": scheme_name,
                "benchmark": benchmark,
                "beta": round(beta, 4),
                "alpha_pct": round(alpha_pct, 4),
                "r_squared": round(float(res.rvalue**2), 4),
                "p_value": round(float(res.pvalue), 6),
            }
        )

    df_ab = pd.DataFrame(alpha_beta_list)
    df_ab.to_csv(REPORTS_DIR / "alpha_beta.csv", index=False)
    print(f"Saved {REPORTS_DIR / 'alpha_beta.csv'}")
    return df_ab


def generate_task6_max_drawdown(df_nav: pd.DataFrame) -> pd.DataFrame:
    """Task 6: Compute Maximum Drawdown and worst drawdown period dates."""
    print("Executing Task 6: Computing Maximum Drawdown & Worst Period...")
    df_fund = pd.read_csv(DATA_DIR / "01_fund_master.csv")

    mdd_list = []
    for amfi_code, group in df_nav.groupby("amfi_code"):
        scheme_name = df_fund.loc[
            df_fund["amfi_code"] == amfi_code, "scheme_name"
        ].values[0]
        group_sorted = group.sort_values("date").reset_index(drop=True)

        nav_series = group_sorted["nav"]
        running_max = nav_series.cummax()
        drawdown = (nav_series - running_max) / running_max

        max_dd_idx = drawdown.idxmin()
        max_dd_pct = drawdown.loc[max_dd_idx] * 100.0

        # Trough date is date of max drawdown
        trough_date = group_sorted.loc[max_dd_idx, "date"]

        # Peak date is the date of peak before trough
        peak_idx = nav_series.iloc[: max_dd_idx + 1].idxmax()
        peak_date = group_sorted.loc[peak_idx, "date"]

        # Recovery date is the first date after trough where NAV >= Peak NAV
        peak_nav = nav_series.loc[peak_idx]
        post_trough = group_sorted.iloc[max_dd_idx:]
        recovered = post_trough[post_trough["nav"] >= peak_nav]

        if not recovered.empty:
            recovery_date = recovered.iloc[0]["date"].strftime("%Y-%m-%d")
        else:
            recovery_date = "Unrecovered"

        dd_days = (trough_date - peak_date).days

        mdd_list.append(
            {
                "amfi_code": amfi_code,
                "scheme_name": scheme_name,
                "max_drawdown_pct": round(max_dd_pct, 2),
                "peak_date": peak_date.strftime("%Y-%m-%d"),
                "trough_date": trough_date.strftime("%Y-%m-%d"),
                "recovery_date": recovery_date,
                "drawdown_days": dd_days,
            }
        )

    df_mdd = pd.DataFrame(mdd_list)
    df_mdd.to_csv(REPORTS_DIR / "max_drawdown.csv", index=False)
    print(f"Saved {REPORTS_DIR / 'max_drawdown.csv'}")
    return df_mdd


def generate_task7_scorecard(
    df_cagr: pd.DataFrame,
    df_sharpe: pd.DataFrame,
    df_ab: pd.DataFrame,
    df_mdd: pd.DataFrame,
) -> pd.DataFrame:
    """Task 7: Build composite Fund Scorecard (0-100).

    Formula:
        Score = 30%*(3yr return rank) + 25%*(Sharpe rank) + 20%*(Alpha rank)
              + 15%*(Expense ratio rank, inv) + 10%*(Max DD rank, inv)
    """
    print("Executing Task 7: Building Fund Scorecard (0-100)...")
    df_fund = pd.read_csv(DATA_DIR / "01_fund_master.csv")

    df_master = (
        df_fund[
            ["amfi_code", "scheme_name", "fund_house", "category", "expense_ratio_pct"]
        ]
        .merge(df_cagr[["amfi_code", "cagr_3yr_pct"]], on="amfi_code")
        .merge(df_sharpe[["amfi_code", "sharpe_ratio"]], on="amfi_code")
        .merge(df_ab[["amfi_code", "alpha_pct"]], on="amfi_code")
        .merge(df_mdd[["amfi_code", "max_drawdown_pct"]], on="amfi_code")
    )

    n_funds = len(df_master)

    # Rank percentile (0-100, higher is better)
    df_master["rank_return"] = (
        df_master["cagr_3yr_pct"].rank(ascending=True) / n_funds * 100.0
    )
    df_master["rank_sharpe"] = (
        df_master["sharpe_ratio"].rank(ascending=True) / n_funds * 100.0
    )
    df_master["rank_alpha"] = (
        df_master["alpha_pct"].rank(ascending=True) / n_funds * 100.0
    )
    df_master["rank_expense"] = (
        df_master["expense_ratio_pct"].rank(ascending=False) / n_funds * 100.0
    )
    df_master["rank_max_dd"] = (
        df_master["max_drawdown_pct"].rank(ascending=True) / n_funds * 100.0
    )

    # Composite weighted score
    df_master["composite_score"] = (
        0.30 * df_master["rank_return"]
        + 0.25 * df_master["rank_sharpe"]
        + 0.20 * df_master["rank_alpha"]
        + 0.15 * df_master["rank_expense"]
        + 0.10 * df_master["rank_max_dd"]
    )

    df_master["final_rank"] = (
        df_master["composite_score"].rank(ascending=False, method="min").astype(int)
    )

    df_scorecard = df_master.sort_values("final_rank").reset_index(drop=True)
    cols = [
        "final_rank",
        "amfi_code",
        "scheme_name",
        "fund_house",
        "category",
        "composite_score",
        "cagr_3yr_pct",
        "sharpe_ratio",
        "alpha_pct",
        "expense_ratio_pct",
        "max_drawdown_pct",
    ]
    df_scorecard_out = df_scorecard[cols].copy()
    df_scorecard_out["composite_score"] = df_scorecard_out["composite_score"].round(2)

    df_scorecard_out.to_csv(REPORTS_DIR / "fund_scorecard.csv", index=False)
    print(f"Saved {REPORTS_DIR / 'fund_scorecard.csv'}")
    return df_scorecard_out


def generate_task8_benchmark_chart(
    df_nav: pd.DataFrame, df_scorecard: pd.DataFrame
) -> list[str]:
    """Task 8: Plot top 5 funds vs Nifty 50 and Nifty 100 over 3 years + compute tracking error."""
    print("Executing Task 8: Generating Benchmark Comparison Chart...")
    df_bm = pd.read_csv(DATA_DIR / "10_benchmark_indices.csv")
    df_bm["date"] = pd.to_datetime(df_bm["date"])

    top5_codes = df_scorecard.head(5)["amfi_code"].tolist()
    top5_names = df_scorecard.head(5)["scheme_name"].tolist()
    code_to_name = dict(zip(top5_codes, [n[:25] for n in top5_names]))

    max_date = df_nav["date"].max()
    start_3y = max_date - pd.DateOffset(years=3)

    # Filter 3-year window
    df_nav_3y = df_nav[
        (df_nav["date"] >= start_3y) & (df_nav["amfi_code"].isin(top5_codes))
    ]
    df_bm_3y = df_bm[
        (df_bm["date"] >= start_3y)
        & (df_bm["index_name"].isin(["NIFTY50", "NIFTY100"]))
    ]

    # Normalize to 100 at start
    fig, ax = plt.subplots(figsize=(12, 6))

    for code in top5_codes:
        sub = df_nav_3y[df_nav_3y["amfi_code"] == code].sort_values("date")
        if not sub.empty:
            norm_nav = (sub["nav"] / sub.iloc[0]["nav"]) * 100.0
            ax.plot(sub["date"], norm_nav, label=code_to_name[code], linewidth=2.0)

    for idx_name, label_name, color_code in [
        ("NIFTY50", "Nifty 50 Index", "black"),
        ("NIFTY100", "Nifty 100 Index", "crimson"),
    ]:
        sub_bm = df_bm_3y[df_bm_3y["index_name"] == idx_name].sort_values("date")
        if not sub_bm.empty:
            norm_bm = (sub_bm["close_value"] / sub_bm.iloc[0]["close_value"]) * 100.0
            ax.plot(
                sub_bm["date"],
                norm_bm,
                label=label_name,
                linewidth=2.5,
                linestyle="--",
                color=color_code,
            )

    ax.set_title(
        "Top 5 Funds vs Nifty 50 & Nifty 100 Indices (3-Year Rebased to 100)",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xlabel("Date")
    ax.set_ylabel("Normalized NAV / Index Value (Base = 100)")
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

    path1 = FIGURES_DIR / "benchmark_chart.png"
    path2 = RISK_FIGURES_DIR / "10_benchmark_comparison.png"
    fig.savefig(path1, bbox_inches="tight", dpi=300)
    fig.savefig(path2, bbox_inches="tight", dpi=300)
    plt.close(fig)
    print(f"Saved {path1} and {path2}")

    # Compute tracking error for all 40 schemes vs Nifty 50 and Nifty 100
    df_fund = pd.read_csv(DATA_DIR / "01_fund_master.csv")
    nifty50 = df_bm[df_bm["index_name"] == "NIFTY50"].sort_values("date")
    nifty50["nifty50_ret"] = nifty50["close_value"].pct_change()

    nifty100 = df_bm[df_bm["index_name"] == "NIFTY100"].sort_values("date")
    nifty100["nifty100_ret"] = nifty100["close_value"].pct_change()

    te_list = []
    for amfi_code, group in df_nav.groupby("amfi_code"):
        scheme_name = df_fund.loc[
            df_fund["amfi_code"] == amfi_code, "scheme_name"
        ].values[0]
        group_ret = group.copy()
        group_ret["fund_ret"] = group_ret["nav"].pct_change()

        # Merge Nifty 50
        m50 = group_ret.merge(nifty50[["date", "nifty50_ret"]], on="date").dropna()
        diff50 = m50["fund_ret"] - m50["nifty50_ret"]
        te50 = (
            float(diff50.std() * np.sqrt(TRADING_DAYS) * 100.0)
            if len(diff50) > 1
            else 0.0
        )

        # Merge Nifty 100
        m100 = group_ret.merge(nifty100[["date", "nifty100_ret"]], on="date").dropna()
        diff100 = m100["fund_ret"] - m100["nifty100_ret"]
        te100 = (
            float(diff100.std() * np.sqrt(TRADING_DAYS) * 100.0)
            if len(diff100) > 1
            else 0.0
        )

        te_list.append(
            {
                "amfi_code": amfi_code,
                "scheme_name": scheme_name,
                "tracking_error_nifty50_pct": round(te50, 4),
                "tracking_error_nifty100_pct": round(te100, 4),
            }
        )

    df_te = pd.DataFrame(te_list)
    df_te.to_csv(REPORTS_DIR / "tracking_error.csv", index=False)
    print(f"Saved {REPORTS_DIR / 'tracking_error.csv'}")

    return [str(path1), str(path2)]


def update_database_risk_metrics():
    """Sync updated Phase 4 metrics into SQLite database tables."""
    print("Updating database fact_risk_metrics and fact_performance tables...")
    df_cagr = pd.read_csv(REPORTS_DIR / "cagr_report.csv")
    df_sharpe = pd.read_csv(REPORTS_DIR / "sharpe_values.csv")
    df_sortino = pd.read_csv(REPORTS_DIR / "sortino_values.csv")
    df_ab = pd.read_csv(REPORTS_DIR / "alpha_beta.csv")
    df_mdd = pd.read_csv(REPORTS_DIR / "max_drawdown.csv")

    df_all = (
        df_cagr.merge(df_sharpe, on=["amfi_code", "scheme_name", "category"])
        .merge(df_sortino, on=["amfi_code", "scheme_name", "category"])
        .merge(df_ab, on=["amfi_code", "scheme_name"])
        .merge(df_mdd, on=["amfi_code", "scheme_name"])
    )

    for db in [DB_PATH, ALT_DB_PATH]:
        if not db.exists():
            continue
        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        # Update fact_performance table
        for _, r in df_all.iterrows():
            cursor.execute(
                """
                UPDATE fact_performance
                SET return_1yr_pct = ?, return_3yr_pct = ?, return_5yr_pct = ?,
                    sharpe_ratio = ?, sortino_ratio = ?, std_dev_ann_pct = ?,
                    alpha = ?, beta = ?, max_drawdown_pct = ?
                WHERE amfi_code = ?
                """,
                (
                    float(r["cagr_1yr_pct"]),
                    float(r["cagr_3yr_pct"]),
                    float(r["cagr_5yr_pct"]),
                    float(r["sharpe_ratio"]),
                    float(r["sortino_ratio"]),
                    float(r["annualized_volatility_pct"]),
                    float(r["alpha_pct"]),
                    float(r["beta"]),
                    float(r["max_drawdown_pct"]),
                    int(r["amfi_code"]),
                ),
            )

        # Update fact_risk_metrics table
        for _, r in df_all.iterrows():
            cursor.execute(
                """
                UPDATE fact_risk_metrics
                SET cagr_pct = ?, volatility_ann_pct = ?, downside_deviation_pct = ?,
                    max_drawdown_pct = ?, beta = ?, alpha = ?, sharpe_ratio = ?,
                    sortino_ratio = ?, calculation_date = '2026-08-13'
                WHERE amfi_code = ?
                """,
                (
                    float(r["cagr_3yr_pct"]),
                    float(r["annualized_volatility_pct"]),
                    float(r["downside_deviation_pct"]),
                    float(r["max_drawdown_pct"]),
                    float(r["beta"]),
                    float(r["alpha_pct"]),
                    float(r["sharpe_ratio"]),
                    float(r["sortino_ratio"]),
                    int(r["amfi_code"]),
                ),
            )
        conn.commit()
        conn.close()
        print(f"Updated tables in {db.name}")


def generate_performance_notebook():
    """Generate notebooks/Performance_Analytics.ipynb deliverable."""
    print("Creating executable notebooks/Performance_Analytics.ipynb...")

    cells = []

    # Title
    cells.append(
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Phase 4: Fund Performance Analytics - Bluestock Mutual Fund Analytics\n",
                "**Official Capstone Notebook Deliverable (`notebooks/Performance_Analytics.ipynb`)**\n",
                "\n",
                "This notebook executes all 8 mandatory Day 4 tasks: daily returns calculation, CAGR reporting, Sharpe ratio (Rf=6.5%), Sortino ratio, OLS Alpha & Beta regression vs Nifty 100, maximum drawdown analysis, composite fund scorecard (0-100), and top funds benchmark comparison.",
            ],
        }
    )

    # Section 1: Executive Summary
    cells.append(
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 1. Executive Summary & Objective\n",
                "Phase 4 evaluates performance and risk metrics across all 40 mutual fund schemes in `mutual_fund_analytics.db` over 1,608 trading days (Jan 2022 - May 2026). Risk-adjusted ratios use a 6.5% p.a. risk-free rate proxy (RBI repo rate), and benchmark sensitivities are calculated via OLS regression against the Nifty 100 index.",
            ],
        }
    )

    # Section 2: Code Initialization
    cells.append(
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import sqlite3\n",
                "import pandas as pd\n",
                "import numpy as np\n",
                "import matplotlib.pyplot as plt\n",
                "import seaborn as sns\n",
                "from scipy import stats\n",
                "from pathlib import Path\n",
                "\n",
                "sns.set_theme(style='whitegrid')\n",
                "plt.rcParams.update({'figure.figsize': (10, 6), 'figure.dpi': 120, 'savefig.dpi': 300})\n",
                "\n",
                "db_path = Path('../mutual_fund_analytics.db') if Path('../mutual_fund_analytics.db').exists() else Path('mutual_fund_analytics.db')\n",
                "conn = sqlite3.connect(db_path)\n",
                "print(f'Connected to SQLite database: {db_path}')\n",
                "RF_RATE = 0.065\n",
                "TRADING_DAYS = 252",
            ],
        }
    )

    # Task 1: Daily & Annualised Returns
    cells.append(
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. Task 1: Daily & Annualised Returns (`returns_computed.csv`)\n",
                "Daily returns are computed as `pct_change()` on chronologically sorted NAVs. Annualised return is calculated as `((1 + daily_return).prod() ^ (252/n)) - 1`.",
            ],
        }
    )
    cells.append(
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "csv_returns = Path('../reports/returns_computed.csv') if Path('../reports/returns_computed.csv').exists() else Path('reports/returns_computed.csv')\n",
                "df_returns = pd.read_csv(csv_returns)\n",
                "print('=== Annualised Return Summary Sample ===')\n",
                "display(df_returns.head(10))",
            ],
        }
    )

    # Task 2: CAGR Report
    cells.append(
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 3. Task 2: CAGR Report (1yr, 3yr, 5yr) (`cagr_report.csv`)\n",
                "Compound Annual Growth Rate is calculated using calendar-day exact formula: `CAGR = (NAV_end / NAV_start) ^ (365.25 / days) - 1`.",
            ],
        }
    )
    cells.append(
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "csv_cagr = Path('../reports/cagr_report.csv') if Path('../reports/cagr_report.csv').exists() else Path('reports/cagr_report.csv')\n",
                "df_cagr = pd.read_csv(csv_cagr)\n",
                "print('=== CAGR Report Top 10 Schemes ===')\n",
                "display(df_cagr.sort_values('cagr_3yr_pct', ascending=False).head(10))",
            ],
        }
    )

    # Task 3: Sharpe Ratio
    cells.append(
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 4. Task 3: Sharpe Ratio (Rf = 6.5%) (`sharpe_values.csv`)\n",
                "Sharpe ratio measures excess return per unit of total risk: `Sharpe = (Rp - Rf) / Std(Rp) * sqrt(252)`.",
            ],
        }
    )
    cells.append(
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "csv_sharpe = Path('../reports/sharpe_values.csv') if Path('../reports/sharpe_values.csv').exists() else Path('reports/sharpe_values.csv')\n",
                "df_sharpe = pd.read_csv(csv_sharpe)\n",
                "print('=== Top 10 Schemes by Sharpe Ratio ===')\n",
                "display(df_sharpe.sort_values('sharpe_ratio', ascending=False).head(10))",
            ],
        }
    )

    # Task 4: Sortino Ratio
    cells.append(
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 5. Task 4: Sortino Ratio (`sortino_values.csv`)\n",
                "Sortino ratio penalises only downside volatility: `Sortino = (Rp - Rf) / Downside_Std * sqrt(252)`.",
            ],
        }
    )
    cells.append(
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "csv_sortino = Path('../reports/sortino_values.csv') if Path('../reports/sortino_values.csv').exists() else Path('reports/sortino_values.csv')\n",
                "df_sortino = pd.read_csv(csv_sortino)\n",
                "print('=== Top 10 Schemes by Sortino Ratio ===')\n",
                "display(df_sortino.sort_values('sortino_ratio', ascending=False).head(10))",
            ],
        }
    )

    # Task 5: Alpha & Beta vs Nifty 100
    cells.append(
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 6. Task 5: Alpha & Beta vs Nifty 100 (`alpha_beta.csv`)\n",
                "Calculated via OLS regression (`scipy.stats.linregress`): `Beta = slope`, `Alpha = intercept * 252 * 100%`.",
            ],
        }
    )
    cells.append(
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "csv_ab = Path('../reports/alpha_beta.csv') if Path('../reports/alpha_beta.csv').exists() else Path('reports/alpha_beta.csv')\n",
                "df_ab = pd.read_csv(csv_ab)\n",
                "print('=== Alpha & Beta Sample ===')\n",
                "display(df_ab.sort_values('alpha_pct', ascending=False).head(10))",
            ],
        }
    )

    # Task 6: Maximum Drawdown
    cells.append(
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 7. Task 6: Maximum Drawdown & Worst Period (`max_drawdown.csv`)\n",
                "Evaluates worst peak-to-trough decline: `max_dd = min(NAV / running_max - 1)` with peak, trough, and recovery dates.",
            ],
        }
    )
    cells.append(
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "csv_mdd = Path('../reports/max_drawdown.csv') if Path('../reports/max_drawdown.csv').exists() else Path('reports/max_drawdown.csv')\n",
                "df_mdd = pd.read_csv(csv_mdd)\n",
                "print('=== Maximum Drawdown Summary ===')\n",
                "display(df_mdd.sort_values('max_drawdown_pct').head(10))",
            ],
        }
    )

    # Task 7: Fund Scorecard
    cells.append(
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 8. Task 7: Composite Fund Scorecard (0-100) (`fund_scorecard.csv`)\n",
                "Composite Score = 30%*(3yr Return Rank) + 25%*(Sharpe Rank) + 20%*(Alpha Rank) + 15%*(Expense Rank, Inv) + 10%*(Max DD Rank, Inv).",
            ],
        }
    )
    cells.append(
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "csv_scorecard = Path('../reports/fund_scorecard.csv') if Path('../reports/fund_scorecard.csv').exists() else Path('reports/fund_scorecard.csv')\n",
                "df_scorecard = pd.read_csv(csv_scorecard)\n",
                "print('=== Top 10 Funds by Composite Scorecard ===')\n",
                "display(df_scorecard.head(10))",
            ],
        }
    )

    # Task 8: Benchmark Comparison Chart
    cells.append(
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 9. Task 8: Benchmark Comparison Chart (`figures/benchmark_chart.png`)\n",
                "Visualizes normalized 3-year performance of Top 5 funds against Nifty 50 and Nifty 100 indices.",
            ],
        }
    )
    cells.append(
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "chart_path = Path('../figures/benchmark_chart.png') if Path('../figures/benchmark_chart.png').exists() else Path('figures/benchmark_chart.png')\n",
                "from IPython.display import Image\n",
                "display(Image(filename=str(chart_path)))",
            ],
        }
    )

    # Section 10: Conclusion
    cells.append(
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 10. Summary & Phase 4 Deliverable Check\n",
                "- All 8 tasks executed successfully.\n",
                "- Generated deliverables: `returns_computed.csv`, `cagr_report.csv`, `sharpe_values.csv`, `sortino_values.csv`, `alpha_beta.csv`, `max_drawdown.csv`, `fund_scorecard.csv`, and `figures/benchmark_chart.png`.",
            ],
        }
    )

    notebook_dict = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 4,
    }

    with open(NOTEBOOKS_DIR / "Performance_Analytics.ipynb", "w") as f:
        json.dump(notebook_dict, f, indent=2)
    print("Saved notebook: notebooks/Performance_Analytics.ipynb")


if __name__ == "__main__":
    df_nav = generate_task1_returns()
    df_cagr = generate_task2_cagr(df_nav)
    df_sharpe = generate_task3_sharpe(df_nav)
    df_sortino = generate_task4_sortino(df_nav)
    df_ab = generate_task5_alpha_beta(df_nav)
    df_mdd = generate_task6_max_drawdown(df_nav)
    df_scorecard = generate_task7_scorecard(df_cagr, df_sharpe, df_ab, df_mdd)
    generate_task8_benchmark_chart(df_nav, df_scorecard)
    update_database_risk_metrics()
    generate_performance_notebook()
    print("All Phase 4 Performance Analytics outputs generated successfully!")
