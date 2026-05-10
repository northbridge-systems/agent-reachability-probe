# agent-reachability-probe

A standalone Python probe that simulates the major LLM crawlers and reports
whether they can actually reach a given URL.

For each crawler, the probe records:

- HTTP status code
- Content-Length and Content-Type
- whether `robots.txt` allows that crawler on the path
- a simple JS-dependency heuristic (response size relative to a browser baseline)

No third-party dependencies. Python 3.9 or newer, standard library only.

## Why this exists

Generative engines retrieve content through dedicated crawlers with distinct
User-Agent strings. A page that renders perfectly in Chrome may be invisible
to GPTBot if it requires JavaScript, returns a different status code for the
bot, or is disallowed in `robots.txt` without the operator's knowledge.

`agent-reachability-probe` makes those failure modes explicit before the
engines route around them silently.

## Crawlers covered

GPTBot, ChatGPT-User, OAI-SearchBot, ClaudeBot, PerplexityBot, Google-Extended,
CCBot, Bytespider — plus a Chrome browser baseline for comparison.

User-Agent strings reflect the documented public versions as of early 2026.
When operators change their strings, update `CRAWLERS` in `probe.py`.

## Install

```bash
git clone https://github.com/northbridge-systems/agent-reachability-probe.git
cd agent-reachability-probe
```

That is the entire install. No `pip install`, no virtual environment required.

## Use

```bash
python3 probe.py https://example.com/
```

Output is a text table by default:

```
URL: https://example.com/

Crawler               Status     Bytes   robots.txt   JS-dep?  Note
-------------------------------------------------------------------
Browser (Chrome)         200    1 256          n/a        no
GPTBot                   200    1 256      allowed        no
ChatGPT-User             200    1 256      allowed        no
OAI-SearchBot            200    1 256      allowed        no
ClaudeBot                200    1 256      allowed        no
PerplexityBot            200    1 256      allowed        no
Google-Extended          200    1 256      allowed        no
CCBot                    200    1 256      allowed        no
Bytespider               200    1 256      allowed        no
```

Machine-readable JSON output for pipelines:

```bash
python3 probe.py https://example.com/ --json
```

Custom timeout per request:

```bash
python3 probe.py https://example.com/ --timeout 30
```

## How to read the output

**Status** — anything other than `200` for a specific crawler while the
browser baseline returns `200` indicates User-Agent-based gating.

**Bytes** — values significantly smaller than the browser baseline often
indicate a client-side rendered page. The `JS-dep?` column flags responses
smaller than half the baseline size.

**robots.txt** — `DISALLOWED` means the crawler is excluded by your own
`robots.txt`. That is either intentional or the most expensive single
configuration error in generative-engine visibility.

**JS-dep?** — `likely` is a heuristic, not a verdict. Some pages legitimately
serve a smaller HTML to crawlers; others fail to render their main content at
all. Confirm by viewing the response directly.

## Limitations

- Heuristic only. A response that passes this probe is not guaranteed to be
  parsed correctly by the downstream model.
- User-Agent strings of LLM crawlers change. Treat `CRAWLERS` in `probe.py`
  as a maintained list, not a constant.
- The JS-dependency check is size-based and does not execute JavaScript. For
  precise render-state checks, use a headless browser probe alongside this one.

## Part of

This tool is part of the
[Compliance-GEO methodology](https://www.northbridgesystems.de/de/) maintained
by [Northbridge Systems](https://github.com/northbridge-systems).

## License

MIT — see [LICENSE](LICENSE).
