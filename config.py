"""
config.py — Central configuration for the Smart Web Scraper project.
All settings live here; other modules import from this file.
"""

# ─── Target Sites ─────────────────────────────────────────────────────────────
BOOKS_BASE_URL  = "http://books.toscrape.com/catalogue/"
BOOKS_START_URL = "http://books.toscrape.com/catalogue/page-1.html"

JOBS_BASE_URL   = "https://realpython.github.io/fake-jobs/"
JOBS_START_URL  = "https://realpython.github.io/fake-jobs/"

# ─── HTTP Settings ────────────────────────────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
}

TIMEOUT      = 10          # seconds per request
MAX_RETRIES  = 3           # retry attempts on failure
REQUEST_DELAY = (1, 3)     # random sleep range between pages (seconds)

# ─── Output Paths ─────────────────────────────────────────────────────────────
OUTPUT_DIR       = "output"
BOOKS_CSV        = "output/books.csv"
JOBS_CSV         = "output/jobs.csv"
REPORT_HTML      = "output/report.html"

# ─── Misc ─────────────────────────────────────────────────────────────────────
RATING_MAP = {
    "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
}
