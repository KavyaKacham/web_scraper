"""
main.py — Entry point for the Smart Web Scraper & Data Extraction Tool.

Pipeline:
  1. Scrape  →  scraper.py  (HTTP requests + retry/error handling)
  2. Parse   →  parser.py   (BeautifulSoup HTML extraction)
  3. Clean   →  cleaner.py  (normalise, deduplicate, validate)
  4. Export  →  exporter.py (write CSV files)
  5. Analyse →  analyzer.py (summary statistics)
  6. Report  →  report.py   (generate HTML report)

Sites:
  books.toscrape.com          — 1000 books across 50 pages
  realpython.github.io/fake-jobs — job listings (single page demo)
"""

import os
import logging
from datetime import datetime

# ── Local modules ────────────────────────────────────────────────────────────
from config   import BOOKS_START_URL, JOBS_START_URL, BOOKS_CSV, JOBS_CSV, REPORT_HTML
from scraper  import fetch_page, polite_sleep, make_session
from parser   import parse_books_page, get_books_next_url, parse_jobs_page
from cleaner  import clean_books, clean_jobs
from exporter import export_books_csv, export_jobs_csv
from analyzer import analyze_books, analyze_jobs
from report   import generate_html_report

# ── Logging setup ────────────────────────────────────────────────────────────
os.makedirs("output", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("output/scraper.log"),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
def scrape_books(session) -> list[dict]:
    """Paginates through all catalogue pages and returns raw book records."""
    raw_books   = []
    current_url = BOOKS_START_URL
    page        = 1

    while current_url:
        soup = fetch_page(current_url, session)
        if soup is None:
            logger.error(f"Stopping books scrape — failed to load page {page}")
            break

        page_records = parse_books_page(soup, page)
        raw_books.extend(page_records)
        logger.info(f"[Books] Page {page:>3} → {len(page_records):>2} records | Total: {len(raw_books)}")

        current_url = get_books_next_url(soup)
        page += 1
        polite_sleep()

    return raw_books


def scrape_jobs(session) -> list[dict]:
    """Scrapes the fake-jobs page (single page for demo; extend for paginated sites)."""
    raw_jobs = []
    soup = fetch_page(JOBS_START_URL, session)
    if soup is None:
        logger.error("Failed to load jobs page.")
        return raw_jobs

    raw_jobs = parse_jobs_page(soup, page_number=1)
    logger.info(f"[Jobs] Page 1 → {len(raw_jobs)} records")
    return raw_jobs


# ─────────────────────────────────────────────────────────────────────────────
def main():
    start_time = datetime.now()
    print("\n" + "═" * 60)
    print("  🕷️  Smart Web Scraper & Data Extraction Tool")
    print(f"  Started : {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 60 + "\n")

    session = make_session()

    # ── BOOKS pipeline ───────────────────────────────────────────────────────
    logger.info("━━━ STEP 1/6 : Scraping books ━━━")
    raw_books = scrape_books(session)

    logger.info("━━━ STEP 2/6 : Cleaning books ━━━")
    clean_books_data = clean_books(raw_books)

    logger.info("━━━ STEP 3/6 : Exporting books CSV ━━━")
    export_books_csv(clean_books_data, BOOKS_CSV)

    # ── JOBS pipeline ────────────────────────────────────────────────────────
    logger.info("━━━ STEP 4/6 : Scraping jobs ━━━")
    raw_jobs = scrape_jobs(session)

    logger.info("━━━ STEP 5/6 : Cleaning & exporting jobs CSV ━━━")
    clean_jobs_data = clean_jobs(raw_jobs)
    export_jobs_csv(clean_jobs_data, JOBS_CSV)

    # ── Analysis & Report ────────────────────────────────────────────────────
    logger.info("━━━ STEP 6/6 : Analysing data & generating report ━━━")
    books_stats = analyze_books(clean_books_data)
    jobs_stats  = analyze_jobs(clean_jobs_data)
    generate_html_report(books_stats, jobs_stats, REPORT_HTML)

    session.close()

    # ── Final summary ────────────────────────────────────────────────────────
    elapsed = (datetime.now() - start_time).seconds
    print("\n" + "═" * 60)
    print("  ✅  SCRAPING COMPLETE")
    print("═" * 60)
    print(f"  Books extracted  : {books_stats.get('total', 0):,}")
    print(f"  Pages scraped    : {books_stats.get('pages_scraped', 0)}")
    print(f"  Avg book price   : £{books_stats.get('avg_price', 0):.2f}")
    print(f"  Avg book rating  : {books_stats.get('avg_rating', 0):.1f} ★")
    print(f"  Jobs extracted   : {jobs_stats.get('total', 0):,}")
    print(f"  Time elapsed     : {elapsed}s")
    print(f"  Books CSV        : {BOOKS_CSV}")
    print(f"  Jobs CSV         : {JOBS_CSV}")
    print(f"  HTML Report      : {REPORT_HTML}")
    print("═" * 60 + "\n")


if __name__ == "__main__":
    main()
