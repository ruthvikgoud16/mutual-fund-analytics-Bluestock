"""Dashboard Page 2 - Fund Performance."""

import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATABASE_PATH = PROJECT_ROOT / "mutual_fund_analytics.db"

st.set_page_config(page_title="Fund Performance - Bluestock MF", layout="wide")

st.title("📈 Day 5 Page 2: Fund Performance Analytics")
st.caption(
    "Risk-Return Quadrant, Sortable Fund Scorecard & Interactive NAV Benchmarking"
)

conn = sqlite3.connect(DATABASE_PATH)

# Fetch Data
query = """
    SELECT r.*, f.scheme_name, f.category, f.fund_house, f.plan
    FROM fact_risk_metrics r
    JOIN dim_fund f ON r.amfi_code = f.amfi_code
"""
df = pd.read_sql_query(query, conn)

# Sidebar Slicers
st.sidebar.header("Filter Options")
categories = ["All"] + list(df["category"].dropna().unique())
selected_cat = st.sidebar.selectbox("Select Category", categories)

amcs = ["All"] + list(df["fund_house"].dropna().unique())
selected_amc = st.sidebar.selectbox("Select Fund House", amcs)

df_filtered = df.copy()
if selected_cat != "All":
    df_filtered = df_filtered[df_filtered["category"] == selected_cat]
if selected_amc != "All":
    df_filtered = df_filtered[df_filtered["fund_house"] == selected_amc]

# Row 1: Scatter Plot
st.subheader("Risk vs Return Scatter Plot")
fig_scatter = px.scatter(
    df_filtered,
    x="volatility_ann_pct",
    y="cagr_pct",
    size="sharpe_ratio",
    color="category",
    hover_name="scheme_name",
    labels={
        "volatility_ann_pct": "Annualized Volatility (%)",
        "cagr_pct": "3-Year CAGR (%)",
    },
    title="Annualized Return (CAGR) vs Risk (Volatility)",
)
st.plotly_chart(fig_scatter, use_container_width=True)

# Row 2: Sortable Scorecard Table
st.subheader("Sortable Fund Scorecard Table")
cols_show = [
    "amfi_code",
    "scheme_name",
    "category",
    "fund_house",
    "cagr_pct",
    "volatility_ann_pct",
    "sharpe_ratio",
    "sortino_ratio",
    "alpha",
    "beta",
    "max_drawdown_pct",
]
st.dataframe(
    df_filtered[cols_show].sort_values("sharpe_ratio", ascending=False),
    use_container_width=True,
)

# Row 3: Interactive NAV Comparison
st.subheader("Interactive Scheme NAV Comparison")
selected_scheme = st.selectbox(
    "Select Scheme to Overlay NAV", df_filtered["scheme_name"].unique()
)

if selected_scheme:
    amfi_code = df_filtered[df_filtered["scheme_name"] == selected_scheme][
        "amfi_code"
    ].iloc[0]
    df_nav = pd.read_sql_query(
        f"SELECT date_id as Date, nav as Scheme_NAV FROM fact_nav WHERE amfi_code = {amfi_code} ORDER BY date_id ASC",
        conn,
    )
    fig_nav = px.line(
        df_nav,
        x="Date",
        y="Scheme_NAV",
        title=f"Historical NAV Movement - {selected_scheme}",
    )
    st.plotly_chart(fig_nav, use_container_width=True)

conn.close()
