"""
analyzer.py — Computes summary statistics from cleaned records.
Results are used by report.py to build the HTML report.
"""

import logging
from collections import Counter

logger = logging.getLogger(__name__)


# ─── Books Analysis ───────────────────────────────────────────────────────────

def analyze_books(records: list[dict]) -> dict:
    """
    Returns a stats dictionary for book records:
      total, pages_scraped, avg_price, min_price, max_price,
      avg_rating, in_stock_count, rating_distribution,
      top_rated (list), cheapest (list), most_expensive (list)
    """
    if not records:
        return {}

    prices  = [r["price_gbp"]    for r in records]
    ratings = [r["rating_stars"] for r in records]
    in_stock = [r for r in records if "In stock" in r.get("availability", "")]

    rating_dist = dict(sorted(Counter(ratings).items()))

    top_rated = sorted(records, key=lambda r: (-r["rating_stars"], r["price_gbp"]))[:5]
    cheapest  = sorted(records, key=lambda r: r["price_gbp"])[:5]
    priciest  = sorted(records, key=lambda r: -r["price_gbp"])[:5]

    stats = {
        "total":              len(records),
        "pages_scraped":      max(r["page"] for r in records),
        "avg_price":          round(sum(prices) / len(prices), 2),
        "min_price":          round(min(prices), 2),
        "max_price":          round(max(prices), 2),
        "avg_rating":         round(sum(ratings) / len(ratings), 2),
        "in_stock_count":     len(in_stock),
        "rating_distribution": rating_dist,
        "top_rated":          top_rated,
        "cheapest":           cheapest,
        "most_expensive":     priciest,
    }

    logger.info(
        f"Books analysis — {stats['total']} records, "
        f"avg price £{stats['avg_price']}, avg rating {stats['avg_rating']}★"
    )
    return stats


# ─── Jobs Analysis ────────────────────────────────────────────────────────────

def analyze_jobs(records: list[dict]) -> dict:
    """
    Returns a stats dictionary for job records:
      total, pages_scraped, top_companies, top_locations,
      recent_postings (list)
    """
    if not records:
        return {}

    company_counts  = Counter(r["company"]  for r in records)
    location_counts = Counter(r["location"] for r in records)

    # Most recent by date string (ISO format sorts correctly)
    recent = sorted(records, key=lambda r: r.get("date_posted", ""), reverse=True)[:5]

    stats = {
        "total":          len(records),
        "pages_scraped":  max(r["page"] for r in records),
        "top_companies":  company_counts.most_common(5),
        "top_locations":  location_counts.most_common(5),
        "recent_postings": recent,
    }

    logger.info(
        f"Jobs analysis — {stats['total']} records, "
        f"{len(company_counts)} unique companies"
    )
    return stats
