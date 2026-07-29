"""Dashboard Page 1 - Industry Overview."""

import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATABASE_PATH = PROJECT_ROOT / "mutual_fund_analytics.db"

st.set_page_config(page_title="Industry Overview - Bluestock MF", layout="wide")

st.title("🏛️ Day 5 Page 1: Industry Overview")
st.caption(
    "Macro Industry AUM Growth, Fund House Dominance & Monthly SIP Inflow Velocity"
)

conn = sqlite3.connect(DATABASE_PATH)

# Top KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Industry AUM", "₹81.00 Lakh Cr", "Dec 2025")
col2.metric("Monthly SIP Inflow", "₹31,002 Cr", "All-Time High")
col3.metric("Total Folios", "26.12 Crore", "+9.6% YoY")
col4.metric("Industry Schemes", "1,908 Schemes", "Active AMFI")

st.markdown("---")

# Row 1: Line Chart (Industry AUM) & Bar Chart (Top AMCs)
r1_col1, r1_col2 = st.columns(2)

with r1_col1:
    st.subheader("Industry AUM Growth (2022 - 2025)")
    df_aum = pd.read_sql_query(
        "SELECT date_id as Date, SUM(aum_crore) as Total_AUM FROM fact_aum GROUP BY date_id ORDER BY date_id ASC",
        conn,
    )
    fig_aum = px.line(
        df_aum,
        x="Date",
        y="Total_AUM",
        labels={"Total_AUM": "AUM (Rs. Crore)"},
        markers=True,
        title="Quarterly Industry AUM Trend",
    )
    fig_aum.update_traces(line_color="#0066FF", linewidth=3)
    st.plotly_chart(fig_aum, use_container_width=True)

with r1_col2:
    st.subheader("AUM by Fund House (Top 10 AMCs)")
    df_amc = pd.read_sql_query(
        "SELECT fund_house, SUM(aum_crore) as AUM FROM fact_aum GROUP BY fund_house ORDER BY AUM DESC LIMIT 10",
        conn,
    )
    fig_amc = px.bar(
        df_amc,
        x="AUM",
        y="fund_house",
        orientation="h",
        labels={"AUM": "AUM (Rs. Crore)"},
        title="Top 10 AMC Market Share",
    )
    fig_amc.update_traces(marker_color="#0A2540")
    st.plotly_chart(fig_amc, use_container_width=True)

conn.close()
