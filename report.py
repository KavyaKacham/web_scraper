"""
report.py — Generates a styled HTML report from analysis statistics.
Writes output/report.html summarising both books and jobs data.
"""

import os
import logging
from datetime import datetime
from config import OUTPUT_DIR

logger = logging.getLogger(__name__)


def _star_bar(rating: int) -> str:
    """Returns a Unicode star string for a given integer rating (0–5)."""
    return "★" * rating + "☆" * (5 - rating)


def _rows_books_top(books: list[dict]) -> str:
    rows = ""
    for b in books:
        rows += (
            f"<tr>"
            f"<td>{b['title'][:55]}{'…' if len(b['title'])>55 else ''}</td>"
            f"<td>£{b['price_gbp']:.2f}</td>"
            f"<td>{_star_bar(b['rating_stars'])}</td>"
            f"<td>{b['availability']}</td>"
            f"</tr>"
        )
    return rows


def _rows_jobs(jobs: list[dict]) -> str:
    rows = ""
    for j in jobs:
        rows += (
            f"<tr>"
            f"<td>{j['title']}</td>"
            f"<td>{j['company']}</td>"
            f"<td>{j['location']}</td>"
            f"<td>{j['date_posted']}</td>"
            f"</tr>"
        )
    return rows


def generate_html_report(
    books_stats: dict,
    jobs_stats:  dict,
    output_path: str,
) -> None:
    """
    Builds and writes a self-contained HTML report.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Rating distribution bars
    rating_bars = ""
    if books_stats:
        max_count = max(books_stats["rating_distribution"].values(), default=1)
        for stars, count in books_stats["rating_distribution"].items():
            pct = int((count / max_count) * 100)
            rating_bars += f"""
            <div class="bar-row">
              <span class="bar-label">{_star_bar(stars)}</span>
              <div class="bar-track"><div class="bar-fill" style="width:{pct}%"></div></div>
              <span class="bar-count">{count}</span>
            </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Web Scraper Report</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; }}
    header {{ background: linear-gradient(135deg,#1e3a5f,#0ea5e9); padding: 2rem 3rem; }}
    header h1 {{ font-size: 2rem; font-weight: 700; letter-spacing: 1px; }}
    header p  {{ color: #bae6fd; margin-top: .4rem; font-size: .9rem; }}
    main {{ max-width: 1100px; margin: 2rem auto; padding: 0 1.5rem; }}
    h2 {{ font-size: 1.3rem; color: #38bdf8; border-left: 4px solid #0ea5e9;
          padding-left: .75rem; margin: 2rem 0 1rem; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px,1fr)); gap: 1rem; }}
    .card  {{ background: #1e293b; border-radius: 10px; padding: 1.2rem; text-align: center; }}
    .card .val  {{ font-size: 2rem; font-weight: 700; color: #38bdf8; }}
    .card .lbl  {{ font-size: .78rem; color: #94a3b8; margin-top: .3rem; }}
    table {{ width: 100%; border-collapse: collapse; background: #1e293b;
             border-radius: 8px; overflow: hidden; }}
    th {{ background: #0f3460; color: #7dd3fc; font-size: .8rem; text-align: left;
          padding: .6rem 1rem; }}
    td {{ padding: .55rem 1rem; font-size: .82rem; border-bottom: 1px solid #334155; }}
    tr:last-child td {{ border-bottom: none; }}
    tr:hover td {{ background: #263148; }}
    .bar-row   {{ display: flex; align-items: center; gap: .7rem; margin: .4rem 0; }}
    .bar-label {{ width: 90px; font-size: .82rem; color: #fbbf24; }}
    .bar-track {{ flex: 1; background: #334155; border-radius: 4px; height: 14px; }}
    .bar-fill  {{ background: #0ea5e9; height: 100%; border-radius: 4px;
                  transition: width .5s ease; }}
    .bar-count {{ width: 40px; text-align: right; font-size: .8rem; color: #94a3b8; }}
    footer {{ text-align: center; padding: 2rem; color: #475569; font-size: .8rem; }}
  </style>
</head>
<body>
<header>
  <h1>🕷️ Smart Web Scraper — Data Report</h1>
  <p>Generated: {now} &nbsp;|&nbsp;
     Sources: books.toscrape.com &amp; realpython.github.io/fake-jobs</p>
</header>

<main>

  <!-- ── BOOKS ─────────────────────────────────── -->
  <h2>📚 Books Dataset</h2>

  <div class="cards">
    <div class="card"><div class="val">{books_stats.get('total', 0)}</div>
      <div class="lbl">Total Books</div></div>
    <div class="card"><div class="val">{books_stats.get('pages_scraped', 0)}</div>
      <div class="lbl">Pages Scraped</div></div>
    <div class="card"><div class="val">£{books_stats.get('avg_price', 0):.2f}</div>
      <div class="lbl">Avg Price</div></div>
    <div class="card"><div class="val">£{books_stats.get('min_price', 0):.2f}</div>
      <div class="lbl">Cheapest</div></div>
    <div class="card"><div class="val">£{books_stats.get('max_price', 0):.2f}</div>
      <div class="lbl">Most Expensive</div></div>
    <div class="card"><div class="val">{books_stats.get('avg_rating', 0):.1f}★</div>
      <div class="lbl">Avg Rating</div></div>
    <div class="card"><div class="val">{books_stats.get('in_stock_count', 0)}</div>
      <div class="lbl">In Stock</div></div>
  </div>

  <h2>⭐ Rating Distribution</h2>
  <div style="background:#1e293b;border-radius:10px;padding:1.2rem 1.5rem;">
    {rating_bars}
  </div>

  <h2>🏆 Top Rated Books</h2>
  <table>
    <thead><tr><th>Title</th><th>Price</th><th>Rating</th><th>Availability</th></tr></thead>
    <tbody>{_rows_books_top(books_stats.get('top_rated', []))}</tbody>
  </table>

  <h2>💰 Cheapest Books</h2>
  <table>
    <thead><tr><th>Title</th><th>Price</th><th>Rating</th><th>Availability</th></tr></thead>
    <tbody>{_rows_books_top(books_stats.get('cheapest', []))}</tbody>
  </table>

  <!-- ── JOBS ──────────────────────────────────── -->
  <h2>💼 Jobs Dataset</h2>

  <div class="cards">
    <div class="card"><div class="val">{jobs_stats.get('total', 0)}</div>
      <div class="lbl">Total Jobs</div></div>
    <div class="card"><div class="val">{jobs_stats.get('pages_scraped', 0)}</div>
      <div class="lbl">Pages Scraped</div></div>
    <div class="card">
      <div class="val">{len(jobs_stats.get('top_companies', []))}</div>
      <div class="lbl">Unique Companies</div></div>
  </div>

  <h2>🕒 Recent Job Postings</h2>
  <table>
    <thead><tr><th>Title</th><th>Company</th><th>Location</th><th>Date Posted</th></tr></thead>
    <tbody>{_rows_jobs(jobs_stats.get('recent_postings', []))}</tbody>
  </table>

  <h2>🏢 Top Hiring Companies</h2>
  <table>
    <thead><tr><th>Company</th><th>Listings</th></tr></thead>
    <tbody>
      {''.join(f"<tr><td>{c}</td><td>{n}</td></tr>" for c,n in jobs_stats.get('top_companies',[]))}
    </tbody>
  </table>

</main>
<footer>Smart Web Scraper &copy; {datetime.now().year} — Data extracted for educational purposes.</footer>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    logger.info(f"HTML report saved → {os.path.abspath(output_path)}")
