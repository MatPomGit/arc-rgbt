# Development and documentation

The canonical contribution/review rules are in
[CONTRIBUTING.md](https://github.com/MatPomGit/arc-rgbt/blob/main/CONTRIBUTING.md)
and [AGENTS.md](https://github.com/MatPomGit/arc-rgbt/blob/main/AGENTS.md).
Use Python 3.12+ and keep tests deterministic, code KISS/PEP 8, and
changes limited to the named responsibility.

## Validate locally

```bash
python -m pip install -e '.[dev,docs]'
python -m pytest -q
python -m ruff check src tests tools
python -m tools.check_docs
python -m mkdocs build --strict --clean
```

For documentation editing use `python -m mkdocs serve`. Each Markdown
page in `docs/` must appear in `mkdocs.yml` navigation; use relative
links inside the site and explicit repository links to files outside
`docs/`. The site is built locally; it is not automatically published.

## Optional offline browser checks

On Fedora/Linux with existing Chromium/Playwright:

```bash
ARC_RGBT_BROWSER_TEST=1 ARC_RGBT_CHROMIUM_EXECUTABLE=/usr/bin/chromium \
  python -m pytest -q tests/test_studio_browser.py tests/test_studio_playwright_offline.py
```

In PowerShell, set `$env:ARC_RGBT_BROWSER_TEST = "1"` instead of using
CMD's `set VARIABLE=1`. The detailed fail-closed procedure is in
[Offline Playwright](guides/playwright-offline.md).

Never run untrusted contributions on a persistent self-hosted runner.
Manual workflow dispatch, local wheelhouses and zero-paid-service policy
remain in force. For provenance see [reproducibility](reproducibility.md).
