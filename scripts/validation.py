"""Data validation utilities for the Mutual Fund Ingestion pipeline.

This module provides checks for missing values, duplicate rows, empty columns,
invalid datatypes, and referential integrity across the financial datasets.
"""

import pandas as pd

from scripts.utils import setup_logging

logger = setup_logging("validation")


def check_missing_values(df: pd.DataFrame) -> dict[str, int]:
    """Identify columns with missing values and count them.

    Args:
        df: Input pandas DataFrame.

    Returns:
        Dict[str, int]: Mapping of column name to number of null values.
    """
    null_counts = df.isnull().sum()
    return null_counts[null_counts > 0].to_dict()


def check_duplicate_rows(df: pd.DataFrame) -> int:
    """Count duplicate rows in the DataFrame.

    Args:
        df: Input pandas DataFrame.

    Returns:
        int: Total count of duplicate rows.
    """
    return int(df.duplicated().sum())


def check_empty_columns(df: pd.DataFrame) -> list[str]:
    """Find columns that are entirely null/empty.

    Args:
        df: Input pandas DataFrame.

    Returns:
        List[str]: List of completely empty column names.
    """
    return [col for col in df.columns if df[col].isnull().all()]


def validate_referential_integrity(
    fund_master_df: pd.DataFrame, nav_history_df: pd.DataFrame
) -> list[int]:
    """Verify that all amfi_codes in fund_master exist in nav_history.

    Args:
        fund_master_df: The master fund scheme DataFrame.
        nav_history_df: Historical daily NAVs DataFrame.

    Returns:
        List[int]: List of amfi_codes present in master but missing in NAV history.
    """
    master_codes = set(fund_master_df["amfi_code"].unique())
    nav_codes = set(nav_history_df["amfi_code"].unique())
    missing_codes = list(master_codes - nav_codes)

    if missing_codes:
        logger.warning(
            f"Referential integrity failure: {len(missing_codes)} scheme codes from master "
            f"are missing in NAV history: {missing_codes}"
        )
    else:
        logger.info(
            "Referential integrity check passed: All master fund codes exist in NAV history."
        )

    return missing_codes
