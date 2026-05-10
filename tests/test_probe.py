"""Minimal unit tests for agent-reachability-probe.

Run with: python3 -m unittest tests/test_probe.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Make probe.py importable from the repository root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import probe  # noqa: E402


class CrawlerListTests(unittest.TestCase):
    def test_known_crawlers_present(self) -> None:
        expected = {
            "GPTBot",
            "ChatGPT-User",
            "OAI-SearchBot",
            "ClaudeBot",
            "PerplexityBot",
            "Google-Extended",
            "CCBot",
        }
        self.assertTrue(expected.issubset(probe.CRAWLERS.keys()))

    def test_user_agent_strings_non_empty(self) -> None:
        for name, ua in probe.CRAWLERS.items():
            with self.subTest(crawler=name):
                self.assertTrue(ua.strip(), f"empty UA for {name}")
                self.assertIn("/", ua, f"UA for {name} looks malformed")


class FormatTextTests(unittest.TestCase):
    def test_renders_minimal_report(self) -> None:
        report = {
            "url": "https://example.com/",
            "results": {
                "Browser (Chrome)": {
                    "status": 200,
                    "content_length": 1256,
                    "content_type": "text/html",
                    "elapsed_ms": 12.3,
                    "error": None,
                    "robots": {"robots_url": None, "allowed": None, "error": "n/a"},
                    "js_dependency_flag": None,
                },
                "GPTBot": {
                    "status": 200,
                    "content_length": 1256,
                    "content_type": "text/html",
                    "elapsed_ms": 14.1,
                    "error": None,
                    "robots": {
                        "robots_url": "https://example.com/robots.txt",
                        "allowed": True,
                        "error": None,
                    },
                    "js_dependency_flag": False,
                },
            },
        }
        rendered = probe.format_text(report)
        self.assertIn("https://example.com/", rendered)
        self.assertIn("GPTBot", rendered)
        self.assertIn("allowed", rendered)
        self.assertIn("Browser (Chrome)", rendered)


class JsHeuristicRatioTests(unittest.TestCase):
    def test_ratio_constant_is_sensible(self) -> None:
        self.assertGreater(probe.JS_HEURISTIC_RATIO, 0.0)
        self.assertLess(probe.JS_HEURISTIC_RATIO, 1.0)


if __name__ == "__main__":
    unittest.main()
