"""
parser.py — Parses BeautifulSoup objects into structured Python dicts.
Contains separate parsers for each site (books, jobs).
"""

import logging
from config import BOOKS_BASE_URL, RATING_MAP

logger = logging.getLogger(__name__)


# ─── Books Parser (books.toscrape.com) ────────────────────────────────────────

def parse_book(article, page_number: int) -> dict | None:
    """
    Extracts structured data from a single <article class='product_pod'> element.

    Fields extracted:
      title, price_gbp, rating_stars, availability, page, url
    Returns None if the element is too malformed to parse.
    """
    try:
        # Title stored in the <a> tag's 'title' attribute (not inner text, which is truncated)
        title_tag = article.select_one("h3 a")
        title = title_tag["title"].strip() if title_tag else "N/A"

        # Price — strip pound sign and any encoding artefacts
        price_tag = article.select_one("p.price_color")
        price_raw = price_tag.get_text(strip=True) if price_tag else "0"
        price = price_raw.replace("£", "").replace("Â", "").strip()

        # Star rating encoded as a CSS class word: "One" … "Five"
        rating_tag = article.select_one("p.star-rating")
        rating_word = rating_tag["class"][1] if rating_tag else "Zero"
        rating = RATING_MAP.get(rating_word, 0)

        # Availability text
        avail_tag = article.select_one("p.availability")
        availability = avail_tag.get_text(strip=True) if avail_tag else "Unknown"

        # Build absolute URL from the relative href
        href = title_tag["href"].replace("../", "") if title_tag else ""
        url  = BOOKS_BASE_URL + href if href else "N/A"

        return {
            "title":        title,
            "price_gbp":    price,
            "rating_stars": rating,
            "availability": availability,
            "page":         page_number,
            "url":          url,
        }

    except (KeyError, TypeError, AttributeError) as e:
        logger.warning(f"Skipping malformed book element: {e}")
        return None


def parse_books_page(soup, page_number: int) -> list[dict]:
    """Parses all book cards on a single catalogue page."""
    articles = soup.select("article.product_pod")
    books = []
    for article in articles:
        book = parse_book(article, page_number)
        if book:
            books.append(book)
    return books


def get_books_next_url(soup) -> str | None:
    """Returns the absolute URL for the next catalogue page, or None if last page."""
    next_btn = soup.select_one("li.next a")
    if next_btn:
        href = next_btn["href"].replace("../", "")
        return BOOKS_BASE_URL + href
    return None


# ─── Jobs Parser (realpython.github.io/fake-jobs) ─────────────────────────────

def parse_job(card, page_number: int) -> dict | None:
    """
    Extracts structured data from a single job card element.

    Fields extracted:
      title, company, location, date_posted, page
    """
    try:
        title_tag   = card.select_one("h2.title")
        company_tag = card.select_one("h3.company")
        location_tag = card.select_one("p.location")
        date_tag    = card.select_one("time")

        title    = title_tag.get_text(strip=True)    if title_tag    else "N/A"
        company  = company_tag.get_text(strip=True)  if company_tag  else "N/A"
        location = location_tag.get_text(strip=True) if location_tag else "N/A"
        date     = date_tag["datetime"]              if date_tag     else "N/A"

        return {
            "title":       title,
            "company":     company,
            "location":    location,
            "date_posted": date,
            "page":        page_number,
        }

    except (KeyError, TypeError, AttributeError) as e:
        logger.warning(f"Skipping malformed job element: {e}")
        return None


def parse_jobs_page(soup, page_number: int) -> list[dict]:
    """Parses all job cards on a single jobs page."""
    cards = soup.select("div.card-content")
    jobs = []
    for card in cards:
        job = parse_job(card, page_number)
        if job:
            jobs.append(job)
    return jobs
