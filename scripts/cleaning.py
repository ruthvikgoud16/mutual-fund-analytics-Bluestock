"""Module containing the data cleaning pipeline for Mutual Fund Analytics.

This module provides data cleaning, type conversion, category standardisation,
and specialized NAV holiday forward-filling methods.
"""

import pandas as pd

from scripts.utils import setup_logging

logger = setup_logging("cleaning")


def clean_dataframe(df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
    """Apply standard cleanings (deduplication, whitespace trimming, casing) to a DataFrame.

    Args:
        df: Input raw DataFrame.
        dataset_name: Identifier for logs.

    Returns:
        pd.DataFrame: Cleaned DataFrame.
    """
    logger.info(f"Starting standard cleaning for: {dataset_name}")
    cleaned_df = df.copy()

    # 1. Deduplication
    initial_rows = len(cleaned_df)
    cleaned_df = cleaned_df.drop_duplicates()
    dropped_dups = initial_rows - len(cleaned_df)
    if dropped_dups > 0:
        logger.info(f"Dropped {dropped_dups} duplicate rows from {dataset_name}.")

    # 2. String standardisation
    for col in cleaned_df.columns:
        if cleaned_df[col].dtype == "object":
            # Strip trailing/leading whitespace
            cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
            # If it's a code or indicator category, keep casing standardized
            if col in ["plan", "kyc_status", "transaction_type", "gender", "city_tier"]:
                cleaned_df[col] = cleaned_df[col].str.capitalize()

    return cleaned_df


def parse_and_validate_dates(df: pd.DataFrame, date_columns: list[str]) -> pd.DataFrame:
    """Format and validate date columns in a DataFrame.

    Args:
        df: Input DataFrame.
        date_columns: Column names to parse.

    Returns:
        pd.DataFrame: DataFrame with parsed date columns.
    """
    cleaned_df = df.copy()
    for col in date_columns:
        if col in cleaned_df.columns:
            # Parse to datetime
            cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors="coerce")
            # Log any rows with unparseable dates
            invalid_dates = cleaned_df[cleaned_df[col].isnull()]
            if not invalid_dates.empty:
                logger.warning(
                    f"Found {len(invalid_dates)} unparseable date values in column '{col}'."
                )
            # Standardize date output representation
            cleaned_df[col] = cleaned_df[col].dt.strftime("%Y-%m-%d")
    return cleaned_df


def clean_nav_history_gaps(nav_df: pd.DataFrame) -> pd.DataFrame:
    """Reindex daily NAV history and forward-fill weekend/holiday price gaps.

    Args:
        nav_df: Input historical daily NAV DataFrame.

    Returns:
        pd.DataFrame: Reindexed and forward-filled daily NAV DataFrame.
    """
    logger.info("Handling holiday and weekend gaps in NAV history...")
    cleaned_nav = nav_df.copy()

    # Ensure datatypes
    cleaned_nav["date"] = pd.to_datetime(cleaned_nav["date"])
    cleaned_nav["nav"] = pd.to_numeric(cleaned_nav["nav"], errors="coerce")

    # Process each scheme separately
    processed_list = []
    schemes = cleaned_nav["amfi_code"].unique()

    for scheme in schemes:
        scheme_df = cleaned_nav[cleaned_nav["amfi_code"] == scheme].copy()

        # Set date as index to allow reindexing
        scheme_df = scheme_df.set_index("date")

        # Generate full date range between min and max date for this scheme
        full_date_range = pd.date_range(
            start=scheme_df.index.min(), end=scheme_df.index.max(), freq="D"
        )

        # Reindex
        scheme_reindexed = scheme_df.reindex(full_date_range)
        scheme_reindexed.index.name = "date"

        # Populate constant amfi_code and forward-fill missing NAVs
        scheme_reindexed["amfi_code"] = scheme
        scheme_reindexed["nav"] = scheme_reindexed["nav"].ffill()

        # Reset index and restore date as a column
        scheme_final = scheme_reindexed.reset_index()
        processed_list.append(scheme_final)

    final_df = pd.concat(processed_list, ignore_index=True)
    # Format date back to string
    final_df["date"] = final_df["date"].dt.strftime("%Y-%m-%d")
    logger.info(
        f"NAV history gaps resolved. Expanded rows count from {len(nav_df)} to {len(final_df)}."
    )
    return final_df
