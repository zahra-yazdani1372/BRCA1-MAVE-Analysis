
"""
Project: BRCA1 MAVE Analysis
Module: Data Validation
Purpose: Assess the quality and structure of raw BRCA1 MAVE data.
"""

from pathlib import Path

import numpy as np
import pandas as pd


# Define project directories
PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "BRCA1_E3_scores.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "results" / "tables"


def validate_data():
    """Generate a data quality report."""

    # Check whether the input dataset exists
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input dataset not found: {INPUT_FILE}"
        )

    # Load the raw dataset
    data = pd.read_csv(INPUT_FILE)

    print("Dataset loaded successfully.")
    print("Total rows:", len(data))
    print("Total columns:", len(data.columns))

    # Check required columns
    required_columns = [
        "accession",
        "hgvs_nt",
        "hgvs_pro",
        "score"
    ]

    missing_required = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_required:
        raise ValueError(
            f"Required columns are missing: {missing_required}"
        )

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate column-level quality report
    report = []

    for column in data.columns:

        values = data[column]

        row = {
            "column": column,
            "data_type": str(values.dtype),
            "non_missing": int(values.notna().sum()),
            "missing": int(values.isna().sum()),
            "missing_percent": round(
                values.isna().mean() * 100, 2
            ),
            "unique_values": int(values.nunique())
        }

        if pd.api.types.is_numeric_dtype(values):

            numeric_values = values.dropna()

            row["minimum"] = (
                numeric_values.min()
                if len(numeric_values) > 0
                else None
            )

            row["median"] = (
                numeric_values.median()
                if len(numeric_values) > 0
                else None
            )

            row["maximum"] = (
                numeric_values.max()
                if len(numeric_values) > 0
                else None
            )

            row["infinite_values"] = int(
                np.isinf(numeric_values).sum()
            )

        else:
            row["minimum"] = None
            row["median"] = None
            row["maximum"] = None
            row["infinite_values"] = None

        report.append(row)

    report_df = pd.DataFrame(report)

    # Save column-level report
    report_file = OUTPUT_DIR / "data_quality_report.csv"

    report_df.to_csv(
        report_file,
        index=False
    )

    # Calculate dataset-level statistics
    duplicate_rows = int(data.duplicated().sum())

    missing_scores = int(
        data["score"].isna().sum()
    )

    available_scores = int(
        data["score"].notna().sum()
    )

    missing_splice = (
        int(data["hgvs_splice"].isna().sum())
        if "hgvs_splice" in data.columns
        else "Column not found"
    )

    # Create summary report
    summary = [
        "BRCA1 MAVE Data Quality Summary",
        "================================",
        f"Total rows: {len(data)}",
        f"Total columns: {len(data.columns)}",
        f"Duplicate rows: {duplicate_rows}",
        f"Rows with missing primary scores: {missing_scores}",
        f"Rows with available primary scores: {available_scores}",
        f"Missing hgvs_splice values: {missing_splice}",
        "",
        "No rows have been removed during validation."
    ]

    summary_file = OUTPUT_DIR / "data_quality_summary.txt"

    summary_file.write_text(
        "\n".join(summary),
        encoding="utf-8"
    )

    # Display results
    print("\nData validation completed successfully.")
    print("Duplicate rows:", duplicate_rows)
    print("Missing scores:", missing_scores)
    print("Available scores:", available_scores)
    print("Quality report:", report_file)
    print("Summary report:", summary_file)


if __name__ == "__main__":
    validate_data()
