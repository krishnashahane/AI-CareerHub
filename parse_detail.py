"""Parse a BLS OOH detail page into clean Markdown."""

from pathlib import Path
import re
import sys

from bs4 import BeautifulSoup


def clean(text):
    return re.sub(r"\s+", " ", text).strip()


def escape_cell(text):
    return clean(text).replace("|", "\\|").replace("\n", " ")


def parse_ooh_page(html_path):
    source = Path(html_path).resolve()
    if not source.is_file():
        raise FileNotFoundError(f"HTML source not found: {source}")

    soup = BeautifulSoup(source.read_text(encoding="utf-8"), "html.parser")
    md = []

    h1 = soup.find("h1")
    title = clean(h1.get_text()) if h1 else "Unknown Occupation"
    md.extend([f"# {title}", ""])

    canonical = soup.find("link", rel="canonical")
    canonical_url = canonical.get("href") if canonical else None
    if canonical_url:
        md.extend([f"**Source:** {canonical_url}", ""])

    qf_table = soup.find("table", id="quickfacts")
    if qf_table:
        md.extend(["## Quick Facts", "", "| Field | Value |", "|-------|-------|"])
        tbody = qf_table.find("tbody")
        for row in tbody.find_all("tr") if tbody else []:
            th = row.find("th")
            td = row.find("td")
            if th and td:
                md.append(f"| {escape_cell(th.get_text())} | {escape_cell(td.get_text())} |")
        md.append("")

    panes = soup.find("div", id="panes")
    if not panes:
        return "\n".join(md)

    skip_tabs = {"tab-1", "tab-7", "tab-8", "tab-9"}
    for tab_id in [f"tab-{i}" for i in range(1, 10)]:
        if tab_id in skip_tabs:
            continue

        tab_div = panes.find("div", id=tab_id)
        if not tab_div:
            continue

        article = tab_div.find("article") or tab_div
        h2 = article.find("h2")
        if not h2:
            continue

        span = h2.find("span")
        section_title = clean(span.get_text()) if span else clean(h2.get_text())
        md.extend([f"## {section_title}", ""])

        chart_div = article.find("div", class_="ooh-chart")
        if chart_div:
            chart_subtitle = chart_div.find("p")
            dts = chart_div.find("dl")
            if dts:
                items = []
                for dt, dd in zip(dts.find_all("dt"), dts.find_all("dd")):
                    label = escape_cell(dt.get_text())
                    for value_span in dd.find_all("span"):
                        value = clean(value_span.get_text())
                        if value and (value.startswith("$") or value.endswith("%")):
                            items.append((label, value))
                            break
                if items:
                    subtitle = clean(chart_subtitle.get_text()) if chart_subtitle else ""
                    if subtitle:
                        md.extend([f"*{subtitle}*", ""])
                    for label, value in items:
                        md.append(f"- **{label}**: {value}")
                    md.append("")

        for elem in article.children:
            if not getattr(elem, "name", None):
                continue
            if elem.name == "h2":
                continue
            if elem.name == "div" and "ooh-chart" in elem.get("class", []):
                continue
            if elem.name == "div" and "ooh_right_img" in elem.get("class", []):
                continue

            if elem.name == "h3":
                md.extend([f"### {clean(elem.get_text())}", ""])
            elif elem.name == "p":
                text = clean(elem.get_text())
                if text:
                    md.extend([text, ""])
            elif elem.name == "ul":
                for li in elem.find_all("li"):
                    md.append(f"- {clean(li.get_text())}")
                md.append("")
            elif elem.name == "table":
                if elem.get("id") == "outlook-table":
                    continue
                rows = []
                for row in elem.find_all("tr"):
                    values = [escape_cell(cell.get_text()) for cell in row.find_all(["td", "th"])]
                    if values and any(values):
                        rows.append(values)
                if rows:
                    max_cols = max(len(row) for row in rows)
                    rows = [row + [""] * (max_cols - len(row)) for row in rows]
                    md.append("| " + " | ".join(["---"] * max_cols) + " |")
                    for row in rows:
                        md.append("| " + " | ".join(row) + " |")
                    md.append("")

        if tab_id == "tab-6":
            outlook_table = article.find("table", id="outlook-table")
            if outlook_table:
                md.extend(["### Employment Projections", ""])
                tbody = outlook_table.find("tbody")
                labels = [
                    "Occupational Title",
                    "SOC Code",
                    "Employment 2024",
                    "Projected Employment 2034",
                    "Change % 2024-34",
                    "Change Numeric 2024-34",
                ]
                for row in tbody.find_all("tr") if tbody else []:
                    values = [clean(cell.get_text()) for cell in row.find_all(["td", "th"])]
                    if values:
                        for label, value in zip(labels, values):
                            if value and value != "Get data":
                                md.append(f"- **{label}:** {escape_cell(value)}")
                        md.append("")

    update_p = soup.find("p", class_="update")
    if update_p:
        md.extend(["---", f"*{clean(update_p.get_text())}*", ""])

    return "\n".join(md)


if __name__ == "__main__":
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("electricians.html")
    result = parse_ooh_page(input_path)
    output_path = input_path.with_suffix(".md")
    output_path.write_text(result, encoding="utf-8")
    print(f"Written to {output_path}")
    print()
    print(result)
