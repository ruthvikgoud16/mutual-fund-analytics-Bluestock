"""Module to fetch live NAV values from mfapi.in API.

This module retrieves historical daily NAV data in JSON format for specified schemes,
validates the payload structure, and writes the results to raw CSV files.
"""

from pathlib import Path
from typing import Any

import pandas as pd
import requests

from scripts.config import LIVE_NAV_DIR, MFAPI_BASE_URL, TARGET_SCHEME_CODES
from scripts.utils import ensure_directory, setup_logging

logger = setup_logging("live_nav_fetch")


def fetch_scheme_nav(scheme_code: int) -> dict[str, Any]:
    """Retrieve raw historical NAV JSON from the mfapi.in REST API.

    Args:
        scheme_code: The target AMFI scheme code.

    Returns:
        Dict[str, Any]: The parsed JSON response.

    Raises:
        requests.RequestException: If the HTTP request fails.
        ValueError: If the response is not valid JSON.
    """
    url = f"{MFAPI_BASE_URL}/{scheme_code}"
    logger.info(f"Fetching live NAV data for scheme code: {scheme_code} from {url}")

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    data = response.json()
    if not isinstance(data, dict) or "data" not in data:
        raise ValueError(
            f"Invalid API response payload structure for scheme {scheme_code}."
        )

    return data


def save_nav_to_csv(
    api_response: dict[str, Any], scheme_code: int, output_dir: Path
) -> Path:
    """Parse JSON response and write NAV time-series rows to a CSV file.

    Args:
        api_response: The raw API dictionary payload.
        scheme_code: The AMFI scheme code.
        output_dir: Folder to write the CSV.

    Returns:
        Path: Path to the generated CSV file.
    """
    ensure_directory(output_dir)
    output_path = output_dir / f"{scheme_code}.csv"

    # Extract records and build DataFrame
    nav_records = api_response["data"]
    df = pd.DataFrame(nav_records)

    # Standardise date format (AMFI API returns DD-MM-YYYY, convert to YYYY-MM-DD)
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y").dt.strftime("%Y-%m-%d")
    df["nav"] = pd.to_numeric(df["nav"])

    # Sort chronologically
    df = df.sort_values("date").reset_index(drop=True)

    # Save target CSV
    df.to_csv(output_path, index=False)
    logger.info(f"Successfully saved {len(df)} NAV records to {output_path}")
    return output_path


def run_live_nav_ingestion(
    scheme_codes: list[int] = TARGET_SCHEME_CODES, output_dir: Path = LIVE_NAV_DIR
) -> None:
    """Loop through target schemes, fetch live data, and write to disk.

    Args:
        scheme_codes: List of AMFI codes to download.
        output_dir: Target output folder.
    """
    logger.info(f"Starting live NAV ingestion for {len(scheme_codes)} schemes...")
    for code in scheme_codes:
        try:
            payload = fetch_scheme_nav(code)
            save_nav_to_csv(payload, code, output_dir)
        except Exception:
            logger.exception(f"Failed to fetch or save NAV for scheme code {code}")
    logger.info("Live NAV ingestion run complete.")
