# AI-CareerHub

AI-CareerHub is a searchable explorer and data pipeline for U.S. occupations from the Bureau of Labor Statistics (BLS) Occupational Outlook Handbook. It combines BLS employment, pay, education, and outlook data with an LLM-generated AI-exposure score.

The repository contains the source dataset, generated occupation pages, parsing scripts, scoring scripts, and a lightweight browser entry point.

## What is included

- Searchable occupation explorer at `index.html`
- 300+ BLS occupation records
- Individual generated occupation pages named by slug
- Employment, pay, education, and outlook extraction
- Optional AI-exposure scoring from 0–10 through OpenRouter
- Scripts to scrape, parse, score, and build derived datasets
- Reproducible Python environment managed with `uv`

## Data model

Each occupation can include:

- Title and BLS source URL
- BLS category and SOC code
- Median annual and hourly pay
- Employment counts
- Projected employment change
- Entry-level education
- Work experience and training requirements
- AI-exposure score and rationale

AI-exposure scores are analytical estimates produced by an LLM. They are not BLS forecasts, employment predictions, or guarantees about future automation.

## Quick start

Requirements:

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)
- A modern browser

Install dependencies:

~~~bash
uv sync
~~~

Serve the repository over HTTP:

~~~bash
uv run python -m http.server 8000
~~~

Open:

~~~text
http://localhost:8000/
~~~

Do not open `index.html` directly with `file://`; the browser explorer loads the JSON datasets with `fetch()`, which requires an HTTP origin.

## Data pipeline

The scripts are intended to be run from the repository root.

### 1. Parse the BLS occupation index

`parse_occupations.py` reads the saved BLS Occupational Outlook Handbook index and refreshes `occupations.json`.

~~~bash
uv run python parse_occupations.py
~~~

### 2. Scrape BLS detail pages

`scrape.py` uses Playwright and stores raw HTML in the ignored `html/` directory.

Install Chromium once:

~~~bash
uv run playwright install chromium
~~~

Then scrape:

~~~bash
uv run python scrape.py --start 0 --end 20
~~~

Use `--force` to refresh cached pages.

The scraper only accepts `https://www.bls.gov/` URLs and runs Chromium headlessly.

### 3. Convert HTML to Markdown

~~~bash
uv run python process.py
~~~

This writes parsed Markdown into the ignored `pages/` directory.

### 4. Build the CSV dataset

~~~bash
uv run python make_csv.py
~~~

This produces `occupations.csv`.

### 5. Score AI exposure

Set your OpenRouter key:

~~~bash
export OPENROUTER_API_KEY="your-key"
~~~

Score a test range:

~~~bash
uv run python score.py --start 0 --end 10
~~~

Results are checkpointed to `scores.json` after each occupation.

### 6. Build derived site data

~~~bash
uv run python build_site_data.py
~~~

This writes `site/data.json`.

## Security and reliability

- Scraped paths are validated before writing files, preventing a malicious occupation slug from escaping its intended directory.
- Scraping is restricted to BLS URLs.
- The scraper runs Chromium headlessly rather than opening an interactive browser.
- HTML parsing escapes Markdown table delimiters so source text cannot corrupt generated tables.
- AI scoring validates that model output is a JSON object with an integer exposure score from 0 to 10 and a non-empty rationale.
- No API keys are stored in the repository.
- Local virtual environments, caches, and generated pipeline directories are ignored by Git.
- The browser explorer uses a restrictive Content Security Policy and does not inject dataset values through `innerHTML`.

The checked-in `uv.lock` currently resolves `python-dotenv` to 1.2.2, which is the patched version for the 2026 symlink-following advisory; Playwright 1.58.0 is also above the affected range for its installer vulnerability. citeturn512262search0turn512262search7

## Repository layout

~~~text
AI-CareerHub/
├── index.html
├── occupations.json
├── occupations.csv
├── scores.json
├── prompt.md
├── pyproject.toml
├── uv.lock
├── parse_occupations.py
├── scrape.py
├── parse_detail.py
├── process.py
├── make_csv.py
├── make_prompt.py
├── score.py
├── build_site_data.py
└── <generated occupation>.html
~~~

Local scraper and parser output is intentionally kept outside the committed source tree in `html/`, `pages/`, and `site/data.json`.

## Sources

- [U.S. Bureau of Labor Statistics — Occupational Outlook Handbook](https://www.bls.gov/ooh/)
- AI-exposure scoring: LLM analysis using the scoring rubric in `score.py`

## License

MIT
