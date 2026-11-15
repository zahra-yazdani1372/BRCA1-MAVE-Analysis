
"""
Project: BRCA1 MAVE Analysis
Module: Statistical Analysis
Purpose: Perform descriptive statistical analysis and generate figures.
"""

from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# Define project directories
PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "BRCA1_E3_scores.csv"
TABLE_DIR = PROJECT_ROOT / "results" / "tables"
FIGURE_DIR = PROJECT_ROOT / "results" / "figures"

TABLE_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)


def main():

    print("Loading BRCA1 MAVE dataset...")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    data = pd.read_csv(INPUT_FILE)

    print("Dataset shape:", data.shape)

    # Identify numeric columns
    numeric_columns = data.select_dtypes(
        include=np.number
    ).columns.tolist()

    if not numeric_columns:
        raise ValueError(
            "No numeric columns were found in the dataset."
        )

    # Identify functional score columns
    score_columns = [
        column for column in numeric_columns
        if "score" in column.lower()
    ]

    if not score_columns:
        score_columns = numeric_columns

    print("Columns selected for analysis:", score_columns)

    # Generate descriptive statistics
    statistics = data[numeric_columns].describe().T

    statistics["missing_values"] = (
        data[numeric_columns].isna().sum()
    )

    statistics.to_csv(
        TABLE_DIR / "descriptive_statistics.csv"
    )

    # Generate data quality report
    quality_report = pd.DataFrame({
        "Metric": [
            "Number of rows",
            "Number of columns",
            "Duplicate rows",
            "Total missing values"
        ],
        "Value": [
            len(data),
            len(data.columns),
            int(data.duplicated().sum()),
            int(data.isna().sum().sum())
        ]
    })

    quality_report.to_csv(
        TABLE_DIR / "statistical_quality_report.csv",
        index=False
    )

    # Analyze functional score distributions
    for column in score_columns:

        values = data[column].dropna()

        if values.empty:
            continue

        # Histogram
        plt.figure(figsize=(8, 5))
        sns.histplot(values, kde=True)
        plt.title(f"Distribution of {column}")
        plt.xlabel(column)
        plt.ylabel("Frequency")
        plt.tight_layout()

        plt.savefig(
            FIGURE_DIR / f"{column}_distribution.png",
            dpi=300
        )
        plt.close()

        # Boxplot
        plt.figure(figsize=(8, 4))
        sns.boxplot(x=values)
        plt.title(f"Boxplot of {column}")
        plt.xlabel(column)
        plt.tight_layout()

        plt.savefig(
            FIGURE_DIR / f"{column}_boxplot.png",
            dpi=300
        )
        plt.close()

        # Calculate IQR-based outliers
        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outlier_count = int(
            ((values < lower_bound) |
             (values > upper_bound)).sum()
        )

        print(f"\nColumn: {column}")
        print("Mean:", values.mean())
        print("Median:", values.median())
        print("Standard deviation:", values.std())
        print("IQR-based outliers:", outlier_count)

    print("\nStatistical analysis completed.")
    print("Tables saved to:", TABLE_DIR)
    print("Figures saved to:", FIGURE_DIR)


if __name__ == "__main__":
    main()
