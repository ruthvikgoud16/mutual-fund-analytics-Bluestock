"""Unit tests for Day 6 Advanced Analytics modules.

Tests VaR/CVaR calculations, fund recommendation engine, and cohort analysis functions.
"""

import sqlite3
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent / "scripts"))

from cohort_analysis import run_var_cvar_analysis
from config import DATABASE_PATH
from recommender import recommend_funds
from risk_metrics import calculate_var_cvar


class TestAdvancedAnalytics(unittest.TestCase):
    """Test suite for advanced financial risk, recommendations, and cohorts."""

    def setUp(self):
        """Construct synthetic test return series."""
        np.random.seed(42)
        # Synthetic daily returns with known negative left tail
        self.returns = pd.Series(np.random.normal(0.0005, 0.015, 500))

    def test_calculate_var_cvar(self):
        """Verify 95% Historical VaR and CVaR calculations."""
        var_95, cvar_95 = calculate_var_cvar(self.returns, confidence_level=0.95)
        self.assertLess(var_95, 0.0)  # VaR threshold should be negative return %
        self.assertLessEqual(
            cvar_95, var_95
        )  # CVaR (Expected Shortfall) is worse/lower than VaR

    def test_var_cvar_edge_cases(self):
        """Verify VaR/CVaR handling for small or empty series."""
        var_empty, cvar_empty = calculate_var_cvar(pd.Series([]))
        self.assertEqual(var_empty, 0.0)
        self.assertEqual(cvar_empty, 0.0)

    def test_recommend_funds(self):
        """Verify multi-factor fund recommendation engine."""
        df_rec = recommend_funds(
            risk_appetite="Moderate", top_n=3, db_path=DATABASE_PATH
        )
        self.assertFalse(df_rec.empty)
        self.assertLessEqual(len(df_rec), 3)
        self.assertIn("sharpe_ratio", df_rec.columns)

    def test_run_var_cvar_analysis(self):
        """Verify database-backed VaR/CVaR report generation."""
        conn = sqlite3.connect(DATABASE_PATH)
        df_var_report = run_var_cvar_analysis(conn)
        conn.close()
        self.assertFalse(df_var_report.empty)
        self.assertIn("var_95_pct", df_var_report.columns)


if __name__ == "__main__":
    unittest.main()
