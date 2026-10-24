# Contributing

Keep the project hardware/vendor/partner neutral. Use short, reviewable changes, typed Python and deterministic tests. Run `pytest -q` and `ruff check src tests tools` locally. Never commit datasets with uncertain redistribution rights, trained weights, secrets, physical measurement claims inferred from simulations, or generated `reports/` contents. Use conventional commits (e.g. `feat:`, `test:`, `docs:`). Keep PRs Draft pending code review and reproducible test evidence. Never enable paid-hosted Actions or run untrusted external code on self-hosted runners. New algorithms must state units, interpolation policy, random seeds, provenance and modality assumptions.

## Documentation maintenance

Documentation pages live in `docs/` with navigation in `mkdocs.yml`.
Update the corresponding guide, CLI table, data contract and evidence boundary
whenever an algorithm or experiment is introduced or changed.

```bash
python -m pip install -e '.[dev,docs]'
python -m tools.check_docs
python -m pytest -q tests/test_docs.py
python -m mkdocs build --strict --clean
```

The docs workflow is only manually dispatched to an approved self-hosted runner;
do not execute untrusted PR contributions on it, and do not publish the
site or upload source data without explicit review.
