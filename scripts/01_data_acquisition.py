
"""
Project: BRCA1 MAVE Analysis
Module: Data Acquisition
Purpose: Download BRCA1 functional variant scores from MaveDB.
"""

from pathlib import Path
import requests
import pandas as pd

# Dataset information
BASE_URL = "https://api.mavedb.org/api/v1"
DATASET_URN = "urn:mavedb:00000003-a-1"

# Project directories
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

def download_score_set(urn):
    """Retrieve score set metadata and variant scores from MaveDB."""

    metadata_url = f"{BASE_URL}/score-sets/{urn}"
    scores_url = f"{BASE_URL}/score-sets/{urn}/scores"

    print("Retrieving dataset metadata...")

    metadata_response = requests.get(
        metadata_url, timeout=60
    )
    metadata_response.raise_for_status()
    metadata = metadata_response.json()

    print("Dataset title:", metadata.get("title"))
    print("Reported number of variants:", metadata.get("numVariants"))

    print("Downloading variant scores...")

    scores_response = requests.get(
        scores_url, timeout=120
    )
    scores_response.raise_for_status()

    output_file = RAW_DATA_DIR / "BRCA1_E3_scores.csv"
    output_file.write_text(
        scores_response.text, encoding="utf-8"
    )

    data = pd.read_csv(output_file)

    print("\nDownload completed successfully.")
    print("Number of rows:", len(data))
    print("Number of columns:", len(data.columns))
    print("Available columns:", data.columns.tolist())
    print("Saved to:", output_file)

    return data


if __name__ == "__main__":
    brca1_data = download_score_set(DATASET_URN)
