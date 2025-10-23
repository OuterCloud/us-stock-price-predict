"""Playwright scraper for Yahoo Finance historical prices table.

Usage:
  python scripts/scrape_yahoo_playwright.py <url> [TICKER]

If Playwright isn't installed, the script will print installation hints.

Installation:
  pip install playwright
  playwright install chromium
"""

import sys
from pathlib import Path


def ensure_playwright():
    try:
        from playwright.sync_api import sync_playwright

        return True
    except Exception:
        print("Playwright not installed. Install with:")
        print("  pip install playwright")
        print("  playwright install chromium")
        return False


def extract_table_and_save(html, ticker):
    try:
        import pandas as pd
        from bs4 import BeautifulSoup
    except Exception as e:
        print("Missing dependencies for parsing (pandas/bs4):", e)
        return False

    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", attrs={"data-test": "historical-prices"})
    if table is None:
        table = soup.find("table")
        if table is None:
            print("No table found in rendered HTML")
            return False

    headers = [th.get_text(strip=True) for th in table.find_all("th")]
    rows = []
    for tr in table.find_all("tr"):
        tds = tr.find_all("td")
        if not tds:
            continue
        rows.append([td.get_text(strip=True) for td in tds])

    if not rows:
        print("No rows extracted")
        return False

    df = pd.DataFrame(rows, columns=headers[: len(rows[0])])
    out = Path("data") / f"stock_{ticker or 'UNKNOWN'}.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        df.to_parquet(out, index=False)
        print("Wrote", out)
        return True
    except Exception as e:
        csv_out = out.with_suffix(".csv")
        df.to_csv(csv_out, index=False)
        print("Parquet write failed, wrote CSV", csv_out, "error:", e)
        return True


def main(url, ticker=None):
    if not ensure_playwright():
        raise SystemExit(2)

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        # Increase timeouts and navigation waiting
        page.set_default_navigation_timeout(120000)
        page.set_default_timeout(120000)
        try:
            page.goto(url, timeout=60000, wait_until="networkidle")

            # Try to accept cookie banners if present (several possible labels)
            cookie_selectors = [
                'button:has-text("Accept")',
                'button:has-text("Accept all")',
                'button:has-text("I agree")',
                'button:has-text("Agree")',
                'button[aria-label="agree"]',
                'button[title*="Accept"]',
            ]
            for sel in cookie_selectors:
                try:
                    if page.query_selector(sel):
                        page.click(sel)
                        print("Clicked cookie selector", sel)
                        break
                except Exception:
                    continue

            # wait for the historical table
            page.wait_for_selector(
                'table[data-test="historical-prices"]', timeout=60000
            )
        except Exception as e:
            print("Page load / selector wait failed:", e)
            html = page.content()
            Path("data").mkdir(parents=True, exist_ok=True)
            debug_file = Path("data") / f"debug_{ticker or 'UNKNOWN'}.html"
            debug_file.write_text(html, errors="ignore")
            # also save a screenshot for debugging
            try:
                shot = Path("data") / f"debug_{ticker or 'UNKNOWN'}.png"
                page.screenshot(path=str(shot), full_page=True)
                print("Wrote rendered debug screenshot to", shot)
            except Exception as se:
                print("Screenshot failed:", se)
            print("Wrote rendered debug HTML to", debug_file)
            browser.close()
            raise

        html = page.content()
        browser.close()

    ok = extract_table_and_save(html, ticker or "UNKNOWN")
    if not ok:
        debug_file = Path("data") / f"debug_{ticker or 'UNKNOWN'}.html"
        debug_file.write_text(html, errors="ignore")
        print("Wrote rendered debug HTML to", debug_file)


# python scripts/scrape_yahoo_playwright.py "https://finance.yahoo.com/quote/IONQ/history" IONQ
if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else None
    ticker = sys.argv[2] if len(sys.argv) > 2 else None
    if not url:
        print("Usage: python scripts/scrape_yahoo_playwright.py <url> [TICKER]")
        raise SystemExit(2)
    main(url, ticker)
