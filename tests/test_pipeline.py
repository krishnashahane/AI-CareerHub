"""Regression tests for dataset integrity, parser behavior, and path safety."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.make_csv import parse_outlook, parse_pay
from scripts.parse_detail import parse_ooh_page
from scripts.process import valid_slug
from scripts.scrape import is_allowed_bls_url

ROOT = Path(__file__).resolve().parents[1]


class PipelineTests(unittest.TestCase):
    def test_valid_slug(self):
        self.assertEqual(valid_slug("software-developers"), "software-developers")

    def test_rejects_path_traversal_slugs(self):
        for value in ("../outside", "..", "folder/name", r"folder\\name", "", "UPPERCASE"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                valid_slug(value)

    def test_only_https_bls_urls_are_allowed(self):
        self.assertTrue(is_allowed_bls_url("https://www.bls.gov/ooh/example.htm"))
        for url in (
            "http://www.bls.gov/ooh/example.htm",
            "https://bls.gov/ooh/example.htm",
            "https://www.bls.gov.evil.example/ooh/example.htm",
            "https://example.com/",
            "javascript:alert(1)",
        ):
            with self.subTest(url=url):
                self.assertFalse(is_allowed_bls_url(url))

    def test_pay_and_outlook_parsers(self):
        self.assertEqual(parse_pay("$62,350 per year $29.98 per hour"), ("62350", "29.98"))
        self.assertEqual(parse_outlook("9% (Much faster than average)"), ("9", "Much faster than average"))

    def test_parser_escapes_markdown_table_delimiters(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            sample = Path(temporary_directory) / "sample.html"
            sample.write_text(
                '<html><head><link rel="canonical" href="https://www.bls.gov/ooh/example.htm"></head>'
                '<body><h1>Example Occupation</h1><table id="quickfacts"><tbody>'
                '<tr><th>Median pay</th><td>Pay | values</td></tr></tbody></table></body></html>',
                encoding="utf-8",
            )
            self.assertIn(r"Pay \| values", parse_ooh_page(sample))

    def test_repository_datasets_have_expected_shape(self):
        occupations = json.loads((ROOT / "occupations.json").read_text(encoding="utf-8"))
        scores = json.loads((ROOT / "scores.json").read_text(encoding="utf-8"))
        self.assertTrue(occupations)
        self.assertTrue(scores)
        seen_slugs = set()
        for occupation in occupations:
            self.assertTrue(occupation.get("title"))
            self.assertRegex(occupation.get("slug", ""), r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
            self.assertTrue(occupation.get("url", "").startswith("https://www.bls.gov/ooh/"))
            self.assertNotIn(occupation["slug"], seen_slugs)
            seen_slugs.add(occupation["slug"])
        for score in scores:
            self.assertTrue(score.get("slug"))
            self.assertIsInstance(score.get("exposure"), int)
            self.assertGreaterEqual(score["exposure"], 0)
            self.assertLessEqual(score["exposure"], 10)
            self.assertTrue(score.get("rationale", "").strip())


if __name__ == "__main__":
    unittest.main()
