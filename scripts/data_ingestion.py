"""Main orchestrator for Day 1 Data Ingestion and Validation.

This module automates CSV discovery, prints profile summaries, validates data quality
(missing values, duplicates, referential integrity), runs the live NAV fetch,
and generates a comprehensive markdown Data Quality Report.
"""

import sys
from pathlib import Path
from typing import Any

import pandas as pd

# Ensure scripts directory is in path
sys.path.append(str(Path(__file__).resolve().parent))

from scripts.config import RAW_DATA_DIR, REPORTS_DIR
from scripts.live_nav_fetch import run_live_nav_ingestion
from scripts.utils import ensure_directory, setup_logging
from scripts.validation import (
    check_duplicate_rows,
    check_empty_columns,
    check_missing_values,
    validate_referential_integrity,
)

logger = setup_logging("data_ingestion")


def discover_csv_files(directory: Path) -> list[Path]:
    """Find all CSV files in the raw data directory.

    Args:
        directory: Path to raw data folder.

    Returns:
        List[Path]: Sorted list of CSV file paths.
    """
    csv_files = sorted(directory.glob("*.csv"))
    logger.info(f"Discovered {len(csv_files)} CSV files in {directory}")
    return csv_files


def profile_and_validate_dataset(filepath: Path) -> dict[str, Any]:
    """Profile and run quality checks on a single CSV file.

    Args:
        filepath: Path to the target CSV file.

    Returns:
        Dict[str, Any]: Profile metrics and quality findings.
    """
    logger.info(f"Profiling dataset: {filepath.name}")
    df = pd.read_csv(filepath)

    # Basic profiling metrics
    shape = df.shape
    memory_usage = df.memory_usage(deep=True).sum() / (1024 * 1024)  # MB
    dtypes = df.dtypes.to_dict()

    # Prints per requirements
    print("\n" + "=" * 50)
    print(f"Dataset: {filepath.name}")
    print(f"Shape: {shape[0]} rows, {shape[1]} columns")
    print(f"Memory Usage: {memory_usage:.4f} MB")
    print("-" * 50)
    print("Datatypes:")
    for col, dtype in dtypes.items():
        print(f"  - {col}: {dtype}")
    print("-" * 50)
    print("Preview (Head):")
    print(df.head(2))
    print("=" * 50 + "\n")

    # Data Quality checks
    missing_vals = check_missing_values(df)
    duplicates = check_duplicate_rows(df)
    empty_cols = check_empty_columns(df)

    # Detect invalid numeric datatypes
    invalid_dtypes = {}
    for col in df.columns:
        # Check if the column is expected to be numeric
        is_expected_numeric = any(
            keyword in col.lower()
            for keyword in [
                "pct",
                "crore",
                "inr",
                "lakh",
                "nav",
                "close",
                "amount",
                "rating",
                "schemes",
            ]
        )
        if is_expected_numeric and not pd.api.types.is_numeric_dtype(df[col]):
            # Try to convert to numeric to confirm if it has non-numeric garbage characters
            converted = pd.to_numeric(df[col], errors="coerce")
            garbage_count = converted.isna().sum() - df[col].isna().sum()
            if garbage_count > 0:
                invalid_dtypes[col] = (
                    f"Expected numeric, but contains {garbage_count} non-numeric values."
                )

    return {
        "filename": filepath.name,
        "rows": shape[0],
        "cols": shape[1],
        "memory_mb": memory_usage,
        "missing_values": missing_vals,
        "duplicates": duplicates,
        "empty_columns": empty_cols,
        "invalid_dtypes": invalid_dtypes,
        "dataframe": df,
    }


def generate_quality_report(
    report_data: list[dict[str, Any]], referential_missing: list[int], output_dir: Path
) -> Path:
    """Compile and write a markdown Data Quality Report.

    Args:
        report_data: List of dictionaries containing metrics for each dataset.
        referential_missing: List of missing codes from the integrity check.
        output_dir: Folder to write the report.

    Returns:
        Path: Path to the generated report file.
    """
    ensure_directory(output_dir)
    report_path = output_dir / "data_quality_report.md"

    markdown_content = []
    markdown_content.append("# Mutual Fund Analytics - Data Quality Report\n")
    markdown_content.append(
        "This report summarizes the data profiling and quality metrics collected during the Day 1 Ingestion pipeline run.\n"
    )

    # 1. Summary Table
    markdown_content.append("## 1. Executive Summary Table\n")
    markdown_content.append(
        "| Dataset Name | Row Count | Column Count | Memory (MB) | Duplicate Rows | Null Columns | Quality Status |"
    )
    markdown_content.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

    for item in report_data:
        status = "🟢 Pass"
        if (
            item["missing_values"]
            or item["duplicates"]
            or item["empty_columns"]
            or item["invalid_dtypes"]
        ):
            status = "⚠️ Warnings"
        markdown_content.append(
            f"| {item['filename']} | {item['rows']} | {item['cols']} | {item['memory_mb']:.4f} | "
            f"{item['duplicates']} | {len(item['empty_columns'])} | {status} |"
        )
    markdown_content.append("\n")

    # 2. Referential Integrity Check
    markdown_content.append("## 2. Referential Integrity Check")
    if referential_missing:
        markdown_content.append(
            f"\n> [!WARNING]\n> Referential integrity check failed. The following {len(referential_missing)} AMFI scheme code(s) exist in `01_fund_master.csv` but are missing in `02_nav_history.csv`:\n> **{referential_missing}**\n"
        )
    else:
        markdown_content.append(
            "\n> [!NOTE]\n> Referential integrity check passed. All scheme codes in the fund master exist in the NAV history.\n"
        )

    # 3. Detailed Findings per Dataset
    markdown_content.append("## 3. Detailed Findings per Dataset\n")
    for item in report_data:
        markdown_content.append(f"### {item['filename']}")
        markdown_content.append(f"- **Row count:** {item['rows']}")
        markdown_content.append(f"- **Column count:** {item['cols']}")
        markdown_content.append(f"- **Duplicates detected:** {item['duplicates']}")

        # Missing values breakdown
        if item["missing_values"]:
            markdown_content.append("- **Null values detailed count:**")
            for col, count in item["missing_values"].items():
                markdown_content.append(f"  - `{col}`: {count} nulls")
        else:
            markdown_content.append("- **Null values detailed count:** None")

        # Empty columns
        if item["empty_columns"]:
            markdown_content.append(
                f"- **Completely empty columns:** {item['empty_columns']}"
            )

        # Invalid datatypes
        if item["invalid_dtypes"]:
            markdown_content.append("- **Datatype warnings:**")
            for col, warn in item["invalid_dtypes"].items():
                markdown_content.append(f"  - `{col}`: {warn}")
        else:
            markdown_content.append("- **Datatype warnings:** None")
        markdown_content.append("\n---")

    with open(report_path, "w") as f:
        f.write("\n".join(markdown_content))

    logger.info(f"Successfully generated Data Quality Report at {report_path}")
    return report_path


def main() -> None:
    """Orchestrate the ingestion, profiling, validation, and live fetch processes."""
    logger.info("Executing Day 1 ETL pipeline...")

    # 1. Discover CSV files
    csv_files = discover_csv_files(RAW_DATA_DIR)

    # 2 & 3 & 4. Load, profile, and run quality checks
    findings = []
    datasets = {}
    for csv_file in csv_files:
        try:
            finding = profile_and_validate_dataset(csv_file)
            findings.append(finding)
            # Store in datasets dictionary by file prefix (e.g. '01_fund_master')
            prefix = csv_file.name.split(".")[0]
            datasets[prefix] = finding["dataframe"]
        except Exception:
            logger.exception(f"Error loading and profiling {csv_file.name}")

    # 5. Referential Integrity Check
    referential_missing = []
    if "01_fund_master" in datasets and "02_nav_history" in datasets:
        referential_missing = validate_referential_integrity(
            datasets["01_fund_master"], datasets["02_nav_history"]
        )

    # 6. Generate Data Quality Report
    generate_quality_report(findings, referential_missing, REPORTS_DIR)

    # 7. Run Live NAV Ingestion
    try:
        run_live_nav_ingestion()
    except Exception:
        logger.exception("Live NAV Ingestion process failed")

    logger.info("Day 1 Ingestion Pipeline executed successfully.")


if __name__ == "__main__":
    main()
