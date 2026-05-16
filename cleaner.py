"""
cleaner.py — Cleans and normalises raw scraped records before export.
Each function takes a list of raw dicts and returns a cleaned list.
"""

import logging
import re

logger = logging.getLogger(__name__)


# ─── Books Cleaning ───────────────────────────────────────────────────────────

def clean_books(records: list[dict]) -> list[dict]:
    """
    Cleans raw book records:
      - Converts price string → float
      - Ensures rating is an int (0–5)
      - Strips whitespace from all string fields
      - Removes duplicate titles
      - Drops records with price == 0 (likely parse failures)
    """
    seen_titles = set()
    cleaned     = []

    for r in records:
        try:
            # Price: remove any stray characters, cast to float
            price_str = re.sub(r"[^\d.]", "", str(r.get("price_gbp", "0")))
            price = round(float(price_str), 2) if price_str else 0.0

            title = r.get("title", "").strip()

            # Skip duplicates and zero-price entries
            if not title or title in seen_titles or price == 0.0:
                continue

            seen_titles.add(title)

            cleaned.append({
                "title":        title,
                "price_gbp":    price,
                "rating_stars": int(r.get("rating_stars", 0)),
                "availability": r.get("availability", "Unknown").strip(),
                "page":         int(r.get("page", 0)),
                "url":          r.get("url", "N/A").strip(),
            })

        except (ValueError, TypeError) as e:
            logger.warning(f"Skipping uncleanable book record: {e}")

    logger.info(f"Books cleaned: {len(records)} raw → {len(cleaned)} clean records")
    return cleaned


# ─── Jobs Cleaning ────────────────────────────────────────────────────────────

def clean_jobs(records: list[dict]) -> list[dict]:
    """
    Cleans raw job records:
      - Strips whitespace from all string fields
      - Normalises location (title-case)
      - Removes duplicate title + company combinations
      - Drops records where both title and company are 'N/A'
    """
    seen     = set()
    cleaned  = []

    for r in records:
        try:
            title   = r.get("title",   "N/A").strip()
            company = r.get("company", "N/A").strip()
            location = r.get("location", "N/A").strip().title()
            date    = r.get("date_posted", "N/A").strip()

            key = (title.lower(), company.lower())

            if key in seen or (title == "N/A" and company == "N/A"):
                continue
            seen.add(key)

            cleaned.append({
                "title":       title,
                "company":     company,
                "location":    location,
                "date_posted": date,
                "page":        int(r.get("page", 0)),
            })

        except (ValueError, TypeError) as e:
            logger.warning(f"Skipping uncleanable job record: {e}")

    logger.info(f"Jobs cleaned: {len(records)} raw → {len(cleaned)} clean records")
    return cleaned
