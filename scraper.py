"""
scraper.py — Handles all HTTP requests with retry logic and exception handling.
Returns BeautifulSoup objects ready for parsing.
"""

import time
import random
import logging
import requests
from bs4 import BeautifulSoup
from config import HEADERS, TIMEOUT, MAX_RETRIES, REQUEST_DELAY

logger = logging.getLogger(__name__)


def fetch_page(url: str, session: requests.Session) -> BeautifulSoup | None:
    """
    Fetches a URL and returns a parsed BeautifulSoup object.

    Handles:
      - Connection errors
      - Timeouts
      - HTTP errors (4xx / 5xx)
      - Rate limiting (429) with a longer back-off wait
    Retries up to MAX_RETRIES times with exponential back-off.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"GET {url}  (attempt {attempt}/{MAX_RETRIES})")
            response = session.get(url, headers=HEADERS, timeout=TIMEOUT)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")

        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error on attempt {attempt}")

        except requests.exceptions.Timeout:
            logger.error(f"Request timed out on attempt {attempt}")

        except requests.exceptions.HTTPError as e:
            code = e.response.status_code
            if code == 429:
                logger.warning("Rate limited (429). Waiting 30 s …")
                time.sleep(30)
            elif code in (403, 404):
                logger.error(f"HTTP {code} — skipping {url}")
                return None
            else:
                logger.error(f"HTTP {code} on attempt {attempt}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Unexpected error: {e}")

        # Exponential back-off before next retry
        if attempt < MAX_RETRIES:
            wait = 2 ** attempt + random.uniform(0, 1)
            logger.info(f"Retrying in {wait:.1f} s …")
            time.sleep(wait)

    logger.error(f"All {MAX_RETRIES} attempts failed for {url}")
    return None


def polite_sleep():
    """Sleeps for a random duration between requests to avoid overloading the server."""
    delay = random.uniform(*REQUEST_DELAY)
    logger.debug(f"Sleeping {delay:.2f} s …")
    time.sleep(delay)


def make_session() -> requests.Session:
    """Creates and returns a reusable requests.Session."""
    session = requests.Session()
    session.headers.update(HEADERS)
    return session
