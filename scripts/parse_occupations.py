"""Parse the saved BLS Occupational Outlook Handbook A–Z index."""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def main() -> None:
    source = ROOT / "occupational_outlook_handbook.html"
    if not source.is_file():
        raise FileNotFoundError(f"Required source file not found: {source}")

    soup = BeautifulSoup(source.read_text(encoding="utf-8"), "html.parser")
    az_list = soup.find("div", class_="a-z-list")
    if az_list is None:
        raise RuntimeError("BLS A–Z list not found in occupational_outlook_handbook.html")

    occupations: dict[str, dict[str, str]] = {}
    alias_count = 0
    for item in az_list.find_all("li"):
        links = item.find_all("a", href=True)
        label = item.get_text(" ", strip=True)
        if (", see:" in label or ", see " in label) and len(links) >= 2:
            title, url = links[1].get_text(strip=True), links[1]["href"]
            alias_count += 1
        elif links:
            title, url = links[0].get_text(strip=True), links[0]["href"]
        else:
            continue

        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname != "www.bls.gov":
            continue
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) < 3 or parts[0] != "ooh":
            continue
        category = parts[1]
        slug = Path(parts[-1]).stem
        if not title or not SLUG_PATTERN.fullmatch(slug):
            continue
        occupations.setdefault(url, {"title": title, "url": url, "category": category, "slug": slug})

    output = sorted(occupations.values(), key=lambda item: item["title"].casefold())
    if not output:
        raise RuntimeError("No valid BLS occupations were extracted; refusing to overwrite the dataset.")

    destination = ROOT / "occupations.json"
    temporary = destination.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(destination)
    print(f"Saved {len(output)} occupations; alias entries found: {alias_count}.")


if __name__ == "__main__":
    main()
