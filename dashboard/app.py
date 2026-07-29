"""Bluestock Mutual Fund Analytics Platform - Interactive Dashboard App.

Main Streamlit application entry point featuring custom Bluestock Fintech branding,
multi-page navigation, and SQLite database connectivity.
"""

import sqlite3
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "mutual_fund_analytics.db"

st.set_page_config(
    page_title="Bluestock Fintech - Mutual Fund Analytics Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS Theme
st.markdown(
    """
<style>
    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        color: #0A2540;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #637381;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8F9FA;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #0066FF;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""",
    unsafe_allow_html=True,
)


def get_db_connection():
    """Create SQLite connection."""
    return sqlite3.connect(DATABASE_PATH)


def main():
    """Render Dashboard Overview Home Page."""
    (
        st.sidebar.image("https://bluestock.in/assets/images/logo.png", width=200)
        if False
        else None
    )
    st.sidebar.markdown("## 📈 Navigation")
    st.sidebar.info("Select a dashboard page above to explore Mutual Fund Insights.")

    st.markdown(
        '<div class="main-title">Bluestock Fintech - Mutual Fund Analytics Platform</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sub-title">Production Data Engineering, ETL Pipeline & BI Dashboard (Bluestock Capstone)</div>',
        unsafe_allow_html=True,
    )

    conn = get_db_connection()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Industry AUM", "₹81.00 Lakh Cr", delta="Dec 2025 Peak")
    with col2:
        st.metric("Monthly SIP Inflow", "₹31,002 Cr", delta="All-Time High")
    with col3:
        st.metric("Total Folio Count", "26.12 Crore", delta="+9.6% YoY")
    with col4:
        st.metric("Tracked Schemes", "40 Real Schemes", delta="Top AMCs")

    st.markdown("---")
    st.markdown("### 📊 Dashboard Page Guide")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("1. Industry Overview")
        st.write(
            "Monitors macro trends, overall AUM growth across top 10 AMCs, and monthly SIP velocity."
        )

        st.subheader("2. Fund Performance & Risk")
        st.write(
            "Interactive risk-return scatter plots, fund scorecard tables, and scheme vs benchmark NAV comparisons."
        )

    with c2:
        st.subheader("3. Investor Analytics")
        st.write(
            "Demographic insights, state-wise transaction heatmaps, SIP vs Lumpsum splits, and age group distributions."
        )

        st.subheader("4. SIP & Market Trends")
        st.write(
            "Dual-axis SIP inflow against Nifty 50 trends, month-wise category inflow heatmaps, and YoY growth metrics."
        )

    conn.close()


if __name__ == "__main__":
    main()
