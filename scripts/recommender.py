"""Fund Recommendation Engine module - Bluestock Mutual Fund Platform.

Implements Day 6 Task 5 from Bluestock Capstone Handbook:
- Input risk appetite: 'Low', 'Moderate', 'High'
- Matches input profile to fund's actual risk_category
- Ranks matching funds by actual Sharpe ratio
- Returns top 3 recommendations with CLI interface
"""

import argparse
import sqlite3
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path("/Users/ruthvikgoud/Music/mutual-fund-analytics-Bluestock")
sys.path.append(str(PROJECT_ROOT / "scripts"))

from config import DATABASE_PATH
from utils import setup_logging

logger = setup_logging("recommender")

# Risk Grade Mapping Matrix
RISK_MAPPING = {
    "LOW": ["Low", "Low to Moderate", "Moderate"],
    "MODERATE": ["Moderate", "Moderately High"],
    "HIGH": ["High", "Very High"],
}


def recommend_funds(
    risk_appetite: str = "Moderate", top_n: int = 3, db_path: Path = DATABASE_PATH
) -> pd.DataFrame:
    """Recommend top N funds based on investor risk appetite and Sharpe ratio.

    Args:
        risk_appetite: Investor risk profile ('Low', 'Moderate', 'High').
        top_n: Number of recommendations to return (default 3).
        db_path: Path to SQLite database.

    Returns:
        pd.DataFrame: Recommendation table with fund name, category, Sharpe ratio, and CAGR.
    """
    if not isinstance(risk_appetite, str) or not risk_appetite.strip():
        logger.warning("Invalid risk appetite string provided. Defaulting to Moderate.")
        risk_appetite = "Moderate"

    appetite_upper = risk_appetite.strip().upper()
    if appetite_upper not in RISK_MAPPING:
        logger.warning(
            f"Unrecognized risk appetite '{risk_appetite}'. Supported values: Low, Moderate, High. Defaulting to Moderate."
        )
        appetite_upper = "MODERATE"

    target_risk_levels = RISK_MAPPING[appetite_upper]

    if not Path(db_path).exists():
        logger.error(f"Database path not found: {db_path}")
        return pd.DataFrame()

    conn = sqlite3.connect(db_path)
    query = """
        SELECT r.amfi_code, f.scheme_name, f.category, f.fund_house, f.risk_category,
               r.sharpe_ratio, r.cagr_pct, r.volatility_ann_pct, r.sortino_ratio
        FROM fact_risk_metrics r
        JOIN dim_fund f ON r.amfi_code = f.amfi_code
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        logger.warning("No risk metrics found in database for recommendations.")
        return pd.DataFrame()

    # Filter matching risk categories
    df_filtered = df[df["risk_category"].isin(target_risk_levels)]
    if df_filtered.empty:
        logger.warning(
            f"No funds match risk categories {target_risk_levels}. Returning top funds overall."
        )
        df_filtered = df

    # Rank top N by Sharpe ratio
    df_recommended = (
        df_filtered.sort_values("sharpe_ratio", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    df_recommended["rank"] = df_recommended.index + 1

    cols_order = [
        "rank",
        "amfi_code",
        "scheme_name",
        "category",
        "risk_category",
        "sharpe_ratio",
        "cagr_pct",
        "volatility_ann_pct",
        "sortino_ratio",
    ]
    return df_recommended[cols_order]


def print_recommendations(risk_appetite: str = "Moderate", top_n: int = 3) -> None:
    """Format and print recommendation table to console."""
    print("\n==========================================")
    print(f" BLUESTOCK FUND RECOMMENDATIONS: {risk_appetite.upper()} RISK")
    print("==========================================")
    df_rec = recommend_funds(risk_appetite=risk_appetite, top_n=top_n)

    if df_rec.empty:
        print("No recommendations available.")
        return

    for _, row in df_rec.iterrows():
        print(f" Rank #{row['rank']}: {row['scheme_name']}")
        print(f"   - Category      : {row['category']} ({row['risk_category']})")
        print(f"   - Sharpe Ratio  : {row['sharpe_ratio']:.2f}")
        print(f"   - 3-Year CAGR   : {row['cagr_pct']:.2f}%")
        print(f"   - Volatility    : {row['volatility_ann_pct']:.2f}%")
        print(f"   - Sortino Ratio : {row['sortino_ratio']:.2f}\n")


def main():
    """CLI Entrypoint for Fund Recommender Engine."""
    parser = argparse.ArgumentParser(
        description="Bluestock Mutual Fund Recommender Engine"
    )
    parser.add_argument(
        "--risk",
        type=str,
        default="Moderate",
        choices=["Low", "Moderate", "High", "low", "moderate", "high"],
        help="Investor risk appetite profile (Low, Moderate, High)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=3,
        help="Number of top funds to recommend (default: 3)",
    )
    args = parser.parse_args()

    print_recommendations(risk_appetite=args.risk, top_n=args.top)


if __name__ == "__main__":
    main()
