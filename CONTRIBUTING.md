# Contributing

Keep the project hardware/vendor/partner neutral. Use short, reviewable changes, typed Python and deterministic tests. Run `pytest -q` and `ruff check src tests tools` locally. Never commit datasets with uncertain redistribution rights, trained weights, secrets, physical measurement claims inferred from simulations, or generated `reports/` contents. Use conventional commits (e.g. `feat:`, `test:`, `docs:`). Keep PRs Draft pending code review and reproducible test evidence. Never enable paid-hosted Actions or run untrusted external code on self-hosted runners. New algorithms must state units, interpolation policy, random seeds, provenance and modality assumptions.

## Documentation

Keep pages in `docs/` consistent with current CLI behaviour. Update `mkdocs.yml`
navigation and run `python -m tools.check_docs`, followed by
`python -m mkdocs build --strict` with the local `docs` extra installed.
A documentation change must not present reference or simulated output as empirical
sensor or microcontroller validation. Site publication requires separate approval.
