"""Convert cached BLS HTML files into Markdown pages."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts.parse_detail import parse_ooh_page

ROOT = Path(__file__).resolve().parents[1]
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def valid_slug(value: object) -> str:
    slug = str(value or "").strip()
    if not SLUG_PATTERN.fullmatch(slug):
        raise ValueError(f"Invalid occupation slug: {slug!r}")
    return slug


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Regenerate existing Markdown files")
    args = parser.parse_args()

    with (ROOT / "occupations.json").open(encoding="utf-8") as file:
        occupations = json.load(file)

    html_dir, pages_dir = ROOT / "html", ROOT / "pages"
    pages_dir.mkdir(exist_ok=True)
    processed = skipped = missing = 0

    for occupation in occupations:
        slug = valid_slug(occupation.get("slug"))
        html_path = html_dir / f"{slug}.html"
        markdown_path = pages_dir / f"{slug}.md"
        if not html_path.is_file():
            missing += 1
            continue
        if markdown_path.exists() and not args.force:
            skipped += 1
            continue
        markdown_path.write_text(parse_ooh_page(html_path), encoding="utf-8")
        processed += 1

    html_count = sum(1 for path in html_dir.glob("*.html")) if html_dir.is_dir() else 0
    markdown_count = sum(1 for path in pages_dir.glob("*.md"))
    print(f"Processed: {processed}; cached: {skipped}; missing HTML: {missing}")
    print(f"Cache contains {html_count} HTML files and {markdown_count} Markdown files.")


if __name__ == "__main__":
    main()
