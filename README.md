# agent-reachability-probe

A standalone Python probe that simulates the major LLM crawlers and reports whether they can actually reach a given URL.

For each crawler, the probe records:

- HTTP status code
- Content-Length and Content-Type
- whether `robots.txt` allows that crawler on the path
- a simple JS-dependency heuristic (response size relative to a browser baseline)

No third-party dependencies. Python 3.9 or newer, standard library only.

## Why this exists

Generative engines retrieve content through dedicated crawlers with distinct User-Agent strings. A page that renders perfectly in Chrome may be invisible to GPTBot if it requires JavaScript, returns a different status code for the bot, or is disallowed in `robots.txt` without the operator's knowledge.

`agent-reachability-probe` makes those failure modes explicit before the engines route around them silently.

## Crawlers covered

GPTBot, ChatGPT-User, OAI-SearchBot, ClaudeBot, PerplexityBot, Google-Extended, CCBot, Bytespider — plus a Chrome browser baseline for comparison.

User-Agent strings reflect the documented public versions as of early 2026. When operators change their strings, update `CRAWLERS` in `probe.py`.

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

**Status** — anything other than `200` for a specific crawler while the browser baseline returns `200` indicates User-Agent-based gating.

**Bytes** — values significantly smaller than the browser baseline often indicate a client-side rendered page. The `JS-dep?` column flags responses smaller than half the baseline size.

**robots.txt** — `DISALLOWED` means the crawler is excluded by your own `robots.txt`. That is either intentional or the most expensive single configuration error in generative-engine visibility.

**JS-dep?** — `likely` is a heuristic, not a verdict. Some pages legitimately serve a smaller HTML to crawlers; others fail to render their main content at all. Confirm by viewing the response directly.

## Limitations

- Heuristic only. A response that passes this probe is not guaranteed to be parsed correctly by the downstream model.
- User-Agent strings of LLM crawlers change. Treat `CRAWLERS` in `probe.py` as a maintained list, not a constant.
- The JS-dependency check is size-based and does not execute JavaScript. For precise render-state checks, use a headless browser probe alongside this one.

## Citation

If you use this software in academic work, please cite it via the **Cite this repository** button in the right sidebar of this page, or directly via [CITATION.cff](./CITATION.cff).

## Part of the Compliance-GEO methodology

This tool is part of the Compliance-GEO methodology maintained by Northbridge Systems for citation visibility in regulated consumer markets (telecommunications, financial services, insurance, commerce).

- **Methodology** · [Compliance-GEO Codex](https://www.northbridgesystems.de/de/codex/)
- **Empirical evidence** · [Studie DE-Telco](https://www.northbridgesystems.de/de/studie-de-telco/)
- **Procurement standard** · [Einkaufs-Standard](https://www.northbridgesystems.de/de/einkaufs-standard/)
- **Legal anchor** · [BGH-Rechtsprechung](https://www.northbridgesystems.de/de/bgh-rechtsprechung/)

## Industrial property rights

Filed at the German Patent and Trademark Office (DPMA) on 27 April 2026:

- Utility model **DE 20 2026 001 867.4** — Computer system for evaluating digital publication placements in generative AI systems
- Patent application **DE 10 2026 002 308.4** — Deterministic, reproducible retrieval evaluation across multiple independent generative AI systems with signature-secured override discipline

## Author

**Tim Heidfeld** · CEFA · Diplom-Investmentanalyst
Founder & Principal, Northbridge Systems GmbH · Kiefersfelden, Bavaria, Germany

- ORCID · [0009-0008-2133-2625](https://orcid.org/0009-0008-2133-2625)
- ResearchGate · [profile/Tim-Heidfeld](https://www.researchgate.net/profile/Tim-Heidfeld)
- Website · [northbridgesystems.de](https://www.northbridgesystems.de/de/)

## License

MIT — see [LICENSE](LICENSE).
