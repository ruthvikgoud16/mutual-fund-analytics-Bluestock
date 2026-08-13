"""Data Integrity Verification Test Suite for Integrated Bluestock Dashboard.

Validates that dashboard_data.json:
1. Contains exactly 40 schemes matching dim_fund and 07_scheme_performance.csv.
2. Matches SQLite KPI queries, AUM totals, SIP inflows, transaction totals, and metrics.
3. Contains 0 mock / dummy values in production data.
"""

import json
import sqlite3
import unittest
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "mutual_fund_analytics.db"
JSON_PATH = PROJECT_ROOT / "public" / "api" / "dashboard_data.json"


class TestDashboardIntegrity(unittest.TestCase):
    """Test suite for verifying end-to-end data integrity between SQLite and UI."""

    @classmethod
    def setUpClass(cls):
        cls.conn = sqlite3.connect(DB_PATH)
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            cls.data = json.load(f)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_scheme_count_and_mapping(self):
        """Verify exactly 40 schemes are loaded and mapped to AMFI codes."""
        df_funds = pd.read_sql_query("SELECT amfi_code FROM dim_fund", self.conn)
        self.assertEqual(len(self.data["funds"]), 40)
        self.assertEqual(len(df_funds), 40)

        json_amfi = {int(f["fundId"]) for f in self.data["funds"]}
        db_amfi = set(df_funds["amfi_code"].tolist())
        self.assertEqual(json_amfi, db_amfi)

    def test_kpi_values_match_database(self):
        """Verify industry KPIs match database queries."""
        kpis = self.data["kpis"]
        self.assertEqual(kpis["schemes"], 40)
        self.assertEqual(kpis["sipInflowCr"], 31002.0)
        self.assertEqual(kpis["foliosCr"], 26.12)

        # AUM total check
        df_perf = pd.read_csv(
            PROJECT_ROOT / "data" / "processed" / "07_scheme_performance.csv"
        )
        expected_aum = round(float(df_perf["aum_crore"].sum()), 2)
        self.assertEqual(kpis["totalAumCr"], expected_aum)

    def test_fund_performance_metrics_match(self):
        """Verify fund metrics in JSON match Phase 4 performance reports."""
        df_perf = pd.read_csv(
            PROJECT_ROOT / "data" / "processed" / "07_scheme_performance.csv"
        )
        sbi_bluechip = next(f for f in self.data["funds"] if f["fundId"] == "119551")
        db_row = df_perf[df_perf["amfi_code"] == 119551].iloc[0]

        self.assertEqual(
            sbi_bluechip["cagr3y"], round(float(db_row["return_3yr_pct"]), 2)
        )
        self.assertEqual(
            sbi_bluechip["sharpe"], round(float(db_row["sharpe_ratio"]), 2)
        )
        self.assertEqual(
            sbi_bluechip["maxDrawdown"], round(float(db_row["max_drawdown_pct"]), 2)
        )
        self.assertEqual(
            sbi_bluechip["expenseRatio"], round(float(db_row["expense_ratio_pct"]), 2)
        )

    def test_nav_series_rebased_and_aligned(self):
        """Verify NAV series exists for funds and is rebased to 100."""
        nav_map = self.data["navSeries"]
        self.assertIn("119551", nav_map)
        series = nav_map["119551"]
        self.assertGreater(len(series), 30)

        # Initial point rebased to 100
        self.assertEqual(series[0]["nav"], 100.0)
        self.assertEqual(series[0]["benchmark"], 100.0)

    def test_investor_analytics_totals(self):
        """Verify transaction totals match SQLite fact_transactions."""
        df_tx = pd.read_sql_query(
            "SELECT SUM(amount_inr)/1e7 as total_cr, COUNT(*) as tx_count FROM fact_transactions",
            self.conn,
        )
        db_total_cr = round(float(df_tx.iloc[0]["total_cr"]), 2)

        json_state_total = round(
            sum(s["amountCr"] for s in self.data["stateAmounts"]), 2
        )
        self.assertAlmostEqual(json_state_total, db_total_cr, delta=1.0)

        json_split_total = round(sum(s["amountCr"] for s in self.data["txnSplit"]), 2)
        self.assertAlmostEqual(json_split_total, db_total_cr, delta=1.0)

    def test_no_mock_data_labels(self):
        """Verify no mock/representative indicators remain in production export."""
        raw_text = json.dumps(self.data)
        self.assertNotIn("representative", raw_text.lower())
        self.assertNotIn("mock", raw_text.lower())
        self.assertNotIn("fake", raw_text.lower())


if __name__ == "__main__":
    unittest.main()
