"""Unit tests for the Performance & Risk Analytics Engine (scripts/risk_metrics.py).

This test suite verifies mathematical accuracy, edge-case robustness, zero-divisiion safety,
and correct output data structures across all return, volatility, risk-adjusted ratio,
benchmark sensitivity, and concentration metrics.
"""

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

# Ensure scripts folder is on PATH
sys.path.append(str(Path(__file__).resolve().parent.parent / "scripts"))

from risk_metrics import (
    calculate_alpha,
    calculate_annual_returns,
    calculate_annualized_volatility,
    calculate_beta,
    calculate_cagr,
    calculate_calmar_ratio,
    calculate_daily_returns,
    calculate_diversification_score,
    calculate_downside_deviation,
    calculate_drawdown_duration,
    calculate_hhi,
    calculate_max_drawdown,
    calculate_monthly_returns,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_treynor_ratio,
    calculate_weekly_returns,
)


class TestRiskMetrics(unittest.TestCase):
    """Test suite for financial risk and return calculations."""

    def setUp(self):
        """Construct synthetic test time-series datasets."""
        # 252 days of steadily growing NAV (100 -> 120)
        self.dates = pd.date_range(start="2024-01-01", periods=252, freq="D")
        np.random.seed(42)
        noise = np.random.normal(0.0005, 0.01, 252)
        nav_values = 100.0 * np.cumprod(1.0 + noise)
        self.df_nav = pd.DataFrame({"date": self.dates, "nav": nav_values})
        self.nav_series = pd.Series(nav_values, index=self.dates)

    def test_calculate_daily_returns(self):
        """Verify daily percentage returns calculation."""
        returns = calculate_daily_returns(self.nav_series)
        self.assertEqual(len(returns), len(self.nav_series))
        self.assertEqual(returns.iloc[0], 0.0)
        self.assertFalse(returns.isnull().any())

    def test_calculate_weekly_and_monthly_returns(self):
        """Verify weekly, monthly, and annual aggregation."""
        df_weekly = calculate_weekly_returns(self.df_nav)
        self.assertFalse(df_weekly.empty)
        self.assertIn("weekly_return_pct", df_weekly.columns)

        df_monthly = calculate_monthly_returns(self.df_nav)
        self.assertFalse(df_monthly.empty)
        self.assertIn("monthly_return_pct", df_monthly.columns)

        df_annual = calculate_annual_returns(self.df_nav)
        self.assertFalse(df_annual.empty)
        self.assertIn("annual_return_pct", df_annual.columns)

    def test_calculate_cagr(self):
        """Verify CAGR formula against deterministic inputs."""
        dates = pd.Series([pd.Timestamp("2020-01-01"), pd.Timestamp("2022-01-01")])
        navs = pd.Series([100.0, 144.0])  # 20% CAGR over 2 years (1.2^2 = 1.44)
        cagr = calculate_cagr(navs, dates)
        self.assertAlmostEqual(cagr, 20.0, places=1)

    def test_cagr_edge_cases(self):
        """Verify CAGR edge cases handling."""
        self.assertEqual(calculate_cagr(pd.Series([]), pd.Series([])), 0.0)
        self.assertEqual(
            calculate_cagr(pd.Series([100.0]), pd.Series([pd.Timestamp("2020-01-01")])),
            0.0,
        )

    def test_volatility_and_downside_deviation(self):
        """Verify volatility and downside risk functions."""
        daily_ret = calculate_daily_returns(self.nav_series)
        vol = calculate_annualized_volatility(daily_ret)
        downside_dev = calculate_downside_deviation(daily_ret, risk_free_rate=0.06)

        self.assertGreater(vol, 0.0)
        self.assertGreaterEqual(downside_dev, 0.0)

    def test_max_drawdown_and_duration(self):
        """Verify max drawdown percentage and duration calculation."""
        navs = pd.Series([100.0, 120.0, 90.0, 95.0, 130.0])
        max_dd = calculate_max_drawdown(navs)
        self.assertAlmostEqual(max_dd, -25.0, places=1)

        duration = calculate_drawdown_duration(navs)
        self.assertEqual(duration, 2)  # Spent 2 days below 120.0 peak

    def test_beta_and_alpha(self):
        """Verify Beta and Alpha sensitivity metrics."""
        fund_ret = pd.Series([0.01, -0.02, 0.03, 0.015, -0.01])
        bench_ret = pd.Series([0.01, -0.015, 0.025, 0.01, -0.008])

        beta = calculate_beta(fund_ret, bench_ret)
        self.assertGreater(beta, 0.0)

        alpha = calculate_alpha(15.0, 10.0, beta=1.1, risk_free_rate_pct=6.0)
        # Expected Alpha = 15.0 - (6.0 + 1.1 * (10.0 - 6.0)) = 15.0 - (6.0 + 4.4) = 4.6
        self.assertAlmostEqual(alpha, 4.6, places=1)

    def test_risk_adjusted_ratios(self):
        """Verify Sharpe, Sortino, Treynor, and Calmar ratios."""
        sharpe = calculate_sharpe_ratio(
            cagr_fund_pct=16.0, volatility_pct=10.0, risk_free_rate_pct=6.0
        )
        self.assertAlmostEqual(sharpe, 1.0, places=2)

        sortino = calculate_sortino_ratio(
            cagr_fund_pct=16.0, downside_dev_pct=8.0, risk_free_rate_pct=6.0
        )
        self.assertAlmostEqual(sortino, 1.25, places=2)

        treynor = calculate_treynor_ratio(
            cagr_fund_pct=16.0, beta=1.0, risk_free_rate_pct=6.0
        )
        self.assertAlmostEqual(treynor, 10.0, places=2)

        calmar = calculate_calmar_ratio(cagr_fund_pct=15.0, max_drawdown_pct=-10.0)
        self.assertAlmostEqual(calmar, 1.5, places=2)

    def test_zero_division_safety(self):
        """Verify zero division safety across all ratios."""
        self.assertEqual(calculate_sharpe_ratio(10.0, 0.0), 0.0)
        self.assertEqual(calculate_sortino_ratio(10.0, 0.0), 0.0)
        self.assertEqual(calculate_treynor_ratio(10.0, 0.0), 0.0)
        self.assertEqual(calculate_calmar_ratio(10.0, 0.0), 0.0)

    def test_hhi_and_diversification_score(self):
        """Verify portfolio concentration HHI and diversification score."""
        weights = pd.Series([20.0, 20.0, 20.0, 20.0, 20.0])  # Equal weight 5 stocks
        hhi = calculate_hhi(weights)
        self.assertAlmostEqual(hhi, 2000.0, places=1)

        score = calculate_diversification_score(hhi, len(weights))
        self.assertAlmostEqual(score, 100.0, places=1)

    def test_ols_alpha_beta(self):
        """Verify OLS regression Alpha and Beta calculation using scipy.stats.linregress."""
        from risk_metrics import calculate_ols_alpha_beta

        bench_ret = pd.Series([0.01, -0.01, 0.02, -0.02, 0.015, -0.015])
        # fund = 1.2 * bench + 0.0005 daily excess
        fund_ret = 1.2 * bench_ret + 0.0005

        alpha_pct, beta, r_squared, _p_value = calculate_ols_alpha_beta(
            fund_ret, bench_ret, trading_days=252
        )
        self.assertAlmostEqual(beta, 1.2, places=2)
        self.assertAlmostEqual(alpha_pct, 0.0005 * 252 * 100.0, places=1)
        self.assertGreater(r_squared, 0.95)

    def test_tracking_error(self):
        """Verify annualized tracking error formula std(fund - bench) * sqrt(252)."""
        from risk_metrics import calculate_tracking_error

        fund_ret = pd.Series([0.01, 0.02, 0.01, 0.03, 0.02])
        bench_ret = pd.Series([0.008, 0.018, 0.012, 0.028, 0.022])
        te = calculate_tracking_error(fund_ret, bench_ret, trading_days=252)
        self.assertGreater(te, 0.0)

    def test_scorecard_weighting(self):
        """Verify scorecard 0-100 composite scoring logic and ranking directions."""
        from generate_performance_analytics import generate_task7_scorecard

        df_cagr = pd.DataFrame(
            {
                "amfi_code": [119551, 125497],
                "scheme_name": ["A", "B"],
                "category": ["Equity", "Equity"],
                "cagr_3yr_pct": [20.0, 10.0],  # Scheme 119551 > Scheme 125497
            }
        )
        df_sharpe = pd.DataFrame(
            {
                "amfi_code": [119551, 125497],
                "scheme_name": ["A", "B"],
                "category": ["Equity", "Equity"],
                "sharpe_ratio": [1.5, 0.5],  # Scheme 119551 > Scheme 125497
            }
        )
        df_ab = pd.DataFrame(
            {
                "amfi_code": [119551, 125497],
                "scheme_name": ["A", "B"],
                "alpha_pct": [5.0, 1.0],  # Scheme 119551 > Scheme 125497
            }
        )
        df_mdd = pd.DataFrame(
            {
                "amfi_code": [119551, 125497],
                "scheme_name": ["A", "B"],
                "max_drawdown_pct": [
                    -10.0,
                    -25.0,
                ],  # Scheme 119551 better (less negative)
            }
        )
        # Scheme 119551 dominates on return, sharpe, alpha, max_dd
        df_score = generate_task7_scorecard(df_cagr, df_sharpe, df_ab, df_mdd)
        self.assertGreater(len(df_score), 0)
        # 119551 should rank above 125497
        rank_119551 = df_score.loc[
            df_score["amfi_code"] == 119551, "final_rank"
        ].values[0]
        rank_125497 = df_score.loc[
            df_score["amfi_code"] == 125497, "final_rank"
        ].values[0]
        self.assertLess(rank_119551, rank_125497)


if __name__ == "__main__":
    unittest.main()
