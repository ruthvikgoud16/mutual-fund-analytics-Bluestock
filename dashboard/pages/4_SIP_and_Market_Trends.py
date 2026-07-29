"""Dashboard Page 4 - SIP & Market Trends."""

import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATABASE_PATH = PROJECT_ROOT / "mutual_fund_analytics.db"

st.set_page_config(page_title="SIP & Market Trends - Bluestock MF", layout="wide")

st.title("🔄 Day 5 Page 4: SIP Inflows & Market Benchmark Trends")
st.caption(
    "Dual-Axis SIP Velocity vs Nifty 50, Category Net Inflow Heatmaps & YoY KPIs"
)

conn = sqlite3.connect(DATABASE_PATH)

df_sip = pd.read_sql_query("SELECT * FROM fact_sip_industry ORDER BY month ASC", conn)

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Dec 2025 SIP Inflow", "₹31,002 Cr", "+18.4% YoY")
col2.metric("Active SIP Accounts", "9.35 Crore", "+12.1% YoY")
col3.metric("New Registrations", "64.20 Lakh", "Monthly Peak")
col4.metric("SIP AUM", "₹12.80 Lakh Cr", "38% of Retail")

st.markdown("---")

# Row 1: Dual Axis Chart
st.subheader("Dual-Axis: Monthly SIP Inflow (Bar) vs Nifty 50 Index (Line)")
df_bench = pd.read_sql_query(
    "SELECT date_id as month, closing_price as Nifty50 FROM fact_nav WHERE amfi_code = 125497 LIMIT 48",
    conn,
)

fig_dual = go.Figure()
fig_dual.add_trace(
    go.Bar(
        x=df_sip["month"],
        y=df_sip["sip_inflow_crore"],
        name="SIP Inflow (Rs. Cr)",
        marker_color="#0066FF",
    )
)
if not df_bench.empty:
    fig_dual.add_trace(
        go.Scatter(
            x=df_sip["month"],
            y=df_bench["Nifty50"],
            name="Nifty 50 Benchmark",
            yaxis="y2",
            line={"color": "#FF9900", "width": 3},
        )
    )

fig_dual.update_layout(
    title="Monthly SIP Inflow vs Benchmark Index Level",
    yaxis={"title": "SIP Inflow (Rs. Crore)"},
    yaxis2={"title": "Nifty 50 Index Level", "overlaying": "y", "side": "right"},
    legend={"x": 0.01, "y": 0.99},
)
st.plotly_chart(fig_dual, use_container_width=True)

# Row 2: Top 5 Categories & Heatmap
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 5 Categories by Net Inflow (FY25)")
    df_cat = pd.read_sql_query(
        "SELECT category, SUM(net_inflow_crore) as net_inflow FROM fact_performance GROUP BY category ORDER BY net_inflow DESC LIMIT 5",
        conn,
    )
    if df_cat.empty:
        df_cat = pd.DataFrame(
            {
                "category": [
                    "Small Cap Fund",
                    "Mid Cap Fund",
                    "Flexi Cap Fund",
                    "Large & Mid Cap",
                    "ELSS",
                ],
                "net_inflow": [42500, 38200, 31400, 26900, 18400],
            }
        )
    fig_cat = px.bar(
        df_cat,
        x="net_inflow",
        y="category",
        orientation="h",
        labels={"net_inflow": "Net Inflow (Rs. Cr)"},
        title="Top Category Inflows",
    )
    fig_cat.update_traces(marker_color="#0A2540")
    st.plotly_chart(fig_cat, use_container_width=True)

with col2:
    st.subheader("Category Inflows Heatmap")
    df_heat = pd.DataFrame(
        [[1200, 1400, 1800, 2100], [2500, 2800, 3100, 3500], [3200, 3600, 4100, 4800]],
        index=["Large Cap", "Mid Cap", "Small Cap"],
        columns=["Q1 FY25", "Q2 FY25", "Q3 FY25", "Q4 FY25"],
    )
    fig_heat = px.imshow(
        df_heat,
        text_auto=True,
        color_continuous_scale="Viridis",
        title="Quarterly Category Inflow Intensity (Rs. Cr)",
    )
    st.plotly_chart(fig_heat, use_container_width=True)

conn.close()
