# AI-CareerHub

AI-CareerHub is a searchable explorer for U.S. occupations from the Bureau of Labor Statistics (BLS) Occupational Outlook Handbook. It combines BLS employment, pay, education, and outlook data with an LLM-generated AI-exposure score.

AI-exposure scores are analytical estimates, not BLS forecasts or guarantees about future employment or automation.

## Features

- Static occupation explorer with search and dataset summaries
- Individual occupation detail pages linked from the explorer
- CSV/JSON occupation datasets and model-generated AI-exposure scores
- Reproducible Python environment managed with `uv`
- Headless BLS scraper and Markdown/CSV/site-data generation pipeline
- Regression tests and GitHub Actions dependency auditing

## Repository layout

```text
AI-CareerHub/
├── assets/
│   ├── app.js
│   └── styles.css
├── scripts/
│   ├── parse_occupations.py
│   ├── parse_detail.py
│   ├── scrape.py
│   ├── process.py
│   ├── make_csv.py
│   ├── make_prompt.py
│   ├── score.py
│   ├── build_site_data.py
│   └── clean_cache.py
├── tests/
├── .github/workflows/quality.yml
├── index.html
├── occupations.json
├── occupations.csv
├── scores.json
├── prompt.md
├── pyproject.toml
└── uv.lock
```

The occupation detail pages remain at the repository root because `index.html` links to them by slug. The pipeline implementation lives in `scripts/`; generated local scrape/Markdown caches are ignored by Git.

## Requirements and local setup

- Python 3.10 or later
- [uv](https://docs.astral.sh/uv/)
- Chromium for Playwright scraping

Install the locked environment:

```bash
uv sync
```

Start the static explorer from the repository root:

```bash
uv run python -m http.server 8000
```

Open [http://localhost:8000](http://localhost:8000). Do not open `index.html` with `file://`: its JSON datasets are loaded using `fetch()`, which requires an HTTP origin.

## Data pipeline

Run commands from the repository root. Each is also available as a `careerhub-*` command installed by `uv sync`.

### 1. Parse the saved BLS occupation index

```bash
uv run python -m scripts.parse_occupations
```

Reads `occupational_outlook_handbook.html` and atomically refreshes `occupations.json`. Extracted records include title, category, slug, and URL; generated URLs are restricted to HTTPS pages on `www.bls.gov`.

### 2. Scrape BLS occupation details

Install Chromium once:

```bash
uv run playwright install chromium
```

Scrape a small range first:

```bash
uv run python -m scripts.scrape --start 0 --end 20
```

The scraper runs headlessly, validates each BLS URL and final redirect destination, skips cached pages by default, and writes fetched HTML under ignored `html/`. Use `--force` to refresh existing pages.

### 3. Convert cached HTML to Markdown

```bash
uv run python -m scripts.process
```

This writes generated Markdown to ignored `pages/`. Use `--force` to regenerate existing Markdown.

### 4. Build the CSV dataset

```bash
uv run python -m scripts.make_csv
```

This reads cached HTML and writes `occupations.csv`.

### 5. Score AI exposure with OpenRouter

Store the key in your shell or in a local, untracked `.env` file:

```bash
export OPENROUTER_API_KEY="your-key"
uv run python -m scripts.score --start 0 --end 10
```

Results are checkpointed atomically to `scores.json`. The default run skips occupations already scored; `--force` requests recalculation. Never commit API keys or private `.env` files.

### 6. Build derived files

```bash
uv run python -m scripts.build_site_data
uv run python -m scripts.make_prompt
```

The first writes `site/data.json`; the second refreshes `prompt.md`.

## Cache cleaning

The default cache-clean command removes Python bytecode and tool caches only:

```bash
uv run python -m scripts.clean_cache --dry-run
uv run python -m scripts.clean_cache
```

Generated Markdown and site output can optionally be removed with `--include-pipeline-cache`. Scraped HTML is retained unless `--include-scraped-html` is explicitly provided, because deleting it means re-downloading source pages. Dataset files, API scores, prompt data, and committed occupation pages are preserved by default.

## Tests and security checks

Run local checks:

```bash
uv run python -m compileall -q scripts tests
uv run python -m unittest discover -s tests -v
```

GitHub Actions runs compilation, regression tests, and `pip-audit` on pushes to `main` or `hardening/**` and on pull requests. The dependency audit checks the installed dependency environment in CI; it is not a claim that every deployment or dataset has been independently security-reviewed.

Security controls include:
- A restrictive Content Security Policy; application JavaScript and CSS are external same-origin files.
- DOM text insertion via `textContent` rather than dataset-driven HTML injection.
- Slug/path validation before writing generated files.
- Scraping restricted to HTTPS on `www.bls.gov`, including redirect validation.
- Environment-based API credentials and no committed secret file.
- A cache cleaner that preserves source datasets and scrape results unless explicitly asked otherwise.

## Sources

- [U.S. Bureau of Labor Statistics — Occupational Outlook Handbook](https://www.bls.gov/ooh/)
- AI-exposure scoring rubric: `scripts/score.py`

## License

MIT. See [LICENSE](LICENSE).
