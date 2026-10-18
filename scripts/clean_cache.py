"""Clear local caches without deleting datasets or scraper results by default."""
from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
SKIP_DIR_NAMES = {".git", ".venv", "node_modules", "html", "pages", ".tox"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="List paths without deleting them")
    parser.add_argument(
        "--include-pipeline-cache",
        action="store_true",
        help="Also remove generated Markdown pages/ and site/data.json",
    )
    parser.add_argument(
        "--include-scraped-html",
        action="store_true",
        help="Also remove html/ scraper results (they must be downloaded again)",
    )
    args = parser.parse_args()

    candidates: set[Path] = set()
    for current, dirs, files in os.walk(ROOT):
        current_path = Path(current)
        dirs[:] = [name for name in dirs if name not in SKIP_DIR_NAMES]
        for name in list(dirs):
            if name in CACHE_DIR_NAMES:
                candidates.add(current_path / name)
                dirs.remove(name)
        for name in files:
            path = current_path / name
            if path.suffix in {".pyc", ".pyo"} or path.name == ".coverage":
                candidates.add(path)

    if args.include_pipeline_cache:
        candidates.add(ROOT / "pages")
        candidates.add(ROOT / "site" / "data.json")
    if args.include_scraped_html:
        candidates.add(ROOT / "html")

    existing = sorted(
        (path for path in candidates if path.exists()),
        key=lambda path: (len(path.parts), str(path)),
    )
    selected: list[Path] = []
    for path in existing:
        if not any(parent in path.parents for parent in selected):
            selected.append(path)

    for path in selected:
        print(f"{'Would remove' if args.dry_run else 'Removing'}: {path.relative_to(ROOT)}")
        if not args.dry_run:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

    if not selected:
        print("No matching cache files or directories found.")
    elif args.dry_run:
        print(f"Dry run complete: {len(selected)} cache item(s) listed.")
    else:
        print(f"Removed {len(selected)} cache item(s). Dataset files and committed occupation pages were preserved.")


if __name__ == "__main__":
    main()
