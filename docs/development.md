# Development and documentation maintenance

## Working conventions

- Python 3.12+, deterministic fixtures and strict input schemas.
- Small reviewable commits and offline-first tests.
- Only openly publishable, hardware/vendor-independent material.
- No downloaded weights, confidential data, generated `reports/`, tokens or invented empirical claims.
- Do not use paid hosted CI. Self-hosted workflows must run **trusted code only**; manually approve any documentation build on a self-hosted runner.

## Edit and preview the site

```bash
python -m pip install -e '.[dev,docs]'
python -m tools.check_docs
python -m mkdocs serve
```

Open the local development URL reported by MkDocs (typically `http://127.0.0.1:8000/`). Documentation content lives in `docs/`; navigation and theme settings live in `mkdocs.yml`. Search is client-side and does not require a hosted service.

Before review:

```bash
python -m tools.check_docs
python -m mkdocs build --strict --clean
python -m pytest -q
python -m ruff check src tests tools
```

A manual, self-hosted documentation-check workflow is provided. Its runner must have the documentation extra preinstalled; the workflow does not fetch dependencies from the network.

## Extend the docs

1. Add the new Markdown page under the appropriate `docs/` subdirectory.
2. Link it from `mkdocs.yml` navigation; every Markdown page belongs in navigation.
3. Use relative links between documentation pages; link source files with explicit repository URLs instead of unresolved paths outside `docs/`.
4. Supply a reproducible, self-contained command for any new example.
5. Describe units, confidence metrics, provenance, experimental limitations and what remains unverified.

Documentation is not automatically published to GitHub Pages. `mkdocs build --strict` produces a local, distributable `site/` folder; publishing requires a separately reviewed deployment configuration.

See [scientific evidence policy](concepts/evidence.md) and [verification guide](reproducibility.md).
