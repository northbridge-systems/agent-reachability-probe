#!/usr/bin/env python3
"""
agent-reachability-probe: simulates major LLM crawlers and reports reachability.

For each known crawler User-Agent, the probe fetches a target URL and reports:
- HTTP status code
- Content-Length and Content-Type
- Whether robots.txt allows that crawler on the given path
- A simple JS-dependency heuristic (size ratio vs. a browser baseline)

Standalone, standard-library only.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from urllib import robotparser

CRAWLERS: dict[str, str] = {
    "GPTBot": (
        "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; "
        "GPTBot/1.2; +https://openai.com/gptbot)"
    ),
    "ChatGPT-User": (
        "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; "
        "ChatGPT-User/1.0; +https://openai.com/bot)"
    ),
    "OAI-SearchBot": (
        "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; "
        "OAI-SearchBot/1.0; +https://openai.com/searchbot)"
    ),
    "ClaudeBot": (
        "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; "
        "ClaudeBot/1.0; +claudebot@anthropic.com)"
    ),
    "PerplexityBot": (
        "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; "
        "PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)"
    ),
    "Google-Extended": (
        "Mozilla/5.0 (compatible; Google-Extended/1.0; "
        "+https://policies.google.com/extended)"
    ),
    "CCBot": "CCBot/2.0 (https://commoncrawl.org/faq/)",
    "Bytespider": "Mozilla/5.0 (compatible; Bytespider; spider-feedback@bytedance.com)",
}

BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

DEFAULT_TIMEOUT = 15.0
JS_HEURISTIC_RATIO = 0.5


def fetch(url: str, user_agent: str, timeout: float) -> dict:
    """Fetch URL with a given UA and return result dict."""
    request = urllib.request.Request(
        url,
        headers={"User-Agent": user_agent, "Accept": "*/*"},
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read()
            elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
            return {
                "status": response.status,
                "content_length": len(body),
                "content_type": response.headers.get("Content-Type", ""),
                "elapsed_ms": elapsed_ms,
                "error": None,
            }
    except urllib.error.HTTPError as exc:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
        return {
            "status": exc.code,
            "content_length": 0,
            "content_type": "",
            "elapsed_ms": elapsed_ms,
            "error": exc.reason,
        }
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
        return {
            "status": None,
            "content_length": 0,
            "content_type": "",
            "elapsed_ms": elapsed_ms,
            "error": str(exc),
        }


def check_robots(url: str, user_agent_name: str, timeout: float) -> dict:
    """Check robots.txt for the given crawler name on the URL path."""
    parsed = urllib.parse.urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    parser = robotparser.RobotFileParser()
    parser.set_url(robots_url)
    try:
        import socket
        socket.setdefaulttimeout(timeout)
        parser.read()
        allowed = parser.can_fetch(user_agent_name, url)
        return {"robots_url": robots_url, "allowed": allowed, "error": None}
    except Exception as exc:  # noqa: BLE001
        return {"robots_url": robots_url, "allowed": None, "error": str(exc)}


def probe(url: str, timeout: float = DEFAULT_TIMEOUT) -> dict:
    """Run the full probe for one URL."""
    results: dict[str, dict] = {}

    baseline = fetch(url, BROWSER_UA, timeout)
    results["Browser (Chrome)"] = {
        **baseline,
        "robots": {"robots_url": None, "allowed": None, "error": "not applicable"},
        "js_dependency_flag": None,
    }
    baseline_size = baseline["content_length"] or 0

    for name, ua in CRAWLERS.items():
        fetched = fetch(url, ua, timeout)
        robots = check_robots(url, name, timeout)

        js_flag: bool | None = None
        if baseline_size and fetched["content_length"]:
            ratio = fetched["content_length"] / baseline_size
            js_flag = ratio < JS_HEURISTIC_RATIO

        results[name] = {
            **fetched,
            "robots": robots,
            "js_dependency_flag": js_flag,
        }

    return {"url": url, "results": results}


def format_text(report: dict) -> str:
    """Render a human-readable text report."""
    lines: list[str] = [f"URL: {report['url']}", ""]
    header = (
        f"{'Crawler':<20} {'Status':>7} {'Bytes':>9} {'robots.txt':>12} "
        f"{'JS-dep?':>9}  Note"
    )
    lines.append(header)
    lines.append("-" * len(header))

    for name, item in report["results"].items():
        status = str(item["status"]) if item["status"] is not None else "-"
        size = f"{item['content_length']:,}".replace(",", " ")
        robots_state = item["robots"].get("allowed")
        if robots_state is True:
            robots_str = "allowed"
        elif robots_state is False:
            robots_str = "DISALLOWED"
        else:
            robots_str = "n/a"
        js_flag = item.get("js_dependency_flag")
        if js_flag is True:
            js_str = "likely"
        elif js_flag is False:
            js_str = "no"
        else:
            js_str = "-"
        note = item.get("error") or ""
        lines.append(
            f"{name:<20} {status:>7} {size:>9} {robots_str:>12} {js_str:>9}  {note}"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="probe.py",
        description="Probe a URL with major LLM crawler User-Agents.",
    )
    parser.add_argument("url", help="Target URL (include scheme).")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of a text table.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=f"Per-request timeout in seconds (default: {DEFAULT_TIMEOUT}).",
    )
    args = parser.parse_args(argv)

    report = probe(args.url, timeout=args.timeout)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(format_text(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
