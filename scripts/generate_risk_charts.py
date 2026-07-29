"""Generator script for Phase 4 Performance & Risk Analytics visualizations (15 Charts).

This script queries `mutual_fund_analytics.db`, computes metrics using `scripts.risk_metrics`,
and generates 15 high-resolution charts in `figures/risk_metrics/`.
"""

import sqlite3
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Ensure scripts path is loaded
sys.path.append(str(Path(__file__).resolve().parent))

from config import DATABASE_PATH, PROJECT_ROOT
from risk_metrics import (
    calculate_daily_returns,
    calculate_drawdown_duration,
    calculate_monthly_returns,
    calculate_rolling_returns,
    calculate_rolling_sharpe,
    calculate_rolling_volatility,
    calculate_weekly_returns,
    compute_all_scheme_risk_metrics,
)
from utils import ensure_directory, setup_logging

logger = setup_logging("generate_risk_charts")
RISK_FIGURES_DIR = PROJECT_ROOT / "figures" / "risk_metrics"

sns.set_theme(style="whitegrid")
plt.rcParams.update(
    {
        "font.size": 11,
        "axes.labelsize": 12,
        "axes.titlesize": 14,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "figure.titlesize": 16,
        "figure.figsize": (10, 6),
        "savefig.bbox": "tight",
    }
)


def generate_all_risk_charts() -> None:
    """Generate all 15 Phase 4 risk and performance visualizations."""
    ensure_directory(RISK_FIGURES_DIR)
    logger.info("Starting Phase 4 (15 Charts) visualization generation...")

    # Load metrics from database
    conn = sqlite3.connect(DATABASE_PATH)
    query_metrics = """
        SELECT r.*, f.scheme_name, f.category, f.fund_house
        FROM fact_risk_metrics r
        JOIN dim_fund f ON r.amfi_code = f.amfi_code
    """
    df_metrics = pd.read_sql_query(query_metrics, conn)

    if df_metrics.empty:
        logger.info("Metrics not found in DB. Computing dynamically...")
        df_metrics = compute_all_scheme_risk_metrics(DATABASE_PATH)

    # 1. Risk Return Scatter
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        x="volatility_ann_pct",
        y="sharpe_ratio",
        hue="category",
        style="category",
        data=df_metrics,
        s=130,
        alpha=0.9,
    )
    plt.axhline(0, color="gray", linestyle="--", alpha=0.6)
    plt.title("Risk-Return Scatter: Annualized Volatility vs Sharpe Ratio")
    plt.xlabel("Annualized Volatility (%)")
    plt.ylabel("Sharpe Ratio (Rf = 6.0%)")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.savefig(RISK_FIGURES_DIR / "01_risk_return_scatter.png")
    plt.close()

    # Fetch sample top schemes for rolling time-series plots
    query_top = "SELECT amfi_code, scheme_name FROM dim_fund LIMIT 4"
    df_top_schemes = pd.read_sql_query(query_top, conn)

    # 2. Rolling Sharpe Ratio
    plt.figure(figsize=(11, 6))
    for _, s_row in df_top_schemes.iterrows():
        code = int(s_row["amfi_code"])
        name = s_row["scheme_name"]
        df_s_nav = pd.read_sql_query(
            f"SELECT date_id as date, nav FROM fact_nav WHERE amfi_code = {code} ORDER BY date_id ASC",
            conn,
        )
        if len(df_s_nav) > 126:
            df_s_nav["daily_ret"] = calculate_daily_returns(df_s_nav["nav"])
            roll_sharpe = calculate_rolling_sharpe(
                df_s_nav["daily_ret"], window_days=126
            )
            plt.plot(
                pd.to_datetime(df_s_nav["date"]),
                roll_sharpe,
                label=name[:25],
                linewidth=2,
            )

    plt.axhline(0, color="black", linestyle="--", alpha=0.5)
    plt.title("6-Month Rolling Sharpe Ratio Over Time")
    plt.xlabel("Date")
    plt.ylabel("Rolling Sharpe Ratio")
    plt.legend(loc="upper left")
    plt.savefig(RISK_FIGURES_DIR / "02_rolling_sharpe.png")
    plt.close()

    # 3. Rolling Volatility
    plt.figure(figsize=(11, 6))
    for _, s_row in df_top_schemes.iterrows():
        code = int(s_row["amfi_code"])
        name = s_row["scheme_name"]
        df_s_nav = pd.read_sql_query(
            f"SELECT date_id as date, nav FROM fact_nav WHERE amfi_code = {code} ORDER BY date_id ASC",
            conn,
        )
        if len(df_s_nav) > 90:
            df_s_nav["daily_ret"] = calculate_daily_returns(df_s_nav["nav"])
            roll_vol = calculate_rolling_volatility(
                df_s_nav["daily_ret"], window_days=90
            )
            plt.plot(
                pd.to_datetime(df_s_nav["date"]), roll_vol, label=name[:25], linewidth=2
            )

    plt.title("90-Day Rolling Annualized Volatility (%)")
    plt.xlabel("Date")
    plt.ylabel("Rolling Volatility (%)")
    plt.legend(loc="upper left")
    plt.savefig(RISK_FIGURES_DIR / "03_rolling_volatility.png")
    plt.close()

    # 4. Rolling Returns
    plt.figure(figsize=(11, 6))
    for _, s_row in df_top_schemes.iterrows():
        code = int(s_row["amfi_code"])
        name = s_row["scheme_name"]
        df_s_nav = pd.read_sql_query(
            f"SELECT date_id as date, nav FROM fact_nav WHERE amfi_code = {code} ORDER BY date_id ASC",
            conn,
        )
        if len(df_s_nav) > 252:
            roll_ret = calculate_rolling_returns(df_s_nav, window_days=252)
            plt.plot(
                pd.to_datetime(roll_ret.index),
                roll_ret.values,
                label=name[:25],
                linewidth=2,
            )

    plt.axhline(0, color="black", linestyle="--", alpha=0.5)
    plt.title("1-Year Rolling CAGR Returns Over Time")
    plt.xlabel("Date")
    plt.ylabel("Rolling Return (%)")
    plt.legend(loc="upper left")
    plt.savefig(RISK_FIGURES_DIR / "04_rolling_returns.png")
    plt.close()

    # 5. Drawdown Curve Time Series
    plt.figure(figsize=(11, 6))
    sample_code = int(df_top_schemes.iloc[0]["amfi_code"])
    sample_name = df_top_schemes.iloc[0]["scheme_name"]
    df_sample_nav = pd.read_sql_query(
        f"SELECT date_id as date, nav FROM fact_nav WHERE amfi_code = {sample_code} ORDER BY date_id ASC",
        conn,
    )
    df_sample_nav["date"] = pd.to_datetime(df_sample_nav["date"])
    peak = df_sample_nav["nav"].cummax()
    dd_curve = (df_sample_nav["nav"] - peak) / peak * 100.0

    plt.fill_between(df_sample_nav["date"], dd_curve, color="crimson", alpha=0.4)
    plt.plot(
        df_sample_nav["date"],
        dd_curve,
        color="darkred",
        linewidth=1.5,
        label=f"Drawdown ({sample_name[:20]})",
    )
    plt.title("Underwater / Drawdown Time-Series Curve")
    plt.xlabel("Date")
    plt.ylabel("Drawdown (%)")
    plt.legend(loc="lower left")
    plt.savefig(RISK_FIGURES_DIR / "05_drawdown_curve.png")
    plt.close()

    # 6. Drawdown Duration Analysis
    durations = []
    for amfi_code in df_metrics["amfi_code"]:
        df_nav = pd.read_sql_query(
            f"SELECT nav FROM fact_nav WHERE amfi_code = {amfi_code} ORDER BY date_id ASC",
            conn,
        )
        dur = calculate_drawdown_duration(df_nav["nav"])
        durations.append(dur)
    df_metrics["drawdown_duration_days"] = durations

    plt.figure(figsize=(9, 5))
    sns.boxplot(
        x="category",
        y="drawdown_duration_days",
        data=df_metrics,
        palette="Purples_r",
        hue="category",
        legend=False,
    )
    plt.title("Maximum Drawdown Duration (Trading Days) by Category")
    plt.xlabel("Category")
    plt.ylabel("Max Drawdown Duration (Days)")
    plt.savefig(RISK_FIGURES_DIR / "06_drawdown_duration.png")
    plt.close()

    # 7. Alpha Beta Scatter
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x="beta", y="alpha", hue="category", data=df_metrics, s=130)
    plt.axvline(1.0, color="gray", linestyle="--", alpha=0.7)
    plt.axhline(0.0, color="gray", linestyle="--", alpha=0.7)
    plt.title("Alpha vs Beta Quadrant Matrix")
    plt.xlabel("Beta Coefficient")
    plt.ylabel("Alpha (% Excess Return)")
    plt.savefig(RISK_FIGURES_DIR / "07_alpha_beta_scatter.png")
    plt.close()

    # 8. Sharpe Rankings Bar Chart
    plt.figure(figsize=(10, 6))
    top_sharpe = df_metrics.sort_values("sharpe_ratio", ascending=False).head(10)
    sns.barplot(
        x="sharpe_ratio",
        y="scheme_name",
        data=top_sharpe,
        palette="Greens_r",
        hue="scheme_name",
        legend=False,
    )
    plt.title("Top 10 Schemes by Sharpe Ratio")
    plt.xlabel("Sharpe Ratio")
    plt.ylabel("Scheme Name")
    plt.savefig(RISK_FIGURES_DIR / "08_sharpe_rankings.png")
    plt.close()

    # 9. Sortino Rankings Bar Chart
    plt.figure(figsize=(10, 6))
    top_sortino = df_metrics.sort_values("sortino_ratio", ascending=False).head(10)
    sns.barplot(
        x="sortino_ratio",
        y="scheme_name",
        data=top_sortino,
        palette="Blues_r",
        hue="scheme_name",
        legend=False,
    )
    plt.title("Top 10 Schemes by Sortino Ratio (Downside Risk-Adjusted)")
    plt.xlabel("Sortino Ratio")
    plt.ylabel("Scheme Name")
    plt.savefig(RISK_FIGURES_DIR / "09_sortino_rankings.png")
    plt.close()

    # 10. Benchmark Comparison
    query_perf = """
        SELECT f.scheme_name, p.return_3yr_pct as scheme_cagr, p.benchmark_3yr_pct as bench_cagr
        FROM fact_performance p
        JOIN dim_fund f ON p.amfi_code = f.amfi_code
        ORDER BY p.return_3yr_pct DESC LIMIT 8
    """
    df_perf_comp = pd.read_sql_query(query_perf, conn)
    df_melt = df_perf_comp.melt(
        id_vars=["scheme_name"], var_name="Type", value_name="CAGR"
    )
    plt.figure(figsize=(11, 6))
    sns.barplot(x="CAGR", y="scheme_name", hue="Type", data=df_melt, palette="Set2")
    plt.title("3-Year CAGR Comparison: Scheme Return vs Benchmark Index")
    plt.xlabel("CAGR (%)")
    plt.ylabel("Scheme Name")
    plt.savefig(RISK_FIGURES_DIR / "10_benchmark_comparison.png")
    plt.close()

    # 11. Daily Return Distribution Charts
    plt.figure(figsize=(10, 6))
    all_daily_ret = []
    for amfi_code in df_metrics["amfi_code"].head(5):
        df_nav = pd.read_sql_query(
            f"SELECT nav FROM fact_nav WHERE amfi_code = {amfi_code} ORDER BY date_id ASC",
            conn,
        )
        ret = calculate_daily_returns(df_nav["nav"])
        all_daily_ret.extend(ret.dropna().values * 100.0)

    sns.histplot(all_daily_ret, bins=40, kde=True, color="teal")
    plt.title("Daily Return Distribution Across Schemes (%)")
    plt.xlabel("Daily Return (%)")
    plt.ylabel("Frequency")
    plt.savefig(RISK_FIGURES_DIR / "11_return_distribution.png")
    plt.close()

    # 12. Correlation Heatmap
    metric_cols = [
        "cagr_pct",
        "volatility_ann_pct",
        "downside_deviation_pct",
        "max_drawdown_pct",
        "beta",
        "alpha",
        "sharpe_ratio",
        "sortino_ratio",
        "hhi",
    ]
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        df_metrics[metric_cols].corr(),
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        linewidths=0.5,
    )
    plt.title("Risk Metric Correlation Matrix")
    plt.savefig(RISK_FIGURES_DIR / "12_correlation_heatmap.png")
    plt.close()

    # 13. Weekly vs Monthly Return Distributions
    sample_df = pd.read_sql_query(
        f"SELECT date_id as date, nav FROM fact_nav WHERE amfi_code = {sample_code} ORDER BY date_id ASC",
        conn,
    )
    df_w = calculate_weekly_returns(sample_df)
    df_m = calculate_monthly_returns(sample_df)

    plt.figure(figsize=(10, 5))
    sns.kdeplot(
        df_w["weekly_return_pct"].dropna(),
        label="Weekly Returns",
        color="purple",
        fill=True,
        alpha=0.3,
    )
    sns.kdeplot(
        df_m["monthly_return_pct"].dropna(),
        label="Monthly Returns",
        color="orange",
        fill=True,
        alpha=0.3,
    )
    plt.title("Return Distribution Density: Weekly vs Monthly Returns")
    plt.xlabel("Return (%)")
    plt.ylabel("Density")
    plt.legend()
    plt.savefig(RISK_FIGURES_DIR / "13_weekly_monthly_returns.png")
    plt.close()

    # 14. Treynor vs Calmar Ratio Rankings
    tc_df = (
        df_metrics.sort_values("calmar_ratio", ascending=False)
        .head(6)
        .melt(
            id_vars=["scheme_name"],
            value_vars=["treynor_ratio", "calmar_ratio"],
            var_name="Ratio_Metric",
            value_name="Ratio_Value",
        )
    )
    plt.figure(figsize=(11, 6))
    sns.barplot(
        x="Ratio_Value",
        y="scheme_name",
        hue="Ratio_Metric",
        data=tc_df,
        palette="Paired",
    )
    plt.title("Treynor Ratio vs Calmar Ratio Performance Rankings")
    plt.xlabel("Ratio Value")
    plt.ylabel("Scheme Name")
    plt.savefig(RISK_FIGURES_DIR / "14_treynor_calmar_rankings.png")
    plt.close()

    # 15. Portfolio Concentration & HHI Score
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        x="hhi",
        y="diversification_score",
        hue="category",
        data=df_metrics,
        s=130,
        palette="Spectral",
    )
    plt.title("Portfolio HHI Concentration Score vs Diversification Score")
    plt.xlabel("Herfindahl-Hirschman Index (HHI)")
    plt.ylabel("Diversification Score (0..100)")
    plt.savefig(RISK_FIGURES_DIR / "15_portfolio_concentration_hhi.png")
    plt.close()

    conn.close()
    logger.info(
        "Successfully generated all 15 Phase 4 visualizations in figures/risk_metrics/."
    )


if __name__ == "__main__":
    generate_all_risk_charts()
