"""
Process scraped HTML files into Markdown.

Reads from html/<slug>.html, writes to pages/<slug>.md.
Reuses parse_detail.parse_ooh_page() which is already tested.

Usage:
    uv run python process.py              # process all HTML files
    uv run python process.py --force      # re-process even if .md exists
"""

import argparse
import json
from pathlib import Path
from parse_detail import parse_ooh_page


def main():
    parser = argparse.ArgumentParser(description="Convert HTML to Markdown")
    parser.add_argument("--force", action="store_true", help="Re-process even if .md exists")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    (root / "pages").mkdir(exist_ok=True)

    # Load master list for ordering/metadata
    with (root / "occupations.json").open(encoding="utf-8") as f:
        occupations = json.load(f)

    processed = 0
    skipped = 0
    missing = 0

    for occ in occupations:
        slug = occ["slug"].strip()
        if not slug or slug in {".", ".."} or "/" in slug or "\" in slug:
            raise ValueError(f"Invalid occupation slug: {slug!r}")
        html_path = root / "html" / f"{slug}.html"
        md_path = root / "pages" / f"{slug}.md"

        if not os.path.exists(html_path):
            missing += 1
            continue

        if not args.force and os.path.exists(md_path):
            skipped += 1
            continue

        md = parse_ooh_page(html_path)
        md_path.write_text(md, encoding="utf-8")
        processed += 1

    html_dir = root / "html"
    pages_dir = root / "pages"
    total_html = len([f for f in html_dir.iterdir() if f.suffix == ".html"]) if html_dir.exists() else 0
    total_md = len([f for f in pages_dir.iterdir() if f.suffix == ".md"]) if pages_dir.exists() else 0
    print(f"Processed: {processed}, Skipped (cached): {skipped}, Missing HTML: {missing}")
    print(f"Total: {total_html} HTML files, {total_md} Markdown files")


if __name__ == "__main__":
    main()
