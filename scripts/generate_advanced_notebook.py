"""Script to construct and execute notebooks/05_advanced_analytics.ipynb for Day 6."""

import json
from pathlib import Path

PROJECT_ROOT = Path("/Users/ruthvikgoud/Music/mutual-fund-analytics-Bluestock")
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
NOTEBOOKS_DIR.mkdir(exist_ok=True)

cells = []

# Title
cells.append(
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# Day 6: Advanced Analytics & Risk Metrics\n",
            "This notebook implements Day 6 tasks from the Bluestock Capstone Handbook:\n",
            "- 95% Historical Value at Risk (VaR) & Conditional VaR (CVaR)\n",
            "- Investor Cohort Analysis by initial transaction year\n",
            "- SIP Continuation Analysis flagging at-risk investors (>35 days gap)\n",
            "- Multi-Factor Fund Recommendation Model\n",
            "- Sector Concentration Analysis (Herfindahl-Hirschman Index - HHI)",
        ],
    }
)

# Environment Setup
cells.append(
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import sys\n",
            "import sqlite3\n",
            "import pandas as pd\n",
            "import numpy as np\n",
            "import matplotlib.pyplot as plt\n",
            "import seaborn as sns\n",
            "from IPython.display import display, Image\n",
            "\n",
            "sys.path.append('../scripts')\n",
            "\n",
            "from cohort_analysis import (\n",
            "    run_cohort_analysis,\n",
            "    run_sip_continuation_analysis,\n",
            "    run_sector_hhi_analysis,\n",
            "    run_var_cvar_analysis\n",
            ")\n",
            "from recommender import recommend_funds, print_recommendations\n",
            "\n",
            "sns.set_theme(style='whitegrid')\n",
            "print('Advanced Analytics Environment Initialized.')",
        ],
    }
)

# Section 1: VaR & CVaR
cells.append(
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 1. Value at Risk (VaR) and Conditional VaR (CVaR)\n",
            "Historical 95% VaR measures the 5th percentile worst daily return. CVaR (Expected Shortfall) measures the expected loss beyond the VaR threshold.",
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
            "conn = sqlite3.connect('../mutual_fund_analytics.db')\n",
            "df_var = run_var_cvar_analysis(conn)\n",
            "display(df_var.sort_values('var_95_pct', ascending=True).head(10))",
        ],
    }
)

# Section 2: Rolling Sharpe Ratio
cells.append(
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 2. 90-Day Rolling Sharpe Ratio Time Series\n",
            "Evaluating rolling risk-adjusted performance dynamics.",
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
            "display(Image(filename='../figures/risk_metrics/02_rolling_sharpe.png'))"
        ],
    }
)

# Section 3: Cohort & Continuity Analysis
cells.append(
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 3. Investor Cohorts & SIP Continuation Analysis\n",
            "Tracking investor retention and identifying at-risk accounts with inter-transaction gaps > 35 days.",
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
            "df_cohort = run_cohort_analysis(conn)\n",
            "display(df_cohort)\n",
            "\n",
            "df_continuity = run_sip_continuation_analysis(conn)\n",
            "print(f'Total Active SIP Investors Evaluated: {len(df_continuity)}')\n",
            'print(f\'At-Risk Investors Flagged (>35 days gap): {len(df_continuity[df_continuity["status"] == "at-risk"])}\')\n',
            "display(df_continuity.head(10))",
        ],
    }
)

# Section 4: Fund Recommendation Logic
cells.append(
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 4. Multi-Factor Fund Recommendation Model\n",
            "Recommending top 3 funds per risk category based on Sharpe ratio, CAGR, and downside risk.",
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
            "for risk_profile in ['Low', 'Moderate', 'High']:\n",
            "    print(f'=== Recommendations for {risk_profile} Risk Profile ===')\n",
            "    display(recommend_funds(risk_profile, top_n=3, db_path='../mutual_fund_analytics.db'))",
        ],
    }
)

# Section 5: Sector HHI Concentration
cells.append(
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 5. Sector Concentration Analysis (HHI)\n",
            "Evaluating Herfindahl-Hirschman Index (HHI) across fund portfolios.",
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
            "df_hhi = run_sector_hhi_analysis(conn)\n",
            "display(df_hhi.head(10))\n",
            "display(Image(filename='../figures/sector_hhi_chart.png'))\n",
            "conn.close()",
        ],
    }
)

notebook_content = {
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

with open(NOTEBOOKS_DIR / "05_advanced_analytics.ipynb", "w") as f:
    json.dump(notebook_content, f, indent=2)

print("Created notebooks/05_advanced_analytics.ipynb successfully.")
