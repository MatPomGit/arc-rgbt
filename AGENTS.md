# Agent operating contract

## Scope and safety
- Vendor-independent open research code only. Do not mention or infer any industrial partner, product, contact or confidential project.
- No paid APIs. Do not download datasets or models.
- Never commit reports, weights, secrets, user data or local paths.
- Implement functionality, not empty directories or stubs.
- Tie every benchmark claim to labelled evidence with explicit provenance.
- Keep it simple (KISS): no speculative abstractions, no duplicate implementations, docs or configs. Prefer editing existing files over creating new ones.
- Small commits. Report concrete failures; do not hide or soften them.

## Pipeline
- Follow the [shared delivery pipeline](https://github.com/MatPomGit/research-autopilot/blob/41ddb950a363df2ef78850ac9766c130880b2fd9/docs/architecture/DELIVERY_PIPELINE.md). Research Autopilot is the sole controller.
- Act autonomously within existing user authorization. Do not ask again for authorization already given.

## Finish before starting
- Before any feature, read the full current PR inventory and existing task ownership.
- Finish the repository's existing PR first; reuse its branch for repairs.
- Limits: one active PR per repository, five across the managed portfolio. Drafts, testing, review and repair all count as active. A blocked PR does not free a slot.
- Priority order:
  1. Security and dependency blockers
  2. Repairs
  3. Validation and review
  4. Authorized merge and branch cleanup
  5. New features
- No separate report-only PR per validation run.

## Validation
- Use reusable validators from a trusted controller revision.
- One bounded batch per host, isolated execution, exact source SHAs, separate result per check.
- Statuses: PASS, FAIL, BLOCKED, UNAVAILABLE, NOT_RUN. Only PASS is a pass.
- Syntax checks do not establish scientific validity or teaching-material correctness.

## Merge and cleanup
- Merge when all applicable checks, reviews and current GitHub rules pass, within existing authorization.
- Delete a branch only if it is confirmed merged and owned, its current SHA is verified, and no dependent PR needs it.
- Merge does not authorize deployment or publication.

## Blocked work
- Record: reason, required exit condition, next safe action.
- Continue unrelated authorized repairs. Do not start another feature in the blocked repository.

## Reporting
- Report: completed merges, remaining PR age, blockers, and what was actually verified (and what was not).
- PR creation count is not a progress metric.

## Documentation ownership
- Keep `README.md` as entry/navigation; `docs/` owns technical methods and CLI contracts.
- Keep publication-specific preregistration rules only under `publications/P*/protocol/`; `AUTOPILOT_PLAN.md` owns work packages and `PROJECT_STATE.yaml` machine status.
- Link to canonical material rather than repeating methods, flags, formulas or scientific claims.
- Keep editable Markdown, not generated HTML/build assets. Each MkDocs page must be in `mkdocs.yml` and pass the documentation checks.
