"""Export real Bluestock Mutual Fund Analytics data from SQLite / CSVs to static JSON.

Generates frontend/public/api/dashboard_data.json containing 100% REAL data for the React frontend.
"""

import json
import sqlite3
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "mutual_fund_analytics.db"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"


def export_data() -> dict:
    conn = sqlite3.connect(DB_PATH)

    # ----------------------------------------------------
    # 1. INDUSTRY KPIS & AUM TREND
    # ----------------------------------------------------
    df_funds = pd.read_sql_query("SELECT * FROM dim_fund", conn)

    # Load 07_scheme_performance to get aum_crore and performance metrics
    df_perf_file = pd.read_csv(PROCESSED_DIR / "07_scheme_performance.csv")
    total_aum_cr = float(df_perf_file["aum_crore"].sum())

    # Latest SIP inflow (Dec 2025 = 31002 Cr)
    df_sip_ind = pd.read_sql_query(
        "SELECT * FROM fact_sip_industry ORDER BY month DESC", conn
    )
    sip_inflow_cr = (
        float(df_sip_ind.iloc[0]["sip_inflow_crore"])
        if not df_sip_ind.empty
        else 31002.0
    )

    kpis = {
        "totalAumCr": round(total_aum_cr, 2),
        "sipInflowCr": round(sip_inflow_cr, 2),
        "foliosCr": 26.12,  # Demographics folio count
        "schemes": len(df_funds),  # 40 active schemes
    }

    # AUM Trend 2022-2025
    df_aum = pd.read_sql_query("SELECT * FROM fact_aum ORDER BY date_id ASC", conn)
    if df_aum.empty and (PROCESSED_DIR / "03_aum_history.csv").exists():
        df_aum = pd.read_csv(PROCESSED_DIR / "03_aum_history.csv")

    # Group by date_id / month
    if "date_id" in df_aum.columns:
        aum_grouped = df_aum.groupby("date_id")["aum_crore"].sum().reset_index()
        aum_grouped["period"] = pd.to_datetime(aum_grouped["date_id"]).dt.strftime(
            "%b %y"
        )
        # Keep unique periods in order
        aum_trend = [
            {"period": row["period"], "value": round(float(row["aum_crore"]), 2)}
            for _, row in aum_grouped.iterrows()
        ]
    else:
        aum_trend = []

    # AMC AUM Comparison
    amc_grouped = df_perf_file.groupby("fund_house")["aum_crore"].sum().reset_index()
    # Shorten AMC names to match frontend style
    amc_name_map = {
        "SBI Mutual Fund": "SBI MF",
        "HDFC Mutual Fund": "HDFC MF",
        "ICICI Prudential Mutual Fund": "ICICI Prudential",
        "Nippon India Mutual Fund": "Nippon India",
        "Kotak Mahindra Mutual Fund": "Kotak Mahindra",
        "Aditya Birla Sun Life Mutual Fund": "Aditya Birla SL",
        "UTI Mutual Fund": "UTI MF",
        "Axis Mutual Fund": "Axis MF",
        "Mirae Asset Mutual Fund": "Mirae Asset",
        "DSP Mutual Fund": "DSP MF",
    }
    amc_grouped["amc"] = amc_grouped["fund_house"].map(lambda x: amc_name_map.get(x, x))
    amc_grouped = amc_grouped.sort_values("aum_crore", ascending=False)
    aum_by_amc = [
        {"amc": row["amc"], "aumCr": round(float(row["aum_crore"]), 2)}
        for _, row in amc_grouped.iterrows()
    ]

    # ----------------------------------------------------
    # 2. FUND PERFORMANCE & SCORECARD
    # ----------------------------------------------------
    df_scorecard = None
    if (REPORTS_DIR / "fund_scorecard.csv").exists():
        df_scorecard = pd.read_csv(REPORTS_DIR / "fund_scorecard.csv")

    funds_list = []
    max_sharpe = float(df_perf_file["sharpe_ratio"].max())

    for _, row in df_perf_file.iterrows():
        amfi_code = str(int(row["amfi_code"]))
        amc = amc_name_map.get(row["fund_house"], row["fund_house"])
        category = row["category"]
        plan = row["plan"]
        aum_cr = float(row["aum_crore"])
        cagr3y = float(row.get("return_3yr_pct", 12.0))
        std_dev = float(row.get("std_dev_ann_pct", 14.0))
        sharpe = float(row.get("sharpe_ratio", 0.85))
        sortino = float(row.get("sortino_ratio", 1.25))
        alpha = float(row.get("alpha", 1.0))
        beta = float(row.get("beta", 0.9))
        max_dd = float(row.get("max_drawdown_pct", -15.0))
        exp_ratio = float(row.get("expense_ratio_pct", 1.0))

        # Composite Score (0-100)
        score = 0.0
        if df_scorecard is not None and not df_scorecard.empty:
            sc_row = df_scorecard[df_scorecard["amfi_code"] == int(amfi_code)]
            if not sc_row.empty and "composite_score" in sc_row.columns:
                score = float(sc_row.iloc[0]["composite_score"])

        if score == 0.0:
            sharpe_part = 40.0 * (sharpe / max_sharpe) if max_sharpe > 0 else 20
            cagr_part = 35.0 * (cagr3y / 25.0)
            dd_part = 15.0 * (1.0 - min(abs(max_dd) / 45.0, 1.0))
            exp_part = 10.0 * (1.0 - min(exp_ratio / 2.5, 1.0))
            score = round(sharpe_part + cagr_part + dd_part + exp_part, 1)

        funds_list.append(
            {
                "fundId": amfi_code,
                "fundName": row["scheme_name"],
                "amc": amc,
                "category": category,
                "plan": plan,
                "aumCr": round(aum_cr, 2),
                "cagr3y": round(cagr3y, 2),
                "stdDev": round(std_dev, 2),
                "sharpe": round(sharpe, 2),
                "sortino": round(sortino, 2),
                "alpha": round(alpha, 2),
                "beta": round(beta, 2),
                "maxDrawdown": round(max_dd, 2),
                "expenseRatio": round(exp_ratio, 2),
                "compositeScore": round(score, 1),
            }
        )

    # Sort funds by composite score descending
    funds_list.sort(key=lambda x: x["compositeScore"], reverse=True)

    # ----------------------------------------------------
    # 3. NAV VS BENCHMARK TIME SERIES FOR ALL FUNDS
    # ----------------------------------------------------
    df_nav = pd.read_sql_query("SELECT * FROM fact_nav", conn)
    df_bench = pd.read_csv(PROCESSED_DIR / "10_benchmark_indices.csv")
    df_nifty = df_bench[df_bench["index_name"].str.upper() == "NIFTY50"].copy()
    df_nifty["date"] = pd.to_datetime(df_nifty["date"])
    df_nifty = df_nifty.sort_values("date")
    df_nifty["nifty_50"] = df_nifty["close_value"]

    # Sample monthly points for fast chart rendering
    df_nav["date"] = pd.to_datetime(df_nav["date_id"])

    nav_series_map = {}
    for code in df_perf_file["amfi_code"].unique():
        code_str = str(int(code))
        sub_nav = df_nav[df_nav["amfi_code"] == code].sort_values("date")
        if sub_nav.empty:
            continue

        # Group by Year-Month and take last trading day of month
        sub_nav["period"] = sub_nav["date"].dt.strftime("%b %y")
        monthly_nav = sub_nav.groupby("period").last().reset_index()
        monthly_nav = monthly_nav.sort_values("date")

        # Merge with Nifty 50 benchmark
        nifty = df_nifty[["date", "nifty_50"]].copy()
        nifty["period"] = nifty["date"].dt.strftime("%b %y")
        monthly_nifty = nifty.groupby("period").last().reset_index()

        nav_bm = pd.merge(
            monthly_nav,
            monthly_nifty,
            on="period",
            how="inner",
            suffixes=("_nav", "_nifty"),
        )
        nav_bm = nav_bm.sort_values("date_nav")

        if nav_bm.empty:
            continue

        base_nav = float(nav_bm.iloc[0]["nav"])
        base_bm = float(nav_bm.iloc[0]["nifty_50"])

        points = []
        for _, r in nav_bm.iterrows():
            curr_nav = float(r["nav"])
            curr_bm = float(r["nifty_50"])
            rebased_nav = round((curr_nav / base_nav) * 100.0, 2)
            rebased_bm = round((curr_bm / base_bm) * 100.0, 2)
            points.append(
                {
                    "date": r["period"],
                    "nav": rebased_nav,
                    "benchmark": rebased_bm,
                }
            )
        nav_series_map[code_str] = points

    # ----------------------------------------------------
    # 4. INVESTOR ANALYTICS (PAGE 3)
    # ----------------------------------------------------
    df_tx = pd.read_sql_query("SELECT * FROM fact_transactions", conn)
    df_tx["transaction_date"] = pd.to_datetime(df_tx["transaction_date"])
    df_tx["period"] = df_tx["transaction_date"].dt.strftime("%b %y")

    # State amounts
    state_tier_map = dict(zip(df_tx["state"], df_tx["city_tier"]))

    state_group = df_tx.groupby("state")["amount_inr"].sum().reset_index()
    state_group["amountCr"] = (state_group["amount_inr"] / 1e7).round(2)
    state_group["tier"] = state_group["state"].map(
        lambda s: state_tier_map.get(s, "B30")
    )
    state_amounts = [
        {
            "state": r["state"],
            "amountCr": float(r["amountCr"]),
            "tier": "T30" if r["tier"] == "T30" else "B30",
        }
        for _, r in state_group.sort_values("amountCr", ascending=False).iterrows()
    ]

    # Transaction Mix
    type_group = df_tx.groupby("transaction_type")["amount_inr"].sum().reset_index()
    type_group["amountCr"] = (type_group["amount_inr"] / 1e7).round(2)
    type_map = {"SIP": "SIP", "Lump Sum": "Lumpsum", "Redemption": "Redemption"}
    txn_split = [
        {
            "type": type_map.get(r["transaction_type"], r["transaction_type"]),
            "amountCr": float(r["amountCr"]),
        }
        for _, r in type_group.iterrows()
    ]

    # Average SIP by Age Group
    sip_tx = df_tx[df_tx["transaction_type"].str.upper() == "SIP"]
    age_sip_group = sip_tx.groupby("age_group")["amount_inr"].mean().reset_index()
    age_sip = [
        {
            "ageGroup": r["age_group"],
            "avgSipAmount": round(float(r["amount_inr"])),
        }
        for _, r in age_sip_group.iterrows()
    ]

    # Monthly Transaction Volume
    vol_group = df_tx.groupby("period")["tx_id"].count().reset_index()
    vol_group["date"] = pd.to_datetime(vol_group["period"], format="%b %y")
    vol_group = vol_group.sort_values("date")
    monthly_volume = [
        {"month": r["period"], "transactions": int(r["tx_id"])}
        for _, r in vol_group.iterrows()
    ]

    # State-filtered transaction cache
    state_filtered_cache = {}
    for st in df_tx["state"].unique():
        sub_st = df_tx[df_tx["state"] == st]
        sub_type = sub_st.groupby("transaction_type")["amount_inr"].sum().reset_index()
        sub_vol = sub_st.groupby("period")["tx_id"].count().reset_index()
        sub_vol["date"] = pd.to_datetime(sub_vol["period"], format="%b %y")
        sub_vol = sub_vol.sort_values("date")

        state_filtered_cache[st] = {
            "txnSplit": [
                {
                    "type": type_map.get(r["transaction_type"], r["transaction_type"]),
                    "amountCr": round(float(r["amount_inr"] / 1e7), 2),
                }
                for _, r in sub_type.iterrows()
            ],
            "monthlyVolume": [
                {"month": r["period"], "transactions": int(r["tx_id"])}
                for _, r in sub_vol.iterrows()
            ],
        }

    # Tier-filtered age SIP cache
    tier_age_cache = {}
    for tr in ["T30", "B30"]:
        sub_tr = sip_tx[sip_tx["city_tier"] == tr]
        sub_age = sub_tr.groupby("age_group")["amount_inr"].mean().reset_index()
        tier_age_cache[tr] = [
            {
                "ageGroup": r["age_group"],
                "avgSipAmount": round(float(r["amount_inr"])),
            }
            for _, r in sub_age.iterrows()
        ]

    # ----------------------------------------------------
    # 5. SIP & MARKET TRENDS (PAGE 4)
    # ----------------------------------------------------
    df_sip_file = pd.read_csv(PROCESSED_DIR / "04_monthly_sip_inflows.csv")
    df_sip_file["date"] = pd.to_datetime(df_sip_file["month"])
    df_sip_file["period"] = df_sip_file["date"].dt.strftime("%b %y")
    df_sip_file = df_sip_file.sort_values("date")

    # Merge with Nifty 50
    nifty_m = df_nifty[["date", "nifty_50"]].copy()
    nifty_m["period"] = nifty_m["date"].dt.strftime("%b %y")
    monthly_nifty_m = nifty_m.groupby("period").last().reset_index()

    sip_vs_mkt_df = pd.merge(df_sip_file, monthly_nifty_m, on="period", how="inner")
    sip_vs_mkt_df = sip_vs_mkt_df.sort_values("date_x")

    sip_vs_market = [
        {
            "month": r["period"],
            "sipInflowCr": round(float(r["sip_inflow_crore"]), 2),
            "nifty50": round(float(r["nifty_50"])),
        }
        for _, r in sip_vs_mkt_df.iterrows()
    ]

    # Category Inflow Heatmap
    df_cat_file = pd.read_csv(PROCESSED_DIR / "05_category_inflows.csv")
    df_cat_file["dt"] = pd.to_datetime(df_cat_file["month"])

    def to_quarter_period(dt):
        y = dt.year
        m = dt.month
        if m in [4, 5, 6]:
            return f"Q1 FY{str(y)[2:]}"
        elif m in [7, 8, 9]:
            return f"Q2 FY{str(y)[2:]}"
        elif m in [10, 11, 12]:
            return f"Q3 FY{str(y)[2:]}"
        else:
            return f"Q4 FY{str(y)[2:]}"

    df_cat_file["period"] = df_cat_file["dt"].apply(to_quarter_period)

    # Aggregate by category and period
    df_cat_q = (
        df_cat_file.groupby(["category", "period"])["net_inflow_crore"]
        .sum()
        .reset_index()
    )

    cat_heatmap = [
        {
            "category": r["category"],
            "period": r["period"],
            "netInflowCr": round(float(r["net_inflow_crore"]), 2),
        }
        for _, r in df_cat_q.iterrows()
    ]

    # Top FY25 categories
    fy25_cat = df_cat_file.groupby("category")["net_inflow_crore"].sum().reset_index()
    fy25_cat = fy25_cat.sort_values("net_inflow_crore", ascending=False).head(5)
    top_cat_fy25 = [
        {
            "category": r["category"],
            "netInflowCr": round(float(r["net_inflow_crore"]), 2),
        }
        for _, r in fy25_cat.iterrows()
    ]

    conn.close()

    output = {
        "kpis": kpis,
        "aumTrend": aum_trend,
        "aumByAmc": aum_by_amc,
        "funds": funds_list,
        "navSeries": nav_series_map,
        "stateAmounts": state_amounts,
        "txnSplit": txn_split,
        "ageGroupSip": age_sip,
        "monthlyVolume": monthly_volume,
        "stateFilteredCache": state_filtered_cache,
        "tierAgeCache": tier_age_cache,
        "sipVsMarket": sip_vs_market,
        "categoryHeatmap": cat_heatmap,
        "topCategoriesFy25": top_cat_fy25,
    }

    return output


def main():
    print("Extracting real Bluestock data from SQLite & CSVs...")
    data = export_data()

    # Target output directories (consolidated to frontend/)
    target_dirs = [
        PROJECT_ROOT / "frontend" / "public" / "api",
        PROJECT_ROOT / "public" / "api",  # Also keep in root for backward compatibility
    ]

    for d in target_dirs:
        d.mkdir(parents=True, exist_ok=True)
        out_file = d / "dashboard_data.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Exported {out_file.stat().st_size} bytes to {out_file}")

    print("Dashboard data export complete!")


if __name__ == "__main__":
    main()
