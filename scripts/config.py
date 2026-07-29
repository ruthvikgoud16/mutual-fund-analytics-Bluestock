"""Configuration settings for the Mutual Fund Analytics Platform.

This module defines directory paths, external APIs, schema definitions, and list of
target schemes for live data fetching.
"""

from pathlib import Path

# Base Project Directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
LIVE_NAV_DIR = RAW_DATA_DIR / "live_nav"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Database Configuration
DATABASE_PATH = PROJECT_ROOT / "mutual_fund_analytics.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# External API Configuration
MFAPI_BASE_URL = "https://api.mfapi.in/mf"

# Target Scheme Codes for Live NAV Ingestion
TARGET_SCHEME_CODES: list[int] = [
    125497,  # HDFC Top 100 Fund - Direct - Growth
    119551,  # SBI Bluechip Fund
    120503,  # ICICI Prudential Bluechip Fund
    118632,  # Nippon India Large Cap Fund
    119092,  # Axis Bluechip Fund
    120841,  # Kotak Bluechip Fund
]
