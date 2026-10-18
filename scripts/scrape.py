"""Scrape BLS Occupational Outlook Handbook pages into a local HTML cache."""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def valid_slug(value: object) -> str:
    slug = str(value or "").strip()
    if not SLUG_PATTERN.fullmatch(slug):
        raise ValueError(f"Invalid occupation slug: {slug!r}")
    return slug


def is_allowed_bls_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
    except ValueError:
        return False
    return parsed.scheme == "https" and parsed.hostname == "www.bls.gov" and parsed.port in (None, 443)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=int, default=0, help="Start index (inclusive)")
    parser.add_argument("--end", type=int, default=None, help="End index (exclusive)")
    parser.add_argument("--force", action="store_true", help="Re-scrape even if cached")
    parser.add_argument("--delay", type=float, default=1.0, help="Seconds between requests")
    args = parser.parse_args()

    if args.start < 0 or (args.end is not None and args.end < args.start):
        parser.error("--start must be >= 0 and --end must be >= --start")
    if args.delay < 0:
        parser.error("--delay must be >= 0")

    with (ROOT / "occupations.json").open(encoding="utf-8") as file:
        occupations = json.load(file)
    end = min(args.end, len(occupations)) if args.end is not None else len(occupations)
    subset = occupations[args.start:end]

    html_dir = ROOT / "html"
    html_dir.mkdir(exist_ok=True)
    to_scrape: list[tuple[int, dict[str, object]]] = []
    for index, occupation in enumerate(subset, start=args.start):
        slug = valid_slug(occupation.get("slug"))
        cache_path = html_dir / f"{slug}.html"
        if cache_path.exists() and not args.force:
            print(f"[{index}] CACHED {occupation.get('title', slug)}")
        else:
            url = str(occupation.get("url", ""))
            if not is_allowed_bls_url(url):
                raise ValueError(f"Refusing to scrape non-BLS URL for {slug}: {url!r}")
            to_scrape.append((index, {**occupation, "slug": slug, "url": url}))

    if not to_scrape:
        print("Nothing to scrape; selected pages are already cached.")
        return

    print(f"Scraping {len(to_scrape)} occupation pages with headless Chromium.")
    failures: list[str] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.set_default_timeout(15000)
            for position, (index, occupation) in enumerate(to_scrape):
                slug, url = str(occupation["slug"]), str(occupation["url"])
                print(f"[{index}] {occupation.get('title', slug)}...", end=" ", flush=True)
                try:
                    response = page.goto(url, wait_until="domcontentloaded", timeout=15000)
                    final_url_allowed = is_allowed_bls_url(page.url)
                    if response is None or response.status != 200 or not final_url_allowed:
                        status = response.status if response is not None else "no response"
                        raise RuntimeError(
                            f"request refused (HTTP {status}; final URL allowed={final_url_allowed})"
                        )
                    html = page.content()
                    destination = html_dir / f"{slug}.html"
                    temporary = destination.with_suffix(".html.tmp")
                    temporary.write_text(html, encoding="utf-8")
                    temporary.replace(destination)
                    print(f"OK ({len(html):,} characters)")
                except Exception as error:
                    failures.append(slug)
                    print(f"ERROR: {error}")
                if position < len(to_scrape) - 1 and args.delay:
                    time.sleep(args.delay)
        finally:
            browser.close()

    cached_count = sum(1 for path in html_dir.glob("*.html") if path.is_file())
    print(f"Finished: {cached_count}/{len(occupations)} cached HTML pages; errors: {len(failures)}.")
    if failures:
        print("Failed slugs: " + ", ".join(failures))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
