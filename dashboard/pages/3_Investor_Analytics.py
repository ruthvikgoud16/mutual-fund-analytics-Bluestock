"""Dashboard Page 3 - Investor Analytics."""

import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATABASE_PATH = PROJECT_ROOT / "mutual_fund_analytics.db"

st.set_page_config(page_title="Investor Analytics - Bluestock MF", layout="wide")

st.title("👥 Day 5 Page 3: Investor Analytics & Demographics")
st.caption("Geographic Heatmaps, Transaction Volume Splits & Behavioral Demographics")

conn = sqlite3.connect(DATABASE_PATH)

df_tx = pd.read_sql_query("SELECT * FROM fact_transactions", conn)

# Sidebar Filters
st.sidebar.header("Demographic Filters")
states = ["All"] + list(df_tx["state"].dropna().unique())
selected_state = st.sidebar.selectbox("Select State", states)

tiers = ["All"] + list(df_tx["city_tier"].dropna().unique())
selected_tier = st.sidebar.selectbox("Select City Tier", tiers)

df_filtered = df_tx.copy()
if selected_state != "All":
    df_filtered = df_filtered[df_filtered["state"] == selected_state]
if selected_tier != "All":
    df_filtered = df_filtered[df_filtered["city_tier"] == selected_tier]

# Row 1: State Bar & Donut Split
col1, col2 = st.columns(2)

with col1:
    st.subheader("Transaction Amount by State")
    df_state = (
        df_filtered.groupby("state")["amount_inr"]
        .sum()
        .reset_index()
        .sort_values("amount_inr", ascending=False)
    )
    fig_state = px.bar(
        df_state,
        x="amount_inr",
        y="state",
        orientation="h",
        labels={"amount_inr": "Total Amount (INR)"},
        title="State-wise Investment Volume",
    )
    fig_state.update_traces(marker_color="#0066FF")
    st.plotly_chart(fig_state, use_container_width=True)

with col2:
    st.subheader("Transaction Type Split")
    df_type = df_filtered.groupby("transaction_type")["amount_inr"].sum().reset_index()
    fig_donut = px.pie(
        df_type,
        values="amount_inr",
        names="transaction_type",
        hole=0.4,
        title="SIP vs Lumpsum vs Redemption",
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# Row 2: Age Group & Monthly Volume
col3, col4 = st.columns(2)

with col3:
    st.subheader("Average SIP Amount by Age Group")
    sip_df = df_filtered[df_filtered["transaction_type"].str.upper() == "SIP"]
    df_age = sip_df.groupby("age_group")["amount_inr"].mean().reset_index()
    fig_age = px.bar(
        df_age,
        x="age_group",
        y="amount_inr",
        labels={"amount_inr": "Avg SIP Amount (INR)"},
        title="Age Demographics vs SIP Amount",
    )
    st.plotly_chart(fig_age, use_container_width=True)

with col4:
    st.subheader("Monthly Transaction Volume Trend")
    df_filtered["month"] = (
        pd.to_datetime(df_filtered["transaction_date"]).dt.to_period("M").astype(str)
    )
    df_monthly = df_filtered.groupby("month")["amount_inr"].sum().reset_index()
    fig_monthly = px.line(
        df_monthly,
        x="month",
        y="amount_inr",
        title="Monthly Investor Transaction Volume",
    )
    st.plotly_chart(fig_monthly, use_container_width=True)

conn.close()
