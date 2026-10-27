# Contributing

Keep code and documentation small, source-backed and reusable.
Follow [AGENTS.md](AGENTS.md) for the review/merge contract,
[development](docs/development.md) for local commands and
[evidence requirements](docs/concepts/evidence.md) for scientific claims.

Before a PR:

```bash
python -m pytest -q
python -m ruff check src tests tools
python -m tools.check_docs
```

For MkDocs changes also run `python -m mkdocs build --strict --clean`.
Do not commit generated reports, model weights, dataset files without
redistribution rights, secrets or physical measurements inferred from
simulation. Never execute untrusted PR code on a persistent self-hosted runner
or enable paid APIs.
