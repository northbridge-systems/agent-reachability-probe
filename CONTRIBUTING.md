# Contributing

Thank you for considering a contribution to `agent-reachability-probe`.

## Reporting issues

Open a GitHub issue with:

- The command you ran and the URL you tested
- The output you got and what you expected
- Your Python version (`python3 --version`)
- Operating system

For security-relevant findings, please follow [SECURITY.md](./SECURITY.md) instead.

## Suggesting changes

Open an issue first to discuss substantial changes. Small fixes (typos, clearer error messages, additional crawler entries) can go straight to a pull request.

## Pull requests

- Fork the repository, create a topic branch from `main`
- Keep changes focused; one concern per pull request
- Match the existing code style (standard library only, no external dependencies, PEP 8)
- Update the README if user-facing behavior changes
- Add or update tests in `tests/` for new logic
- Run `python3 -m unittest discover tests` before submitting

## Adding a crawler

If you add a User-Agent entry to `CRAWLERS` in `probe.py`, include:

- A link to the operator's public documentation of the User-Agent string
- The date the string was verified

## Code of conduct

Participation in this project is governed by the [Code of Conduct](./CODE_OF_CONDUCT.md).
