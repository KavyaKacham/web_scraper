"""
exporter.py — Exports cleaned records to CSV files.
Handles directory creation and encoding consistently.
"""

import csv
import os
import logging
from config import OUTPUT_DIR

logger = logging.getLogger(__name__)


def _ensure_output_dir():
    """Creates the output directory if it doesn't already exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def export_books_csv(records: list[dict], filepath: str) -> None:
    """
    Writes cleaned book records to a CSV file.

    Columns: title, price_gbp, rating_stars, availability, page, url
    """
    _ensure_output_dir()

    if not records:
        logger.warning("No book records to export.")
        return

    fieldnames = ["title", "price_gbp", "rating_stars", "availability", "page", "url"]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

    logger.info(f"Books CSV saved → {os.path.abspath(filepath)}  ({len(records)} rows)")


def export_jobs_csv(records: list[dict], filepath: str) -> None:
    """
    Writes cleaned job records to a CSV file.

    Columns: title, company, location, date_posted, page
    """
    _ensure_output_dir()

    if not records:
        logger.warning("No job records to export.")
        return

    fieldnames = ["title", "company", "location", "date_posted", "page"]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

    logger.info(f"Jobs CSV saved → {os.path.abspath(filepath)}  ({len(records)} rows)")
